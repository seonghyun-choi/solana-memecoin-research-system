from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from .codec import code_hash

@dataclass(frozen=True)
class ParseResult:
    status: str
    mapping_status: str = 'UNCONFIRMED'
    market: dict | None = None
    social: dict | None = None
    field_status: dict = field(default_factory=dict)
    error_code: str | None = None

class ProviderAdapter(ABC):
    """Offline parser interface. No HTTP methods, endpoints, key or wallet access."""
    provider: str
    schema_status: str = 'UNCONFIRMED'
    @abstractmethod
    def parse(self,payload: bytes,metadata: dict) -> ParseResult: ...

class RugCheckAdapter(ProviderAdapter):
    provider='rugcheck'
    def parse(self,payload,metadata):
        return ParseResult('UNCONFIRMED',field_status={k:'UNCONFIRMED' for k in ('score_normalised','risks','mintAuthority','freezeAuthority','lpLockedPct','topHolders','creator_information','insider_information')})
class DexScreenerAdapter(ProviderAdapter):
    provider='dexscreener'
    def parse(self,payload,metadata):
        return ParseResult('UNCONFIRMED',field_status={k:'UNCONFIRMED' for k in ('priceUsd','liquidity.usd','pairCreatedAt','txns','volume','fdv','marketCap','baseToken','quoteToken','dexId')})
class JupiterAdapter(ProviderAdapter):
    provider='jupiter'
    def parse(self,payload,metadata):
        return ParseResult('UNCONFIRMED',field_status={k:'UNCONFIRMED' for k in ('inputMint','outputMint','inAmount','outAmount','inUsdValue','outUsdValue','priceImpact','priceImpactPct','otherAmountThreshold','slippageBps','routePlan','router','feeBps','requestId','quoteId','expireAt','totalTime')})
class XAIAdapter(ProviderAdapter):
    provider='xai'
    def parse(self,payload,metadata):
        return ParseResult('UNCONFIRMED',field_status={k:'UNCONFIRMED' for k in ('structured_output','x_search_calls','x_posts_fetched','x_users_fetched')})

class ParserRegistry:
    def __init__(self): self._items={}
    def register(self,parser_version_id,adapter):
        if parser_version_id in self._items: raise ValueError('Parser already registered')
        self._items[parser_version_id]=adapter
    def resolve(self,row):
        adapter=self._items.get(row['id'])
        if adapter is None: raise ValueError('Exact archived parser implementation not registered')
        if code_hash(adapter)!=row['code_sha256'] or adapter.provider!=row['provider'] or adapter.schema_status!=row['schema_status']:
            raise ValueError('Registered parser does not match immutable version')
        return adapter
