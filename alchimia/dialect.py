from sqlalchemy.dialects import registry


class TxPostgresPool(object):


    def __init__(self, connstr):
        self.connstr = connstr

    def connect(self):
        from txpostgres import txpostgres
        conn = txpostgres.Connection()
        return conn.connect(self.connstr)


class TxPostgresDialect(object):


    def url_to_connstr(self, url):
        opts = url.translate_connect_args(username='user')
        return ('dbname=%(database)s host=%(host)s port=%(port)d '
                'user=%(user)s password=%(password)s' % opts)
    


def register():
    registry.register('postgres.txpostgres', 'alchimia.dialect',
                      'TxPostgresDialect')
    registry.register('postgresql.txpostgres', 'alchimia.dialect',
                      'TxPostgresDialect')
