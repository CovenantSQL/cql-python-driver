PyCovenantSQL
===============

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

* Packages:

  - Requests_ >= 2.19
  - Arrow_ >= 0.13

* CovenantSQL Adapter Server:

  - CovenantSQL_ >= 0.0.3


.. _CPython: https://www.python.org/
.. _PyPy: https://pypy.org/
.. _Requests: http://www.python-requests.org/
.. _Arrow: https://github.com/crsmithdev/arrow
.. _CovenantSQL: https://github.com/CovenantSQL/CovenantSQL



Installation
------------

Package is uploaded on `PyPI <https://pypi.org/project/PyCovenantSQL>`_.

You can install it with pip::

    $ python3 -m pip install PyCovenantSQL


Documentation
-------------

Documentation is available online: http://developers.covenantsql.io/

Key file and dsn can get from: http://developers.covenantsql.io/docs/quickstart

For support, please fire a issue at `Github
<https://github.com/CovenantSQL/CovenantSQL/issues/new>`_.

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

    import pycovenantsql


    # Connect to the database with dsn
    # host and port are your local CovenantSQL Adapter server
    connection = pycovenantsql.connect(
                                 dsn='covenantsql://your_database_id',
                                 host='localhost',
                                 port=11108,
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
