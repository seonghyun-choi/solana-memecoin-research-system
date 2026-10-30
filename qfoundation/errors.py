from enum import Enum
from dataclasses import dataclass
class ErrorCode(str,Enum):
    NONE='NONE'; DNS='DNS'; CONNECT='CONNECT'; TIMEOUT='TIMEOUT'; TLS='TLS'
    AUTH='AUTH'; RATE_LIMIT='RATE_LIMIT'; BAD_REQUEST='BAD_REQUEST'; NOT_FOUND='NOT_FOUND'
    NO_ROUTE='NO_ROUTE'; SERVER='SERVER'; HTTP_OTHER='HTTP_OTHER'; PARSE_ERROR='PARSE_ERROR'
    SCHEMA_CHANGED='SCHEMA_CHANGED'; UNCONFIRMED='UNCONFIRMED'; UNKNOWN='UNKNOWN'
@dataclass(frozen=True)
class ApiError:
    code: ErrorCode
    retryable: bool

def classify_error(http_status=None, transport=None, explicit_no_route=False):
    """No body schema inference. explicit_no_route requires a future confirmed adapter."""
    if transport is not None:
        code=ErrorCode(transport)
        if code not in {ErrorCode.DNS,ErrorCode.CONNECT,ErrorCode.TIMEOUT,ErrorCode.TLS,ErrorCode.UNKNOWN}:
            raise ValueError('Not a transport error')
        return ApiError(code,code in {ErrorCode.DNS,ErrorCode.CONNECT,ErrorCode.TIMEOUT})
    if http_status is not None and (type(http_status) is not int or not 100<=http_status<=599): raise ValueError('Invalid HTTP status')
    if http_status in (401,403): return ApiError(ErrorCode.AUTH,False)
    if http_status==429: return ApiError(ErrorCode.RATE_LIMIT,True)
    if http_status is not None and http_status>=500: return ApiError(ErrorCode.SERVER,True)
    if explicit_no_route: return ApiError(ErrorCode.NO_ROUTE,False)
    if http_status in (400,422): return ApiError(ErrorCode.BAD_REQUEST,False)
    if http_status==404: return ApiError(ErrorCode.NOT_FOUND,False)
    if http_status is not None and 200<=http_status<300: return ApiError(ErrorCode.NONE,False)
    return ApiError(ErrorCode.UNKNOWN if http_status is None else ErrorCode.HTTP_OTHER,False)

class IdempotencyConflict(ValueError): pass
class IntegrityViolation(ValueError): pass
class PartitionConflict(ValueError): pass
class VersionConflict(ValueError): pass
