PyCovenantSQL
=======

.. contents:: Table of Contents
   :local:

This package contains a pure-Python CovenantSQL client library, based on `PEP 249`_.


NOTE: PyCovenantSQL only support high level APIs defined in `PEP 249`_.

.. _`PEP 249`: https://www.python.org/dev/peps/pep-0249/


Requirements
-------------

* Python -- one of the following:

  - CPython_ : 2.7 and >= 3.4
  - PyPy_ : Latest version

* HTTP Client:

  - Requests_ >= 2.19

* CovenantSQL Proxy Server:

  - CovenantSQL_ >= 0.0.2


.. _CPython: https://www.python.org/
.. _PyPy: https://pypy.org/
.. _Requests: http://www.python-requests.org/
.. _CovenantSQL: https://github.com/CovenantSQL/CovenantSQL



Installation
------------

Package is uploaded on `PyPI <https://pypi.org/project/PyCovenantSQL>`_.

You can install it with pip::

    $ python3 -m pip install PyCovenantSQL


Documentation
-------------

Documentation is available online: https://PyCovenantSQL.readthedocs.io/

Key file and database_id can get from: https://testnet.covenantsql.io/quickstart

For support, please refer to the `StackOverflow
<https://stackoverflow.com/questions/tagged/PyCovenantSQL>`_.

Example
-------

The following examples make use of a simple table

.. code:: sql

   CREATE TABLE `users` (
       `id` INTEGER PRIMARY KEY AUTOINCREMENT,
       `email` varchar(255) NOT NULL,
       `password` varchar(255) NOT NULL
   );


.. code:: python

    import pycovenantsql.cursors

    # user key file location
    key = '/path/to/private.key'

    # Connect to the database
    connection = pycovenantsql.connect(host='localhost',
                                 port=11108,
                                 key=key,
                                 database='database_id'
                                 )

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
            cursor.execute(sql, ('webmaster@python.org', 'very-secret'))

        # connection is autocommit. No need to commit in any case.
        # connection.commit()

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
            cursor.execute(sql, ('webmaster@python.org',))
            result = cursor.fetchone()
            print(result)
    finally:
        connection.close()

This example will print:

.. code:: python

    {'password': 'very-secret', 'id': 1}


Resources
---------

* DB-API 2.0: http://www.python.org/dev/peps/pep-0249

* CovenantSQL Website: https://covenantsql.io/

* CovenantSQL testnet quick start:
  https://testnet.covenantsql.io/quickstart

* CovenantSQL source code:
  https://github.com/CovenantSQL/CovenantSQL


License
-------

PyCovenantSQL is released under the Apache 2.0 License. See LICENSE for more information.
