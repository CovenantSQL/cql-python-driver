#!/usr/bin/env python
from __future__ import print_function

import pycovenantsql

key = 'write.dba.data.covenantsql.io.key'
proxy_pem = 'write.dba.data.covenantsql.io.pem'


print(pycovenantsql.get_client_info())

conn = pycovenantsql.connect(dsn='covenant://053d0bb19637ffc7b4a94e3c79cc71b67a768813b09e4b67f1d6159902754a8b',
        host="e.morenodes.com", port=11108, https_pem=proxy_pem,
        key=key, database='053d0bb19637ffc7b4a94e3c79cc71b67a768813b09e4b67f1d6159902754a8b')

cur = conn.cursor()
print(cur.description)

#cur.execute('''create table test_python_driver(
#        name text not null,
#        primary key(name)
#        )''')
cur.execute("replace into test_python_driver values('test'), ('test2'), ('test3'), ('test4')")
cur.execute(" SELECT * FROM test_python_driver")
cur.execute("desc test_python_driver")
for row in cur:
    print(row)
cur.execute("show tables")
for row in cur:
    print(row)

cur.close()
conn.close()
