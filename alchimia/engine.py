from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.util import _distill_params
from sqlalchemy import util

from twisted.internet import defer
from twisted.internet.threads import deferToThreadPool


class TwistedEngine(object):
    def __init__(self, pool, dialect, url, reactor=None, **kwargs):
        if reactor is None:
            raise TypeError("Must provide a reactor")

        self._engine = Engine(pool, dialect, url, **kwargs)
        self._reactor = reactor

    def _defer_to_thread(self, f, *args, **kwargs):
        tpool = self._reactor.getThreadPool()
        return deferToThreadPool(self._reactor, tpool, f, *args, **kwargs)

    @property
    def dialect(self):
        return self._engine.dialect

    @property
    def _has_events(self):
        return self._engine._has_events

    @property
    def _execution_options(self):
        return self._engine._execution_options

    def _should_log_info(self):
        return self._engine._should_log_info()

    def connect(self):
        d = self._defer_to_thread(self._engine.connect)
        d.addCallback(TwistedConnection, self)
        return d

    def execute(self, *args, **kwargs):
        d = self._defer_to_thread(self._engine.execute, *args, **kwargs)
        d.addCallback(TwistedResultProxy, self)
        return d

    def has_table(self, table_name, schema=None):
        return self._defer_to_thread(
            self._engine.has_table, table_name, schema)

    def table_names(self, schema=None, connection=None):
        if connection is not None:
            connection = connection._connection
        return self._defer_to_thread(
            self._engine.table_names, schema, connection)


class TwistedConnection(object):
    def __init__(self, connection, engine):
        self._connection = connection
        self._engine = engine

    def execute(self, *args, **kwargs):
        d = self._engine._defer_to_thread(
            self._connection.execute, *args, **kwargs)
        d.addCallback(TwistedResultProxy, self._engine)
        return d

    def close(self, *args, **kwargs):
        return self._engine._defer_to_thread(
            self._connection.close, *args, **kwargs)

    @property
    def closed(self):
        return self._connection.closed

    def begin(self, *args, **kwargs):
        d = self._engine._defer_to_thread(
            self._connection.begin, *args, **kwargs)
        d.addCallback(TwistedTransaction, self._engine)
        return d

    def in_transaction(self):
        return self._connection.in_transaction()


class TwistedTransaction(object):
    def __init__(self, transaction, engine):
        self._transaction = transaction
        self._engine = engine

    def commit(self):
        return self._engine._defer_to_thread(self._transaction.commit)

    def rollback(self):
        return self._engine._defer_to_thread(self._transaction.rollback)

    def close(self):
        return self._engine._defer_to_thread(self._transaction.close)


class TwistedResultProxy(object):
    def __init__(self, result_proxy, engine):
        self._result_proxy = result_proxy
        self._engine = engine

    def fetchone(self):
        return self._engine._defer_to_thread(self._result_proxy.fetchone)

    def fetchall(self):
        return self._engine._defer_to_thread(self._result_proxy.fetchall)

    def scalar(self):
        return self._engine._defer_to_thread(self._result_proxy.scalar)

    def first(self):
        return self._engine._defer_to_thread(self._result_proxy.first)

    def keys(self):
        return self._engine._defer_to_thread(self._result_proxy.keys)

    @property
    def returns_rows(self):
        return self._result_proxy.returns_rows

    @property
    def rowcount(self):
        return self._result_proxy.rowcount


class AsyncEngine(object):
    def __init__(self, pool, dialect, url, reactor, **kwargs):
        print 'I am an engine'
        self._pool = pool
        self._dialect = dialect
        self._url = url
        self._reactor = reactor

    def _connect(self):
        return self._pool.connect()

    def execute(self, obj, *multiparams, **params):
        if isinstance(obj, util.string_types[0]):
            return self._execute_text(obj, multiparams, params)
        try:
            meth = object._execute_on_connection
        except AttributeError:
            raise exc.InvalidRequestError(
                                "Unexecutable object type: %s" %
                                type(object))
        else:
            return meth(self, multiparams, params)

    @defer.inlineCallbacks
    def _execute_text(self, statement, multiparams, params):
        """
        Execute a string 
        """
        parameters = _distill_params(multiparams, params)

        conn = yield self._connect()
        result = yield conn.runQuery(statement, parameters)
        defer.returnValue(result)

    # @property
    # def dialect(self):
    #     return self.dialect

    # @property
    # def _has_events(self):
    #     return False

    # @property
    # def _execution_options(self):
    #     return self._engine._execution_options

    # def _should_log_info(self):
    #     return self._engine._should_log_info()

    # def connect(self):
    #     d = self._defer_to_thread(self._engine.connect)
    #     d.addCallback(TwistedConnection, self)
    #     return d

    # def execute(self, *args, **kwargs):
    #     d = self._defer_to_thread(self._engine.execute, *args, **kwargs)
    #     d.addCallback(TwistedResultProxy, self)
    #     return d

    # def has_table(self, table_name, schema=None):
    #     return self._defer_to_thread(
    #         self._engine.has_table, table_name, schema)

    # def table_names(self, schema=None, connection=None):
    #     if connection is not None:
    #         connection = connection._connection
    #     return self._defer_to_thread(
    #         self._engine.table_names, schema, connection)

