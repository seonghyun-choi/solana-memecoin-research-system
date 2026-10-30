import sqlite3
from pathlib import Path
from .codec import sha256
from .time_model import clock
from .errors import IntegrityViolation
MIGRATIONS=Path(__file__).with_name('migrations')

def connect(path):
    db=sqlite3.connect(str(path),isolation_level=None,timeout=15)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA recursive_triggers=ON')
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('PRAGMA busy_timeout=15000')
    return db

def statements(script):
    buf=''
    for line in script.splitlines(True):
        buf+=line
        if sqlite3.complete_statement(buf):
            yield buf; buf=''
    if buf.strip(): raise ValueError('Incomplete migration statement')

def migrate(db,target=None,directory=MIGRATIONS):
    db.execute('BEGIN IMMEDIATE')
    try:
        db.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, filename TEXT NOT NULL, sha256 TEXT NOT NULL, applied_at_us INTEGER NOT NULL)')
        files={int(p.name.split('_')[0]):p for p in sorted(Path(directory).glob('*.sql'))}
        for row in db.execute('SELECT * FROM schema_migrations'):
            p=files.get(row['version'])
            if p is None or sha256(p.read_bytes())!=row['sha256']: raise IntegrityViolation('Migration history checksum mismatch')
        current=db.execute('SELECT COALESCE(MAX(version),0) FROM schema_migrations').fetchone()[0]
        if target is not None and (target<current or target not in files): raise ValueError('Downgrades or unknown migration targets prohibited')
        for version,p in sorted(files.items()):
            if target is not None and version>target: continue
            if db.execute('SELECT 1 FROM schema_migrations WHERE version=?',(version,)).fetchone(): continue
            for statement in statements(p.read_text(encoding='utf-8')): db.execute(statement)
            db.execute('INSERT INTO schema_migrations VALUES (?,?,?,?)',(version,p.name,sha256(p.read_bytes()),clock()))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK'); raise
