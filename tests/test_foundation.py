import json, sqlite3, tempfile, unittest, hashlib, socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from qfoundation import Store, ReplayEngine
from qfoundation.db import connect,migrate,MIGRATIONS
from qfoundation.adapters import (ProviderAdapter,ParseResult,ParserRegistry,RugCheckAdapter,DexScreenerAdapter,JupiterAdapter,XAIAdapter)
from qfoundation.replay import ShadowResult,UnconfirmedShadowFilter
from qfoundation.codec import sha256
from qfoundation.time_model import utc_us,iso_utc
from qfoundation.errors import *
from qfoundation.store import HORIZONS
SOL='So11111111111111111111111111111111111111112'
USDC='EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
T='2026-10-28T14:01:00+09:00'

class SyntheticParser(ProviderAdapter):
    provider='synthetic'; schema_status='SYNTHETIC'
    def parse(self,payload,metadata):
        return ParseResult('PARSED','SYNTHETIC',market=json.loads(payload))
class SyntheticParserV2(ProviderAdapter):
    provider='synthetic'; schema_status='SYNTHETIC'
    def parse(self,payload,metadata):
        body=json.loads(payload); body['parser_revision']=2
        return ParseResult('PARSED','SYNTHETIC',market=body,social={'fixture_only':True})
class BrokenParser(ProviderAdapter):
    provider='synthetic'; schema_status='SYNTHETIC'
    def parse(self,payload,metadata): raise ValueError('synthetic parser failure')
class ThresholdShadow:
    def evaluate(self,parsed,config):
        # Synthetic test only, NOT a provider field mapping or optimized threshold.
        score=parsed.market['risk_score']; threshold=config['threshold']
        return ShadowResult('PASS' if score<=threshold else 'FAIL',{'score':score,'threshold':threshold})
class BrokenFilter:
    def evaluate(self,parsed,config): raise RuntimeError('test rollback')

class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'test.sqlite3'; self.s=Store(self.path)
    def tearDown(self): self.s.close(); self.tmp.cleanup()
    def count(self,table): return self.s.db.execute('SELECT count(*) FROM '+table).fetchone()[0]
    def capture(self,provider='synthetic',key='capture',payload=b'{"risk_score":55}'):
        c=self.s.candidate(SOL)
        return self.s.capture(c,provider,'https://example.test/report',payload,T,key,provenance='synthetic')
    def setup_replay(self,adapter=None,filter=None,config=None,version='1'):
        adapter=adapter or SyntheticParser(); filter=filter or ThresholdShadow()
        parser=self.s.parser(adapter,version); cfg=self.s.config('test',version,config or {'threshold':40}); pipeline=self.s.pipeline('test',version,parser,filter)
        registry=ParserRegistry(); registry.register(parser,adapter)
        return ReplayEngine(self.s,registry),parser,cfg,pipeline,filter
    def run_replay(self,**kwargs):
        raw=self.capture(); e,p,c,v,f=self.setup_replay(**kwargs)
        return e.run(raw,p,c,v,f),raw,(e,p,c,v,f)
    def test_database_creation_and_foreign_keys(self):
        expected={'candidates','candidate_discoveries','raw_api_snapshots','market_observations','filter_results','social_observations','decisions','forward_observations','api_events','config_versions','pipeline_versions','parser_versions','partitions','replay_runs','idempotency_keys','schema_migrations'}
        self.assertEqual(expected,{r[0] for r in self.s.db.execute("SELECT name FROM sqlite_master WHERE type='table'")})
        self.assertEqual(self.s.db.execute('PRAGMA foreign_keys').fetchone()[0],1)
        self.assertEqual(self.s.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    def test_migration_upgrade_and_rerun(self):
        db=connect(Path(self.tmp.name)/'old.sqlite3')
        try:
            migrate(db,target=1); self.assertEqual(db.execute('SELECT count(*) FROM schema_migrations').fetchone()[0],1)
            db.execute('INSERT INTO candidates VALUES (?,?,?,?,?)',('legacy','solana',SOL,'RESEARCH',0))
            migrate(db); migrate(db)
            self.assertEqual(db.execute('SELECT count(*) FROM schema_migrations').fetchone()[0],2)
            self.assertEqual(db.execute('SELECT id FROM candidates').fetchone()[0],'legacy')
        finally: db.close()
    def test_migration_tamper_detected(self):
        directory=Path(self.tmp.name)/'migrations'; directory.mkdir()
        for p in MIGRATIONS.glob('*.sql'): (directory/p.name).write_bytes(p.read_bytes())
        with (directory/'001_foundation.sql').open('a') as f:f.write('\n-- tampered\n')
        with self.assertRaises(IntegrityViolation): migrate(self.s.db,directory=directory)
    def test_failed_migration_atomic_rollback(self):
        directory=Path(self.tmp.name)/'broken';directory.mkdir()
        (directory/'001_bad.sql').write_text('CREATE TABLE temporary_table(id INTEGER);\nINVALID SQL;\n')
        db=connect(Path(self.tmp.name)/'broken.sqlite3')
        try:
            with self.assertRaises(sqlite3.OperationalError):migrate(db,directory=directory)
            self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='temporary_table'").fetchone())
        finally: db.close()
    def test_candidate_deduplication(self):
        self.assertEqual(self.s.candidate(SOL),self.s.candidate(SOL)); self.assertEqual(self.count('candidates'),1)
    def test_multiple_discovery_events(self):
        for src,t in [('Pump.fun','14:01'),('X','14:05'),('DexScreener','14:11')]: self.s.discover(SOL,src,'event-1',f'2026-10-28T{t}:00+09:00')
        self.assertEqual(self.count('candidates'),1);self.assertEqual(self.count('candidate_discoveries'),3)
        row=self.s.db.execute('SELECT * FROM candidate_discovery_summary').fetchone()
        self.assertEqual(row['discovery_count'],3);self.assertEqual(row['first_seen_at_us'],utc_us(T))
    def test_same_source_multiple_events_and_out_of_order(self):
        self.s.discover(SOL,'X','late','2026-10-28T14:05:00+09:00')
        self.s.discover(SOL,'X','early',T)
        self.assertEqual(self.count('candidate_discoveries'),2)
        self.assertEqual(self.s.db.execute('SELECT first_seen_at_us FROM candidate_discovery_summary').fetchone()[0],utc_us(T))
    def test_discovery_idempotency_and_conflict(self):
        a=self.s.discover(SOL,'X','one',T);self.assertEqual(a,self.s.discover(SOL,'X','one',T))
        with self.assertRaises(IdempotencyConflict):self.s.discover(SOL,'X','one',T,metadata={'changed':True})
        self.assertEqual(self.count('candidate_discoveries'),1)
    def test_concurrent_candidate_and_discovery(self):
        def call(_):
            s=Store(self.path)
            try:return s.discover(SOL,'X','same',T)
            finally:s.close()
        with ThreadPoolExecutor(max_workers=4) as pool: result=list(pool.map(call,range(8)))
        self.assertEqual(len(set(result)),1);self.assertEqual(self.count('candidates'),1);self.assertEqual(self.count('candidate_discoveries'),1)
    def test_partition_identity_cannot_move(self):
        self.s.candidate(SOL,'RESEARCH')
        with self.assertRaises(PartitionConflict):self.s.candidate(SOL,'FINAL_OOS')
        self.assertEqual(self.s.candidate_row(self.s.candidate(USDC,'VALIDATION'))['partition_id'],'VALIDATION')
    def test_composite_fk_blocks_partition_leak(self):
        c=self.s.candidate(SOL)
        with self.assertRaises(sqlite3.IntegrityError):
            self.s.db.execute('INSERT INTO candidate_discoveries VALUES (?,?,?,?,?,?,?,?,?)',('x',c,'FINAL_OOS','X','1',0,0,'{}','a'*64))
    def test_raw_snapshot_immutable_sql(self):
        raw=self.capture()
        for statement in ('UPDATE raw_api_snapshots SET payload=? WHERE id=?','DELETE FROM raw_api_snapshots WHERE id=?'):
            with self.assertRaises(sqlite3.IntegrityError):self.s.db.execute(statement,(b'changed',raw) if statement.startswith('UPDATE') else (raw,))
        with self.assertRaises(sqlite3.IntegrityError):self.s.db.execute('UPDATE raw_api_snapshots SET endpoint=? WHERE id=?',('https://bad.test',raw))
    def test_replace_cannot_bypass_immutability(self):
        raw=self.capture(); row=self.s.snapshot(raw)
        with self.assertRaises(sqlite3.IntegrityError):self.s.db.execute('INSERT OR REPLACE INTO raw_api_snapshots VALUES ('+','.join('?'*14)+')',tuple(row))
    def test_payload_exact_bytes_hash(self):
        payload=b'{  "risk_score": 55 }\n';id=self.capture(payload=payload);r=self.s.snapshot(id)
        self.assertEqual(r['payload'],payload);self.assertEqual(r['payload_sha256'],hashlib.sha256(payload).hexdigest())
        self.assertNotEqual(r['payload_sha256'],sha256(b'{"risk_score":55}'))
    def test_snapshot_idempotency_and_new_capture(self):
        a=self.capture();self.assertEqual(a,self.capture())
        with self.assertRaises(IdempotencyConflict):self.capture(payload=b'{}')
        b=self.capture(key='new');self.assertNotEqual(a,b);self.assertEqual(self.count('raw_api_snapshots'),2)
        self.assertEqual(self.s.snapshot(a)['payload_sha256'],self.s.snapshot(b)['payload_sha256'])
    def test_hash_corruption_detected(self):
        id=self.capture();self.s.db.execute('DROP TRIGGER immutable_raw_api_snapshots_update')
        self.s.db.execute('UPDATE raw_api_snapshots SET payload=?,byte_length=? WHERE id=?',(b'{}',2,id))
        with self.assertRaises(IntegrityViolation):self.s.snapshot(id)
    def test_utc_normalization(self):
        self.assertEqual(utc_us(T),utc_us('2026-10-28T05:01:00Z'))
        self.assertEqual(iso_utc(utc_us(T)),'2026-10-28T05:01:00.000000Z')
        self.assertEqual(utc_us('1969-12-31T23:59:59.999999Z'),-1)
    def test_naive_time_rejected(self):
        for v in ('2026-10-28T14:01:00',datetime(2026,10,28),1):
            with self.assertRaises(ValueError):utc_us(v)
    def test_config_versioning_canonical_and_immutable(self):
        a=self.s.config('a','1',{'x':1,'y':2});self.assertEqual(a,self.s.config('a','1',{'y':2,'x':1}))
        with self.assertRaises(VersionConflict):self.s.config('a','1',{'x':3})
        self.assertNotEqual(a,self.s.config('a','2',{'x':3}))
        with self.assertRaises(sqlite3.IntegrityError):self.s.db.execute('DELETE FROM config_versions WHERE id=?',(a,))
        with self.assertRaises(ValueError):self.s.config('a','nan',{'x':float('nan')})
    def test_pipeline_versioning(self):
        _,p,_,v,f=self.setup_replay();self.assertEqual(v,self.s.pipeline('test','1',p,f))
        with self.assertRaises(VersionConflict):self.s.pipeline('test','1',p,f,{'changed':1})
        self.assertNotEqual(v,self.s.pipeline('test','2',p,f))
    def test_error_taxonomy(self):
        for kwargs,code in [({'transport':'DNS'},'DNS'),({'transport':'TIMEOUT'},'TIMEOUT'),({'transport':'TLS'},'TLS'),({'http_status':401},'AUTH'),({'http_status':403,'explicit_no_route':True},'AUTH'),({'http_status':429},'RATE_LIMIT'),({'http_status':500},'SERVER'),({'http_status':400},'BAD_REQUEST'),({'http_status':404},'NOT_FOUND'),({'http_status':200},'NONE'),({'http_status':400,'explicit_no_route':True},'NO_ROUTE')]:self.assertEqual(classify_error(**kwargs).code.value,code)
        self.assertFalse(classify_error(http_status=401).retryable)
    def test_api_event_and_idempotency(self):
        a=self.s.api_event('xai',T,'one',http_status=429)
        self.assertEqual(a,self.s.api_event('xai',T,'one',http_status=429))
        self.assertEqual(self.count('api_events'),1)
    def test_provider_adapters_unconfirmed_no_normalization(self):
        for cls in (RugCheckAdapter,DexScreenerAdapter,JupiterAdapter,XAIAdapter):
            adapter=cls();r=adapter.parse(b'{"looks_valid":true}',{})
            self.assertEqual(r.status,'UNCONFIRMED');self.assertIsNone(r.market);self.assertIsNone(r.social)
            self.assertTrue(all(v=='UNCONFIRMED' for v in r.field_status.values()))
    def test_real_adapter_replay_skeleton_offline(self):
        adapter=RugCheckAdapter(); raw=self.capture('rugcheck');e,p,c,v,f=self.setup_replay(adapter=adapter,filter=UnconfirmedShadowFilter())
        with patch.object(socket,'socket',side_effect=AssertionError('Network prohibited')):e.run(raw,p,c,v,f)
        self.assertEqual(self.count('market_observations'),0)
        self.assertEqual(self.s.db.execute('SELECT status FROM replay_runs').fetchone()[0],'UNCONFIRMED')
        self.assertEqual(self.s.db.execute('SELECT outcome FROM decisions').fetchone()[0],'SKIP')
    def test_replay_idempotency(self):
        run,raw,(e,p,c,v,f)=self.run_replay();self.assertEqual(run,e.run(raw,p,c,v,f))
        self.assertEqual(self.count('replay_runs'),1);self.assertEqual(self.count('market_observations'),1)
    def test_replay_new_config_preserves_old(self):
        run,raw,(e,p,c,v,f)=self.run_replay();cfg=self.s.config('test','2',{'threshold':60})
        new=e.run(raw,p,cfg,v,f);self.assertNotEqual(run,new)
        self.assertEqual([r[0] for r in self.s.db.execute('SELECT outcome FROM filter_results ORDER BY rowid')],['FAIL','PASS'])
        self.assertEqual(self.count('raw_api_snapshots'),1)
    def test_replay_new_parser_preserves_raw_and_old_result(self):
        run,raw,_=self.run_replay();e,p,c,v,f=self.setup_replay(adapter=SyntheticParserV2(),version='2')
        self.assertNotEqual(run,e.run(raw,p,c,v,f));self.assertEqual(self.count('market_observations'),2);self.assertEqual(self.count('social_observations'),1)
        self.assertEqual(self.s.snapshot(raw)['payload'],b'{"risk_score":55}')
    def test_parser_version_mismatch_rejected(self):
        raw=self.capture();e,p,c,v,f=self.setup_replay();e.registry._items[p]=SyntheticParserV2()
        with self.assertRaises(ValueError):e.run(raw,p,c,v,f)
        self.assertEqual(self.count('replay_runs'),0)
    def test_filter_failure_rolls_back(self):
        raw=self.capture();e,p,c,v,f=self.setup_replay(filter=BrokenFilter())
        with self.assertRaises(RuntimeError):e.run(raw,p,c,v,f)
        self.assertEqual(self.count('replay_runs'),0);self.assertEqual(self.count('filter_results'),0)
    def test_parser_error_saved_without_inventing_fields(self):
        self.run_replay(adapter=BrokenParser());self.assertEqual(self.s.db.execute('SELECT status FROM replay_runs').fetchone()[0],'PARSE_ERROR');self.assertEqual(self.count('market_observations'),0)
    def test_filter_fail_never_terminates_research(self):
        self.run_replay();row=self.s.db.execute('SELECT * FROM filter_results').fetchone()
        self.assertEqual(row['outcome'],'FAIL');self.assertEqual(row['research_tracking'],'CONTINUE')
        d=self.s.db.execute('SELECT * FROM decisions').fetchone();self.assertEqual(d['outcome'],'SKIP');self.assertEqual(d['research_tracking'],'CONTINUE')
    def test_forward_horizons_pass_and_skip_idempotent(self):
        _,raw,(e,p,c,v,f)=self.run_replay();cfg=self.s.config('test','2',{'threshold':60});e.run(raw,p,cfg,v,f)
        for d in self.s.db.execute('SELECT id FROM decisions').fetchall():
            a=self.s.plan_forwards(d['id']);self.assertEqual(a,self.s.plan_forwards(d['id']));self.assertEqual(len(a),7)
        self.assertEqual(self.count('forward_observations'),14)
        self.assertEqual({r[0] for r in self.s.db.execute('SELECT horizon_seconds FROM forward_observations')},set(HORIZONS))
    def test_forward_record_append_only(self):
        _,raw,_=self.run_replay();d=self.s.db.execute('SELECT id FROM decisions').fetchone()[0];self.s.plan_forwards(d)
        anchor=self.s.db.execute('SELECT created_at_us FROM decisions WHERE id=?',(d,)).fetchone()[0]
        observed=iso_utc(anchor+605000000)
        future=self.s.capture(self.s.candidate(SOL),'synthetic','https://example.test/report',b'{}',observed,'future',provenance='synthetic')
        id=self.s.record_forward(d,600,observed,'observed',snapshot_id=future,data={'synthetic':True})
        self.assertEqual(id,self.s.record_forward(d,600,observed,'observed',snapshot_id=future,data={'synthetic':True}))
        self.assertEqual(self.count('forward_observations'),8)
        with self.assertRaises(sqlite3.IntegrityError):self.s.db.execute('DELETE FROM forward_observations WHERE id=?',(id,))
    def test_no_secret_endpoint_or_known_payload(self):
        c=self.s.candidate(SOL)
        with self.assertRaises(ValueError):self.s.capture(c,'xai','https://api.test/?api_key=secret',b'{}',T,'a')
        with self.assertRaises(ValueError):self.s.capture(c,'xai','https://api.test/',b'{"secret":"abc123"}',T,'b',secrets=(b'abc123',))
        with self.assertRaises(ValueError):self.s.capture(c,'xai','https://api.test/',b'{}',T,'c',metadata={'Authorization':'Bearer abc123'})
        self.assertEqual(self.count('raw_api_snapshots'),0)
    def test_invalid_mint_rejected_no_lowercasing(self):
        with self.assertRaises(ValueError):self.s.candidate('not-a-mint')
        self.assertEqual(self.s.candidate_row(self.s.candidate(SOL))['mint'],SOL)
    def test_online_backup_preserves_raw(self):
        raw=self.capture();dest=Path(self.tmp.name)/'backup.sqlite3';self.s.backup(dest);s=Store(dest)
        try:self.assertEqual(s.snapshot(raw)['payload'],b'{"risk_score":55}')
        finally:s.close()

    def test_forward_rejects_early_event_and_stale_snapshot(self):
        _,raw,_=self.run_replay();d=self.s.db.execute('SELECT * FROM decisions').fetchone()
        with self.assertRaises(sqlite3.IntegrityError):self.s.record_forward(d['id'],600,iso_utc(d['created_at_us']),'early',snapshot_id=raw)
        with self.assertRaises(sqlite3.IntegrityError):self.s.record_forward(d['id'],600,iso_utc(d['created_at_us']+605000000),'stale',snapshot_id=raw)
        self.assertEqual(self.count('forward_observations'),0)
    def test_migration_downgrade_rejected(self):
        with self.assertRaises(ValueError):migrate(self.s.db,target=1)
    def test_api_event_snapshot_partition_mismatch_rejected(self):
        raw=self.capture();other=self.s.candidate(USDC,'VALIDATION')
        with self.assertRaises(sqlite3.IntegrityError):self.s.api_event('synthetic',T,'mismatch',candidate_id=other,snapshot_id=raw)
    def test_confirmed_provider_mapping_registration_blocked(self):
        adapter=RugCheckAdapter();adapter.schema_status='CONFIRMED'
        with self.assertRaises(ValueError):self.s.parser(adapter,'premature')
    def test_unconfirmed_parse_no_live_calls_even_with_valid_looking_body(self):
        with patch.object(socket,'socket',side_effect=AssertionError('No network')):
            for adapter in (RugCheckAdapter(),DexScreenerAdapter(),JupiterAdapter(),XAIAdapter()):
                self.assertEqual(adapter.parse(b'{"risk_score":0,"outAmount":"100"}',{}).status,'UNCONFIRMED')

if __name__=='__main__':unittest.main()
