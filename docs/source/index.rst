.. JUDI documentation master file, created by
   sphinx-quickstart on Fri Apr 19 14:19:08 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
JUDI: Software Pipeline, *Just Do It*
======================================

.. meta::
   :description lang=en: Automate building, and rebuilding software pipelines under different parameter settings.


`JUDI`_ simplifies building and maintaining software pipeline
by automating optimum execution of the pipeline under different
parameter settings.

Consolidated specification of parameter settings 
    Specify all possible parameter settings under which the
    pipeline needs to be excuted. JUDI keeps track of those
    settings in a database table.

Decouple files and tasks from parameter settings
    For each file and task, just specify which parameters it depends upon
    and then build the pipeline as if there were parameters.
    JUDI makes sure there are seperate instances of the file and the task
    for each settings of the parameters and automates the association between
    the file and task instances.

Enable plug-and-play
    Decoupling parameter settings from files and tasks by abstracting them helps
    easy building of pipelines by plug and play.

.. _JUDI: http://judi.readthedocs.org/


.. _get-started

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting Started

   intro/install-judi
   intro/build-pipeline
   intro/execute-pipeline


.. _user-docs:

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   features/param-db
   features/judi-files
   features/judi-tasks
   features/doit


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
