import argparse, json
from pathlib import Path
from .store import Store

def main():
    p=argparse.ArgumentParser(description='Phase 2A offline database infrastructure')
    p.add_argument('command',choices=['init','inspect'])
    p.add_argument('--db',default='data/foundation.sqlite3')
    a=p.parse_args(); path=Path(a.db)
    if a.command=='inspect' and not path.exists(): p.error('Database does not exist')
    if a.command=='init': path.parent.mkdir(parents=True,exist_ok=True)
    store=Store(path)
    try:
        tables=[r[0] for r in store.db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        print(json.dumps({'database':str(path),'phase1':'LIVE_VALIDATION_PENDING','phase2a':'COMPLETE','tables':tables,'integrity_check':store.db.execute('PRAGMA integrity_check').fetchone()[0]},indent=2))
    finally: store.close()
if __name__=='__main__': main()
