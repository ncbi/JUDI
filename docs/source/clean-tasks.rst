Cleanup Files
=============

.. meta::
   :description lang=en: Cleanup files created by a JUDI task.

It is possible to selectively delete the physical files created by a JUDI task or a task instance. For example,
``doit clean -f dodo.py CombineCounts`` on the dodo script created in `this example <build-pipeline.html>`_
deletes the result file from the final stage of the pipeline.

.. code-block:: console

   $ doit clean -f dodo.py CombineCounts
   CombineCounts: - removing file './result.csv'


The following example shows how to clean the files created by a single task instance.

.. code-block:: console

   $ doit clean -f dodo.py GetCounts:n~1
   GetCounts:n~1 - removing file './judi_files/n~1/counts.csv'

More details about DoIt clean command can be found `here <http://pydoit.org/cmd_other.html#clean>`_.
