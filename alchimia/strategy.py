from sqlalchemy.engine.strategies import DefaultEngineStrategy, EngineStrategy
from sqlalchemy.engine import url

from alchimia.engine import TwistedEngine, AsyncEngine


TWISTED_STRATEGY = "_twisted"


class TwistedEngineStrategy(DefaultEngineStrategy):
    """
    An EngineStrategy for use with Twisted. Many of the Engine's methods will
    return Deferreds instead of results. See the documentation of
    ``TwistedEngine`` for more details.
    """

    name = TWISTED_STRATEGY
    engine_cls = TwistedEngine



ASYNC_STRATEGY = "_txpostgres"


class AsyncEngineStrategy(EngineStrategy):
    """
    An EngineStrategy for use with Twisted and Deferred-returning Dialects.
    See the documentation of ``AsyncEngine`` for more details.
    """

    name = ASYNC_STRATEGY

    def create(self, name_or_url, reactor, **kwargs):
        u = url.make_url(name_or_url)
        
        if str(u).count('txpostgres'):
            from alchimia.dialect import TxPostgresDialect, TxPostgresPool
            dialect = TxPostgresDialect()
            connstr = dialect.url_to_connstr(u)
            pool = TxPostgresPool(connstr)


        return AsyncEngine(pool, dialect, u, reactor, **kwargs)
