#!/usr/bin/env python
from __future__ import print_function
import multiprocessing, time
import cProfile
import pycovenantsql

def func_time(func):
    def _wrapper(*args,**kwargs):
        start = time.time()
        func(*args,**kwargs)
        print(func.__name__,'run:',time.time()-start)
    return _wrapper

pycovenantsql.connections.DEBUG = True
pycovenantsql.connections.VERBOSE = False

#key_file = 'admin.test.covenantsql.io-key.pem'
#proxy_pem = 'admin.test.covenantsql.io.pem'
#conn = pycovenantsql.connect(dsn='covenant://057e55460f501ad071383c95f691293f2f0a7895988e22593669ceeb52a6452a',
#        host="192.168.2.100", port=11105, https_pem=proxy_pem,
#        key=key_file, database='057e55460f501ad071383c95f691293f2f0a7895988e22593669ceeb52a6452a')

key_file = 'write.dba.data.covenantsql.io.key'
proxy_pem = 'write.dba.data.covenantsql.io.pem'
conn = pycovenantsql.connect(dsn='covenant://053d0bb19637ffc7b4a94e3c79cc71b67a768813b09e4b67f1d6159902754a8b',
        host="e.morenodes.com", port=11108, https_pem=proxy_pem,
        key=key_file, database='053d0bb19637ffc7b4a94e3c79cc71b67a768813b09e4b67f1d6159902754a8b')

cur = conn.cursor()

table_name = "test_python_driver"

def drop(name):
    cur.execute("drop table if exists `%s`" % name)
def create(name):
    cur.execute('''create table `%s` (
        name text not null,
        primary key(name)
        )''' % name)

def multi_exec(num, total):
    now = 0
    while now < total:
        current = []
        for i in range(num):
            current.append(now+i)
        cur.executemany("replace into " + table_name + " values(%s)", current)
        now += num

def single_exec(data):
    cur.execute("replace into " + table_name + " values(%s)", data)

def single_query(num):
    cur.execute("SELECT * FROM  " + table_name + " limit %s", num)
    #for row in cur:
    #    print(row)

@func_time
def process(process_num, num):
    pool = multiprocessing.Pool(processes=process_num)
    for i in range(num):
        pool.apply_async(single_exec, (i, ))
    pool.close()
    pool.join()
    print("Sub-process(es) done.")

if __name__ == "__main__":
    drop(table_name)
    create(table_name)

    single_exec("what")
    cProfile.run('multi_exec(10000, 30000)')
    cProfile.run('single_query(30000)')
    process(5, 20)
    cur.close()
    conn.close()
