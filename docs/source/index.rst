.. JUDI documentation master file, created by
   sphinx-quickstart on Fri Apr 19 14:19:08 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
JUDI: Software Pipeline, *Just Do It*
======================================

.. meta::
   :description lang=en: Automate building, and rebuilding software pipelines under different parameter settings.


`JUDI`_ simplifies building and executing a software pipeline
under different parameter settings by automating an efficient execution
of the pipeline across the settings.

Consolidated specification of parameter settings 
    JUDI provides an easy and efficient way to specify all possible settings of the parameters
    which the pipeline needs to be executed for.

Files and tasks independent from parameter settings
    For each file/task, a user of JUDI just specifies the parameters the file/task depends upon
    and then builds the pipeline as if there were no parameters at all.  JUDI makes sure there
    are separate instances of the file/task for each setting of the parameters, creates
    appropriate association between the file instances and the task instances, and automates
    an efficient execution of the task instances based on their dependency on other tasks.

Easy plug-and-play
    By decoupling parameter settings from files and tasks, JUDI enables an easy
    plug and play of different stages of the pipeline.

.. _JUDI: http://pyjudi.readthedocs.org/


.. _get-started:

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   install-judi
   build-pipeline


.. _user_docs:

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   param-db
   judi-files
   judi-tasks

.. _putting_together:

.. toctree::
   :maxdepth: 2
   :caption: Putting Together

   example/pipeline
   example/judi-code
   example/run

.. _advanced_use:

.. toctree::
   :maxdepth: 3
   :caption: Advanced Usage

   list-tasks
   clean-tasks
   advanced


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
