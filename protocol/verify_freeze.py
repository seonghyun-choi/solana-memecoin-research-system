"""Read-only protocol artifact verification. Never enables collection."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def verify(root=ROOT):
    registry=root/'protocol/REGISTRY.jsonl'
    previous=None;versions=set();records=[]
    for line in registry.read_text(encoding='utf-8').splitlines():
        row=json.loads(line);claimed=row.pop('record_sha256')
        if digest(canonical(row))!=claimed:raise ValueError('Registry record hash mismatch')
        if row['previous_record_sha256']!=previous:raise ValueError('Registry chain mismatch')
        if row['version'] in versions:raise ValueError('Duplicate protocol version')
        versions.add(row['version']);previous=claimed
        for path,h in row['artifacts'].items():
            if digest((root/path).read_bytes())!=h:raise ValueError('Frozen artifact mismatch: '+path)
        records.append(row)
    if not records:raise ValueError('Empty registry')
    latest=records[-1]
    for root_path,frozen_path in latest['current_mirrors'].items():
        if (root/root_path).read_bytes()!=(root/frozen_path).read_bytes():raise ValueError('Current document differs from registered version')
    manifest=json.loads((root/'protocol/templates/activation_manifest.template.json').read_text())
    unresolved=[k for k,v in manifest['required_before_activation'].items() if v is None]
    # A template is never an approved operational activation, even if edited with values.
    return {'freeze_integrity':'PASS','version':latest['version'],'registered_at_utc':latest['registered_at_utc'],
            'activation_status':'BLOCKED','reason':'Template only; approved activation record required',
            'unresolved_items':unresolved,'phase1':'LIVE_VALIDATION_PENDING','phase2b':'NOT STARTED'}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
