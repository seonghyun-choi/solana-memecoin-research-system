import json
from dataclasses import dataclass, field
from .adapters import ParseResult
from .codec import canonical, sha256, code_hash
from .store import uid, foundation_fingerprint
from .time_model import clock
from .errors import IntegrityViolation

@dataclass(frozen=True)
class ShadowResult:
    outcome: str
    details: dict = field(default_factory=dict)

class UnconfirmedShadowFilter:
    def evaluate(self,parsed,config):
        return ShadowResult('UNCONFIRMED',{'reason':'Provider mapping not confirmed; no inferred score or trading decision'})

class ReplayEngine:
    def __init__(self,store,registry): self.store,self.registry=store,registry
    def run(self,snapshot_id,parser_id,config_id,pipeline_id,shadow_filter=None):
        shadow_filter=shadow_filter or UnconfirmedShadowFilter()
        s=self.store; db=s.db
        with s.transaction():
            raw=s.snapshot(snapshot_id)
            parser=db.execute('SELECT * FROM parser_versions WHERE id=?',(parser_id,)).fetchone()
            cfg=db.execute('SELECT * FROM config_versions WHERE id=?',(config_id,)).fetchone()
            pipe=db.execute('SELECT * FROM pipeline_versions WHERE id=?',(pipeline_id,)).fetchone()
            if parser is None or cfg is None or pipe is None: raise ValueError('Unknown immutable version')
            if pipe['parser_version_id']!=parser_id or raw['provider']!=parser['provider']: raise IntegrityViolation('Provider/parser/pipeline mismatch')
            if sha256(cfg['content_json'].encode())!=cfg['content_sha256'] or sha256(pipe['manifest_json'].encode())!=pipe['content_sha256']: raise IntegrityViolation('Version content integrity failure')
            manifest=json.loads(pipe['manifest_json'])
            if manifest['filter_code_sha256']!=code_hash(shadow_filter) or manifest['foundation_fingerprint']!=foundation_fingerprint(): raise IntegrityViolation('Pipeline implementation/runtime fingerprint mismatch')
            adapter=self.registry.resolve(parser)
            existing=db.execute('SELECT id FROM replay_runs WHERE snapshot_id=? AND parser_version_id=? AND config_version_id=? AND pipeline_version_id=?',(snapshot_id,parser_id,config_id,pipeline_id)).fetchone()
            if existing: return existing['id']
            # Both inputs come from stored evidence; no provider fetch or fallback exists.
            try: parsed=adapter.parse(raw['payload'],dict(raw))
            except Exception:
                parsed=ParseResult('PARSE_ERROR',error_code='PARSE_ERROR')
            if not isinstance(parsed,ParseResult) or parsed.status not in ('UNCONFIRMED','PARSED','PARSE_ERROR'): raise ValueError('Invalid parser contract')
            if raw['provider']!='synthetic' and (parsed.status=='PARSED' or parsed.market is not None or parsed.social is not None): raise IntegrityViolation('Phase 1 field mappings remain unapproved')
            if parsed.status!='PARSED' and (parsed.market is not None or parsed.social is not None): raise IntegrityViolation('Unconfirmed/error output cannot produce normalized observations')
            if parsed.status=='PARSED' and parsed.mapping_status not in ('CONFIRMED','SYNTHETIC'): raise IntegrityViolation('Parsed output requires explicit mapping provenance')
            if raw['provider']=='synthetic' and (raw['provenance']!='synthetic' or parsed.mapping_status not in ('SYNTHETIC','UNCONFIRMED')): raise IntegrityViolation('Synthetic evidence must remain synthetic')
            result=shadow_filter.evaluate(parsed,json.loads(cfg['content_json'])) if parsed.status=='PARSED' else ShadowResult('UNCONFIRMED',{'reason':parsed.status})
            if not isinstance(result,ShadowResult) or result.outcome not in ('PASS','FAIL','SKIP','UNCONFIRMED'): raise ValueError('Invalid shadow filter output')
            run=uid(); timestamp=clock(); candidate=raw['candidate_id']; partition=raw['partition_id']
            details={'field_status':parsed.field_status,'error_code':parsed.error_code,'snapshot_sha256':raw['payload_sha256']}
            db.execute('INSERT INTO replay_runs VALUES (?,?,?,?,?,?,?,?,?,?)',(run,snapshot_id,candidate,partition,parser_id,config_id,pipeline_id,timestamp,parsed.status,canonical(details)))
            for table,body in (('market_observations',parsed.market),('social_observations',parsed.social)):
                if body is not None:
                    if not isinstance(body,dict): raise ValueError('Observation must be an object')
                    db.execute(f'INSERT INTO {table} VALUES (?,?,?,?,?,?,?)',(uid(),run,candidate,partition,raw['captured_at_us'],parsed.mapping_status,canonical(body)))
            filter_id=uid()
            db.execute('INSERT INTO filter_results VALUES (?,?,?,?,?,?,?,?,?)',(filter_id,run,candidate,partition,result.outcome,'SHADOW','CONTINUE',canonical(result.details),timestamp))
            db.execute('INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?)',(uid(),filter_id,candidate,partition,'PASS' if result.outcome=='PASS' else 'SKIP','RESEARCH_SHADOW','CONTINUE',timestamp))
            return run
