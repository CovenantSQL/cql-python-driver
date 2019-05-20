import datetime
import sys
import time
import pycovenantsql
from pycovenantsql.tests import base
from pycovenantsql._compat import text_type
from pycovenantsql.converters import encoders


class TempUser:
    def __init__(self, c, user, db, auth=None, authdata=None, password=None):
        self._c = c
        self._user = user
        self._db = db
        create = "CREATE USER " + user
        if password is not None:
            create += " IDENTIFIED BY '%s'" % password
        elif auth is not None:
            create += " IDENTIFIED WITH %s" % auth
            if authdata is not None:
                create += " AS '%s'" % authdata
        try:
            c.execute(create)
            self._created = True
        except pycovenantsql.err.InternalError:
            # already exists - TODO need to check the same plugin applies
            self._created = False
        try:
            c.execute("GRANT SELECT ON %s.* TO %s" % (db, user))
            self._grant = True
        except pycovenantsql.err.InternalError:
            self._grant = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._grant:
            self._c.execute("REVOKE SELECT ON %s.* FROM %s" % (self._db, self._user))
        if self._created:
            self._c.execute("DROP USER %s" % self._user)


class TestConnection(base.PyCovenantSQLTestCase):

    def test_largedata(self):
        """Large query and response (<=9MB)"""
        cur = self.connections[0].cursor()
        t = 'a' * (9*1024*1024)
        cur.execute("SELECT '" + t + "'")
        assert cur.fetchone()[0] == t

    def test_read_default_group(self):
        conn = self.connect(
            read_default_group='client',
        )
        self.assertTrue(conn.open)

    def test_context(self):
        c = self.connect()
        with c as cur:
            cur.execute('create table test ( a int )')
            self.assertEqual(None, cur.fetchone())
        with c as cur:
            cur.execute('select count(*) from test')
            self.assertEqual(0, cur.fetchone()[0])
            cur.execute('insert into test values ((1))')
        with c as cur:
            cur.execute('select count(*) from test')
            self.assertEqual(1,cur.fetchone()[0])
            cur.execute('drop table test')


# A custom type and function to escape it
class Foo(object):
    value = "bar"


def escape_foo(x, d):
    return x.value


class TestEscape(base.PyCovenantSQLTestCase):
    def test_escape_string(self):
        con = self.connections[0]
        cur = con.cursor()

        self.assertEqual(con.escape("foo'bar"), "'foo''bar'")

    def test_escape_builtin_encoders(self):
        con = self.connections[0]
        cur = con.cursor()

        val = datetime.datetime(2012, 3, 4, 5, 6)
        self.assertEqual(con.escape(val), "'2012-03-04 05:06:00.000000'")

    def test_escape_custom_object(self):
        con = self.connections[0]
        cur = con.cursor()

        mapping = {Foo: escape_foo}
        self.assertEqual(con.escape(Foo(), mapping), "bar")

    def test_escape_fallback_encoder(self):
        con = self.connections[0]
        cur = con.cursor()

        class Custom(str):
            pass

        mapping = {text_type: pycovenantsql.escape_string}
        self.assertEqual(con.escape(Custom('foobar'), mapping), "'foobar'")

    def test_escape_no_default(self):
        con = self.connections[0]
        cur = con.cursor()

        self.assertRaises(TypeError, con.escape, 42, {})

    def test_escape_dict_value(self):
        con = self.connections[0]
        cur = con.cursor()

        mapping = encoders.copy()
        mapping[Foo] = escape_foo
        self.assertEqual(con.escape({'foo': Foo()}, mapping), {'foo': "bar"})

    def test_escape_list_item(self):
        con = self.connections[0]
        cur = con.cursor()

        mapping = encoders.copy()
        mapping[Foo] = escape_foo
        self.assertEqual(con.escape([Foo()], mapping), "(bar)")

    def test_previous_cursor_not_closed(self):
        con = self.connect()
        cur1 = con.cursor()
        cur1.execute("SELECT 1; SELECT 2")
        cur2 = con.cursor()
        cur2.execute("SELECT 3")
        self.assertEqual(cur2.fetchone()[0], 3)

    def test_commit_during_multi_result(self):
        con = self.connect()
        cur = con.cursor()
        cur.execute("SELECT 1; SELECT 2")
        con.commit()
        cur.execute("SELECT 3")
        self.assertEqual(cur.fetchone()[0], 3)

