"""Canonical time = signed integer microseconds since UTC Unix epoch."""
from datetime import datetime, timezone, timedelta
EPOCH = datetime(1970,1,1,tzinfo=timezone.utc)

def utc_us(value):
    if isinstance(value,str):
        value=datetime.fromisoformat(value.replace('Z','+00:00'))
    if not isinstance(value,datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('Timezone-aware datetime or ISO-8601 offset required')
    delta=value.astimezone(timezone.utc)-EPOCH
    return delta.days*86400000000+delta.seconds*1000000+delta.microseconds

def iso_utc(value):
    if type(value) is not int: raise TypeError('Integer UTC microseconds required')
    return (EPOCH+timedelta(microseconds=value)).isoformat(timespec='microseconds').replace('+00:00','Z')

def clock(): return utc_us(datetime.now(timezone.utc))
