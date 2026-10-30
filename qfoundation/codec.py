import hashlib, json, inspect

def canonical(value):
    # Project canonical JSON, not RFC 8785. Versioned serialization contract.
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha256(value): return hashlib.sha256(value).hexdigest()
def json_hash(value): return sha256(canonical(value).encode('utf-8'))
def code_hash(component): return sha256(inspect.getsource(type(component)).encode('utf-8'))
