#!/usr/bin/env python
from __future__ import print_function

import pycovenantsql


print(pycovenantsql.get_client_info())

conn = pycovenantsql.connect(dsn='covenant://0a10b74439f2376d828c9a70fd538dac4b69e0f4065424feebc0f5dbc8b34872',
        host="adp00.cn.gridb.io", port=7784, database='0a10b74439f2376d828c9a70fd538dac4b69e0f4065424feebc0f5dbc8b34872')

cur = conn.cursor()
print(cur.description)

cur.execute('''create table if not exists test_python_driver(
        name text not null,
        primary key(name)
        )''')
print(cur.description)
cur.execute("replace into test_python_driver values('test'), ('test2'), ('test3'), ('test4')")
print(cur.description)
cur.execute(" SELECT * FROM test_python_driver")
print(cur.description)
cur.execute("desc test_python_driver")
print(cur.description)
for row in cur:
    print(row)
cur.execute("show tables")
for row in cur:
    print(row)

cur.close()
conn.close()
