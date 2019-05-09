JUDI Code
=========

.. meta::
   :description lang=en: Python code for implementing an example bioinformatics pipeline using JUDI

Here we demonstrate step by step how to build the pipeline described `here <pipeline.html>`_ using JUDI.

Parameter database
------------------

The pipeline has two parameters: ``sample`` with possible values 100,101,102,103 and ``group`` with
possible values 1,2. The global parameter database for the pipeline can be created as follows:

.. code-block:: python

   add_param('100 101 102 103'.split(), 'sample')
   add_param('1 2'.split(), 'group')


Files
-----

The pipeline deals with 5 types of files which can defined through the following 5 JUDI files.

* reads: 8 input FASTQ files, each corresponding to a row of the global parameter database.

.. code-block:: python

   path_gen = lambda x: '{}_{}.fq'.format(x['sample'],x['group'])
   reads = File('orig_fastq', path = path_gen)


* sai: 8 temporary alignment files that are created in the first stage of the pipeline. Its
  parameter database is same as the global parameter database.

.. code-block:: python

   sai = File('aln.sai')


* bam: 4 alignment files, one for each sample, that are created in the second stage of the pipeline. Its
  parameter database does not have parameter ``group`` and hence can be created by masking ``group``
  in the global parameter database.

.. code-block:: python

   bam = File('aln.bam', mask=['group'])


* cov: 4 genome coverage table file in CSV format, one for each sample, that are created in the
  third stage of the pipeline. Its parameter database does not have parameter ``group`` and
  hence can be created by masking ``group`` in the global parameter database.

.. code-block:: python

   cov = File('cov.csv', mask=['group'])


* combined-coverage: single consolidated coverage table file in CSV format, that is created in the
  final stage of the pipeline. Its parameter database can be created by masking both ``sample`` and 
  ``group`` in the global parameter database.

.. code-block:: python

   combined = File('combined.csv', mask=['sample', 'group'])


* plot: consolidated coverage table plotted in the final stage of the pipeline. Here, too parameter
  database can be created by masking both ``sample`` and ``group`` in the global parameter database.
  Optionally, we can store this in the current directory, instead of the default directory ``judi_files``.

.. code-block:: python

   plot = File('pltcov.csv', mask=['sample', 'group'], root='.')


Additionally, a reference genome file used by the pipeline. However, as this file is independent of the
parameters, we can keep it as a constant.

.. code-block:: python

   REF = 'hg_refs/hg19.fa'

Tasks
-----

Each of the four stages of the pipeline is implemented as a JUDI task.

* Align FASTQ: We need to align each FASTQ separately. So we create a task with parameter database
  same as the global parameter database.

.. code-block:: python

  class AlignFastq(Task):
    inputs = {'reads': File('orig_fastq', path = path_gen)}
    targets = {'sai': File('aln.sai')}
    actions = [('bwa aln {} {} > {}', [REF,'$reads','$sai'])]

* Create BAM: We need one task instance for each sample. So we create a task with only ``sample`` as
  the parameter, or alternatively by masking ``group`` from the global parameter database. We reuse
  the files defined in the ``AlignFastq`` task.

.. code-block:: python

  class CreateBam(Task):
    mask = ['group']
    inputs = {'reads': AlignFastq.inputs['reads'],
              'sai': AlignFastq.targets['sai']}
    targets = {'bam': File('aln.bam', mask = mask)}
    actions = [('bwa sampe {} {} {} | samtools view -Sbh - | samtools sort - > {}', [REF,'$sai','$reads','$bam'])]

* Get coverage: We need one task instance for each sample. So we create a task with ``group``
  masked from the global parameter database.

.. code-block:: python

   class GetCoverage(Task):
     mask = ['group']
     inputs = {'bam': CreateBam.targets['bam']}
     targets = {'cov': File('cov.csv', mask = mask)}
     actions = [('(echo val; samtools rmdup {} - | samtools mpileup - | cut -f4) > {}', ['$bam','$cov'])]

* Combine Coverage: We need only task instance. So we create a task with both ``sample`` and ``group``
  masked from the global parameter database.

.. code-block:: python

   class CombineCoverage(Task):
     mask = ['group', 'sample']
     inputs = {'cov': GetCoverage.targets['cov']}
     targets = {'csv': File('combined.csv', mask = mask),
              'pdf': File('pltcov.pdf', mask = mask, root = '.')}
     actions = [(combine_csvs, ['#cov', '#csv']),
                ("""echo "library(ggplot2); pdf('{}')
                 ggplot(read.csv('{}'), aes(x = val)) +
                 geom_density(aes(color = factor(sample)))"\
                 | R --vanilla""", ['$pdf','$csv'])]
   

