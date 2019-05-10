List Pipeline Stages
====================

.. meta::
   :description lang=en: List the stages of a pipeline created using JUDI

The ``list`` command in DoIt can be used to query the tasks created in a ``dodo`` script.

For example, ``doit list -f dodo.py`` on the dodo script described `here <build-pipeline.html>`_
gives the following output.

.. code-block:: console

   $ doit list -f dodo.py
   CombineCounts
   GetCounts
   Task

Note that ``Task`` here is the default task that all other tasks inherit from. It is also possible to list
and see the status of the task instances, whether to rebuild etc., using the ``--all --status`` options
of ``doit list`` command.

.. code-block:: console

   $ doit list --all --status -f dodo.py
   R CombineCounts
   U CombineCounts:   Combine counts
   R GetCounts
   U GetCounts:n~1    Count lines, words and characters in file
   U GetCounts:n~2    Count lines, words and characters in file
   R Task

where ``R`` denotes 'to run' and ``U`` denotes 'to update'. More details on the ``doit list`` command can be
found `here <http://pydoit.org/cmd_other.html#list>`_.

