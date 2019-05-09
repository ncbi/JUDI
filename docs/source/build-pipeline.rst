Build and Execute a Simple Pipeline
===================================

.. meta::
   :description lang=en: Get started creating software pipelines using JUDI.

Let's consider a simple pipeline working on two input files, ``a.txt``:

.. code-block:: text
   :linenos:

   Hello you!

and ``b.txt``:

.. code-block:: text
   :linenos:

   Hello you,
   and your friends!

For each of the two files, the first stage of the pipeline computes
the number of lines, words and characters and stores in a comma-separated file.

The second stage combines the two comma-separated files into a single
comma-separated file with an extra field to indicate the source.

Build pipeline
--------------

The Python code ``dodo.py`` for building this pipeline using JUDI is:

.. code-block:: python
   :linenos:

   from judi import File, Task, add_param, combine_csvs
   
   add_param([1, 2], 'n')
   
   class GetCounts(Task):
     """Count lines, words and characters in file"""
     inputs = {'inp': File('text', path=['a.txt', 'b.txt'])}
     targets = {'out': File('counts.csv')}
     actions = [("(echo line word char file; wc {}) | sed 's/^ \+//;s/ \+/,/g' > {}", ["$inp", "$out"])]
   
   class CombineCounts(Task):
     """Combine counts"""
     mask = ['n']
     inputs = {'inp': GetCounts.targets['out']}
     targets = {'out': File('result.csv', mask=mask, root='.')}
     actions = [(combine_csvs, ["#inp", "#out"])]

Execute pipeline
----------------

The pipeline is executed from command line:

.. code-block:: console

   $ doit -f dodo.py
   .  GetCounts:n~1
   .  GetCounts:n~2
   .  CombineCounts:

The ``.`` before each pipeline task denotes that the task was computed afresh.

The first stage generates two intermediate count files, ``judi_files/n~1/counts.csv`` and
``./judi_files/n~2/counts.csv``.

.. code-block:: console

   $ cat judi_files/n~1/counts.csv
   line,word,char,file
   1,2,11,a.txt
   $ cat judi_files/n~2/counts.csv
   line,word,char,file
   2,5,29,b.txt

The second stage consolidates the counts in a file ``result.csv``:

.. code-block:: console

   $ cat result.csv
   line,word,char,file,n
   1,2,11,a.txt,1
   2,5,29,b.txt,2


Re-execute pipeline
-------------------

Invoking ``doit`` again gives:

.. code-block:: console

   $ doit -f dodo.py
   -- GetCounts:n~1
   -- GetCounts:n~2
   -- CombineCounts:

where ``--`` denotes that the pipeline task was not executed.

Now let's update the second input file ``b.txt`` to: 

.. code-block:: text
   :linenos:

   Hello you,
   your friends,
   and whole world!

and execute the pipeline again:

.. code-block:: console

   $ doit -f dodo.py
   .  GetCounts:n~2
   -- GetCounts:n~1
   .  CombineCounts:

This time only the counts for ``b.txt`` is recomputed, the unaffected part of
the pipeline for ``a.txt`` is not executed.
