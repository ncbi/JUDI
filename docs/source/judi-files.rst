JUDI File
=========

.. meta::
   :description lang=en: File in JUDI


A JUDI File is associated with a parameter database and actually represents a collection of physical files, each corresponding to a row in the parameter database.


.. autoclass:: judi.File
   :members:

   .. automethod:: __init__

Some examples
-------------

The following code snippet creates a global parameter database with two parameters W and X and then creates a file with a parameter database that masks parameter W in the global parameter database.

.. code-block:: python
   :emphasize-lines: 15

   >>> from judi import add_param, show_param_db, File
   >>> add_param("1 2".split(), 'W')
   0
   >>> add_param("a b c".split(), 'X')
   0
   >>> show_param_db()
   Global param db:
      W  X
   0  1  a
   1  1  b
   2  1  c
   3  2  a
   4  2  b
   5  2  c
   >>> f = File('test', mask = ['W'])
   Creating new directory ./judi_files/X~a
   Creating new directory ./judi_files/X~b
   Creating new directory ./judi_files/X~c
   >>> show_param_db(f.param)
   Param db:
      X  name                   path
   0  a  test  ./judi_files/X~a/test
   1  b  test  ./judi_files/X~b/test
   2  c  test  ./judi_files/X~c/test
