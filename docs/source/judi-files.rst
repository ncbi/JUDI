JUDI File
=========

.. meta::
   :description lang=en: File in JUDI


A JUDI File is associated with a parameter database and actually represents a collection of physical files, each corresponding to a row in the parameter database.


.. autoclass:: judi.judi.File
   :members:

   .. automethod:: __init__

Some examples
-------------

The following code snippet creates a global parameter database with two parameters W and X and then creates a file with a parameter database that masks parameter W in the global parameter database.

.. code-block:: python
   :emphasize-lines: 7
   :linenos:

   from judi import add_param, show_param_db, File
   
   add_param("1 2".split(), 'W')
   add_param("a b c".split(), 'X')
   show_param_db()
   
   f = File('test', mask = ['W'])
   show_param_db(f.param)

The contents of the global parameter database and of the parameter database associated with the file are as follows:

.. code-block:: text

   Global param db:
      W  X
   0  1  a
   1  1  b
   2  1  c
   3  2  a
   4  2  b
   5  2  c
   Param db:
      X  name                   path
   0  a  test  ./judi_files/X~a/test
   1  b  test  ./judi_files/X~b/test
   2  c  test  ./judi_files/X~c/test
