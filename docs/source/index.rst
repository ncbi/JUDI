.. JUDI documentation master file, created by
   sphinx-quickstart on Fri Apr 19 14:19:08 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
JUDI: Software Pipeline, *Just Do It*
======================================

.. meta::
   :description lang=en: Automate building, and rebuilding software pipelines under different parameter settings.


`JUDI`_ simplifies building and executing a software pipeline
under different parameter settings by automating efficient execution
of the pipeline across the settings.

Consolidated specification of parameter settings 
    JUDI provides an easy way to specify all possible parameter settings
    under which the pipeline needs to be excuted.

Files and tasks independent from parameter settings
    For each file or a task, a user just specifies the parameters it depends upon
    and then builds the pipeline as if there were no parameters at all.
    JUDI makes sure there are seperate instances of the file or the task
    for each setting of the parameters, creates appropriate association between
    the file instances and the task instances, and automates an efficient execution
    of the task instances based on their dependency.

Easy plug-and-play
    By decoupling parameter settings from files and tasks, JUDI enables 
    plug and play of different stages of the pipeline.

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
