Parameter Database
==================

.. meta::
   :description lang=en: Parameter Database in JUDI

The main distinguishing feature of JUDI is the use of parameter database which captures all the different settings of parameters that the pipeline being build can possibly be executed for. JUDI maintains a parameter database as a pandas dataframe. The columns indicate the parameters and the rows the settings of the parameters.

In JUDI, each file and each task is associated with a parameter database. However, most of these databases are either the same or share many common parameters. Hence JUDI maintains a global parameter database and the parameter databases to individual file or task is specified as a list of masked parameters.

The global parameter database is populated using the following function:

.. automodule:: judi.judi
   :members: add_param

The global parameter database can be viewed using the following function:

.. automodule:: judi.judi
   :members: show_param_db

Some examples
-------------

In the following code snippet, the highlighted lines show examples of adding parameters to the global parameter database. Line 4 adds a parameter W having two possible values: 1,2. Line 6 adds a second parameter X with three possible values: a, b, c. Line 8 jointly adds two parameters Y,Z with three possible values (11,aa), (22,aa), (33,bb).

.. code-block:: python
   :emphasize-lines: 4,6,8
   :linenos:

   from judi import add_param, show_param_db
   import pandas as pd

   add_param("1 2".split(), 'W')
   show_param_db()
   add_param("a b c".split(), 'X')
   show_param_db()
   add_param(pd.DataFrame({'Y':[11, 22, 33], 'Z':['aa', 'aa', 'bb']}))
   show_param_db()

The contents of the global parameter database can be seen after each addition as follows:

.. code-block:: text

   Global param db:
      W
   0  1
   1  2
   Global param db:
      W  X
   0  1  a
   1  1  b
   2  1  c
   3  2  a
   4  2  b
   5  2  c
   Global param db:
       W  X   Y   Z
   0   1  a  11  aa
   1   1  a  22  aa
   2   1  a  33  bb
   3   1  b  11  aa
   4   1  b  22  aa
   5   1  b  33  bb
   6   1  c  11  aa
   7   1  c  22  aa
   8   1  c  33  bb
   9   2  a  11  aa
   10  2  a  22  aa
   11  2  a  33  bb
   12  2  b  11  aa
   13  2  b  22  aa
   14  2  b  33  bb
   15  2  c  11  aa
   16  2  c  22  aa
   17  2  c  33  bb
