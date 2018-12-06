import gc
import json
import os
import re
import warnings

import unittest2

import pycovenantsql
from .._compat import CPYTHON


class PyCovenantSQLTestCase(unittest2.TestCase):
    # You can specify your test environment creating a file named
    #  "databases.json" or editing the `databases` variable below.
    fname = os.path.join(os.path.dirname(__file__), "databases.json")
    if os.path.exists(fname):
        with open(fname) as f:
            databases = json.load(f)
    else:
        databases = [
                {"host":"192.168.2.100","port":11105,"https_pem":"admin.test.covenantsql.io.pem",
                    "key":"admin.test.covenantsql.io-key.pem", "database":"057e55460f501ad071383c95f691293f2f0a7895988e22593669ceeb52a6452a"},
                {"host":"e.morenodes.com","port":11108,"https_pem":"write.dba.data.covenantsql.io.pem",
                    "key":"write.dba.data.covenantsql.io.key","database":"053d0bb19637ffc7b4a94e3c79cc71b67a768813b09e4b67f1d6159902754a8b"}]

    _connections = None

    @property
    def connections(self):
        if self._connections is None:
            self._connections = []
            for params in self.databases:
                self._connections.append(pycovenantsql.connect(**params))
            self.addCleanup(self._teardown_connections)
        return self._connections

    def connect(self, **params):
        p = self.databases[0].copy()
        p.update(params)
        conn = pycovenantsql.connect(**p)
        @self.addCleanup
        def teardown():
            if conn.open:
                conn.close()
        return conn

    def _teardown_connections(self):
        if self._connections:
            for connection in self._connections:
                if connection.open:
                    connection.close()
            self._connections = None

    def safe_create_table(self, connection, tablename, ddl, cleanup=True):
        """create a table.

        Ensures any existing version of that table is first dropped.

        Also adds a cleanup rule to drop the table after the test
        completes.
        """
        cursor = connection.cursor()

        self.drop_table(connection, tablename)
        cursor.execute(ddl)
        cursor.close()
        if cleanup:
            self.addCleanup(self.drop_table, connection, tablename)

    def drop_table(self, connection, tablename):
        cursor = connection.cursor()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cursor.execute("drop table if exists `%s`" % (tablename,))
        cursor.close()

    def safe_gc_collect(self):
        """Ensure cycles are collected via gc.

        Runs additional times on non-CPython platforms.

        """
        gc.collect()
        if not CPYTHON:
            gc.collect()

