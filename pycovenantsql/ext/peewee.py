import pycovenantsql
from peewee import Database, ImproperlyConfigured

class CovenantSQLDatabase(Database):
    param = '%s'
    quote = '``'
    def __init__(self, database, **kwargs):
        super(CovenantSQLDatabase, self).__init__(database, **kwargs)

    def _connect(self, **kwargs):
        if pycovenantsql is None:
            raise ImproperlyConfigured('pycovenantsql driver not installed!')
        conn = pycovenantsql.connect(database=self.database, **self.connect_params)
        return conn