import json, re, uuid, sys, sqlite3
from pathlib import Path
from contextlib import contextmanager
from urllib.parse import urlsplit, parse_qsl
from .db import connect, migrate
from .codec import canonical, sha256, json_hash, code_hash
from .time_model import utc_us, clock
from .errors import IdempotencyConflict, IntegrityViolation, PartitionConflict, VersionConflict, classify_error
PARTITIONS={'RESEARCH','VALIDATION','FINAL_OOS'}
PROVIDERS={'rugcheck','dexscreener','jupiter','xai','synthetic'}
HORIZONS=(600,1800,3600,10800,21600,43200,86400)
ALPHABET='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def uid(): return str(uuid.uuid4())
def foundation_fingerprint():
    root=Path(__file__).parent
    source={str(p.relative_to(root)):sha256(p.read_bytes()) for p in sorted(root.rglob('*')) if p.suffix in ('.py','.sql')}
    return json_hash({'source':source,'python':sys.version.split()[0],'sqlite':sqlite3.sqlite_version,'serialization':'q-json-v1'})

def validate_mint(mint):
    if not isinstance(mint,str) or not 32<=len(mint)<=44: raise ValueError('Expected Solana mint public address')
    n=0
    for c in mint:
        if c not in ALPHABET: raise ValueError('Invalid base58 mint')
        n=n*58+ALPHABET.index(c)
    size=(n.bit_length()+7)//8+len(mint)-len(mint.lstrip('1'))
    if size!=32: raise ValueError('Mint must decode to 32 bytes')
    return mint  # Case-sensitive; never lowercase a Solana address.

def public_endpoint(endpoint):
    u=urlsplit(endpoint)
    if u.scheme!='https' or not u.hostname or u.username or u.password or u.fragment:
        raise ValueError('Credential-free HTTPS endpoint required')
    if any(re.search('key|token|secret|auth|signature|password',k,re.I) for k,_ in parse_qsl(u.query)):
        raise ValueError('Sensitive query parameters prohibited')
    return endpoint

class Store:
    def __init__(self,path,initialize=True):
        self.db=connect(path)
        if initialize: migrate(self.db)
    def close(self): self.db.close()
    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield; self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK'); raise
    def _once(self,scope,key,request,create):
        if not isinstance(key,str) or not key: raise ValueError('Stable nonempty idempotency key required')
        h=json_hash(request)
        with self.transaction():
            row=self.db.execute('SELECT * FROM idempotency_keys WHERE scope=? AND key=?',(scope,key)).fetchone()
            if row:
                if row['request_sha256']!=h: raise IdempotencyConflict('Key reused with different request')
                return row['result_id']
            result=create()
            self.db.execute('INSERT INTO idempotency_keys VALUES (?,?,?,?,?)',(scope,key,h,result,clock()))
            return result
    def _candidate(self,mint,partition):
        validate_mint(mint)
        if partition not in PARTITIONS: raise ValueError('Unknown partition')
        row=self.db.execute('SELECT * FROM candidates WHERE chain=? AND mint=?',('solana',mint)).fetchone()
        if row:
            if row['partition_id']!=partition: raise PartitionConflict('Candidate already belongs to another partition')
            return row['id']
        id=uid(); self.db.execute('INSERT INTO candidates VALUES (?,?,?,?,?)',(id,'solana',mint,partition,clock())); return id
    def candidate(self,mint,partition='RESEARCH'):
        with self.transaction(): return self._candidate(mint,partition)
    def discover(self,mint,source,event_key,occurred_at,partition='RESEARCH',metadata=None):
        if not source or not event_key: raise ValueError('Source and stable event key required')
        request={'mint':validate_mint(mint),'source':source,'event_key':event_key,'occurred_at_us':utc_us(occurred_at),'partition':partition,'metadata':metadata or {}}
        def create():
            c=self._candidate(mint,partition); id=uid()
            self.db.execute('INSERT INTO candidate_discoveries VALUES (?,?,?,?,?,?,?,?,?)',(id,c,partition,source,event_key,request['occurred_at_us'],clock(),canonical(request['metadata']),json_hash(request)))
            return id
        return self._once('discovery',json_hash([mint,source,event_key]),request,create)
    def candidate_row(self,id):
        row=self.db.execute('SELECT * FROM candidates WHERE id=?',(id,)).fetchone()
        if row is None: raise ValueError('Unknown candidate')
        return row
    def capture(self,candidate_id,provider,endpoint,payload,captured_at,idempotency_key,*,http_status=None,provenance='imported_unverified',content_type='application/json',metadata=None,secrets=()):
        if provider not in PROVIDERS: raise ValueError('Unknown provider')
        if not isinstance(payload,bytes): raise TypeError('Original bytes required; do not reserialize raw JSON')
        public_endpoint(endpoint)
        if http_status is not None and (type(http_status) is not int or not 100<=http_status<=599): raise ValueError('Invalid HTTP status')
        if provenance=='live_capture' and http_status is None: raise ValueError('Live capture requires HTTP status')
        md=metadata or {}
        # No request/authorization headers accepted. Metadata limited to transport facts.
        if set(md)-{'server_schema_version','request_id','response_date','content_encoding','note'}:
            raise ValueError('Metadata outside transport allowlist')
        for secret in secrets:
            if not isinstance(secret,bytes) or not secret: raise ValueError('Nonempty secret bytes required')
            if secret in payload or secret in (endpoint+canonical(md)).encode(): raise ValueError('Secret detected; capture refused')
        c=self.candidate_row(candidate_id)
        req=dict(candidate_id=candidate_id,partition_id=c['partition_id'],provider=provider,endpoint=endpoint,payload_sha256=sha256(payload),captured_at_us=utc_us(captured_at),http_status=http_status,provenance=provenance,content_type=content_type,metadata=md)
        def create():
            id=uid()
            self.db.execute('INSERT INTO raw_api_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(id,candidate_id,c['partition_id'],provider,endpoint,req['captured_at_us'],clock(),http_status,provenance,content_type,payload,req['payload_sha256'],len(payload),canonical(md)))
            return id
        return self._once('capture:'+provider,idempotency_key,req,create)
    def snapshot(self,id):
        row=self.db.execute('SELECT * FROM raw_api_snapshots WHERE id=?',(id,)).fetchone()
        if row is None: raise ValueError('Unknown snapshot')
        if sha256(row['payload'])!=row['payload_sha256'] or len(row['payload'])!=row['byte_length']: raise IntegrityViolation('Raw payload integrity failure')
        return row
    def config(self,name,version,content):
        text=canonical(content); h=sha256(text.encode())
        with self.transaction():
            row=self.db.execute('SELECT * FROM config_versions WHERE name=? AND version=?',(name,version)).fetchone()
            if row:
                if row['content_sha256']!=h: raise VersionConflict('Config version is immutable')
                return row['id']
            id=uid(); self.db.execute('INSERT INTO config_versions VALUES (?,?,?,?,?,?)',(id,name,version,text,h,clock())); return id
    def parser(self,adapter,version):
        provider=adapter.provider; status=adapter.schema_status; h=code_hash(adapter)
        if provider not in PROVIDERS: raise ValueError('Unknown provider')
        if provider!='synthetic' and status!='UNCONFIRMED': raise ValueError('Phase 1 mappings not approved')
        if provider=='synthetic' and status!='SYNTHETIC': raise ValueError('Synthetic parser required')
        with self.transaction():
            row=self.db.execute('SELECT * FROM parser_versions WHERE provider=? AND name=? AND version=?',(provider,type(adapter).__name__,version)).fetchone()
            if row:
                if row['code_sha256']!=h or row['schema_status']!=status: raise VersionConflict('Parser version code mismatch')
                return row['id']
            id=uid(); self.db.execute('INSERT INTO parser_versions VALUES (?,?,?,?,?,?,?)',(id,provider,type(adapter).__name__,version,h,status,clock())); return id
    def pipeline(self,name,version,parser_id,shadow_filter,extra=None):
        content={'parser_version_id':parser_id,'filter_code_sha256':code_hash(shadow_filter),'foundation_fingerprint':foundation_fingerprint(),'mode':'SHADOW','extra':extra or {}}
        text=canonical(content); h=sha256(text.encode())
        with self.transaction():
            row=self.db.execute('SELECT * FROM pipeline_versions WHERE name=? AND version=?',(name,version)).fetchone()
            if row:
                if row['content_sha256']!=h: raise VersionConflict('Pipeline version is immutable')
                return row['id']
            id=uid(); self.db.execute('INSERT INTO pipeline_versions VALUES (?,?,?,?,?,?,?)',(id,name,version,parser_id,text,h,clock())); return id
    def api_event(self,provider,occurred_at,event_key,*,candidate_id=None,partition='RESEARCH',snapshot_id=None,http_status=None,transport=None,explicit_no_route=False,details=None):
        error=classify_error(http_status,transport,explicit_no_route)
        if candidate_id is not None: partition=self.candidate_row(candidate_id)['partition_id']
        req=dict(provider=provider,occurred_at_us=utc_us(occurred_at),candidate_id=candidate_id,partition=partition,snapshot_id=snapshot_id,http_status=http_status,error=error.code.value,retryable=error.retryable,details=details or {})
        def create():
            id=uid(); self.db.execute('INSERT INTO api_events VALUES (?,?,?,?,?,?,?,?,?,?)',(id,candidate_id,partition,provider,snapshot_id,req['occurred_at_us'],http_status,error.code.value,int(error.retryable),canonical(req['details']))); return id
        return self._once('api_event:'+provider,event_key,req,create)
    def plan_forwards(self,decision_id):
        """Explicit offline infrastructure call only. No scheduler or API calls."""
        with self.transaction():
            d=self.db.execute('SELECT * FROM decisions WHERE id=?',(decision_id,)).fetchone()
            if d is None: raise ValueError('Unknown decision')
            ids=[]
            for h in HORIZONS:
                row=self.db.execute("SELECT id FROM forward_observations WHERE decision_id=? AND horizon_seconds=? AND event_key='plan'",(decision_id,h)).fetchone()
                if row: ids.append(row['id']); continue
                id=uid(); due=d['created_at_us']+h*1000000
                self.db.execute('INSERT INTO forward_observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(id,decision_id,d['candidate_id'],d['partition_id'],h,due,None,'PLANNED',None,'{}','plan',json_hash([decision_id,h])))
                ids.append(id)
            return ids
    def record_forward(self,decision_id,horizon,recorded_at,event_key,*,snapshot_id=None,data=None,missing=False):
        if horizon not in HORIZONS or event_key=='plan': raise ValueError('Invalid horizon/event key')
        d=self.db.execute('SELECT * FROM decisions WHERE id=?',(decision_id,)).fetchone()
        if d is None: raise ValueError('Unknown decision')
        req=dict(decision_id=decision_id,horizon=horizon,recorded_at_us=utc_us(recorded_at),snapshot_id=snapshot_id,data=data or {},missing=missing)
        def create():
            id=uid(); self.db.execute('INSERT INTO forward_observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(id,decision_id,d['candidate_id'],d['partition_id'],horizon,d['created_at_us']+horizon*1000000,req['recorded_at_us'],'MISSING' if missing else 'RECORDED',snapshot_id,canonical(req['data']),event_key,json_hash(req))); return id
        return self._once('forward:'+decision_id+':'+str(horizon),event_key,req,create)
    def backup(self,destination):
        """SQLite online backup; includes WAL-visible committed rows."""
        out=sqlite3.connect(str(destination))
        try: self.db.backup(out)
        finally: out.close()
