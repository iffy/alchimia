from alchimia.strategy import TwistedEngineStrategy, TWISTED_STRATEGY
from alchimia.strategy import AsyncEngineStrategy, ASYNC_STRATEGY
from alchimia.dialect import register

__all__ = [
    "TWISTED_STRATEGY", "ASYNC_STRATEGY"
]

TwistedEngineStrategy()
AsyncEngineStrategy()
register()