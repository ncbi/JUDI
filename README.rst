JUDI - Bioinformatics Pipeline: *Just Do It*
============================================

*judi* comes from the idea of bringing the power and efficiency of *doit* to
execute any kind of task under many combinations of parameter settings.


Sample Code
===========

Define functions returning python dict with task's meta-data.

Snippet from `tutorial <https://judi.readthedocs.io/tutorial_1.html>`_::

.. code-block:: python

    from judi import File, Task, add_param, combine_csvs

    add_param('100 101 102 103'.split(), 'sample')
    add_param('1 2'.split(), 'group')

    REF = 'hg_refs/hg19.fa'
    path_gen = lambda x: '{}_{}.fq'.format(x['sample'],x['group'])

    class AlignFastq(Task):
      inputs = {'reads': File('orig_fastq', path = path_gen)}
      targets = {'sai': File('aln.sai')}
      actions = [('bwa aln {} {} > {}', [REF,'$reads','$sai'])]

    class CreateBam(Task):
      mask = ['group']
      inputs = {'reads': AlignFastq.inputs['reads'],
                'sai': AlignFastq.targets['sai']}
      targets = {'bam': File('aln.bam', mask = mask)}
      actions = [('bwa sampe {} {} {} | samtools view -Sbh - | samtools sort - > {}', [REF,'$sai','$reads','$bam'])]

    class GetCoverage(Task):
      mask = ['group']
      inputs = {'bam': CreateBam.targets['bam']}
      targets = {'cov': File('cov.csv', mask = mask)}
      actions = [('(echo val; samtools rmdup {} - | samtools mpileup - | cut -f4) > {}', ['$bam','$cov'])]

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


Run from terminal::

.. code-block:: console

  $ doit list
  AlignFastq
  CombineCoverage
  CreateBam
  GetCoverage
  $ doit
  . AlignFastq:group~1,sample~100
  . AlignFastq:group~2,sample~100
  . AlignFastq:group~1,sample~101
  . AlignFastq:group~2,sample~101
  . AlignFastq:group~1,sample~102
  . AlignFastq:group~2,sample~102
  . AlignFastq:group~1,sample~103
  . AlignFastq:group~2,sample~103
  . CreateBam:sample~100
  . CreateBam:sample~102
  . CreateBam:sample~103
  . CreateBam:sample~101
  . GetCoverage:sample~100
  . GetCoverage:sample~102
  . GetCoverage:sample~103
  . GetCoverage:sample~101
  . CombineCoverage:


Project Details
===============

 - Website & docs - https://pyjudi.readthedocs.io
 - Project management on github - https://github.com/ncbi/JUDI

License
=======

The MIT License
Copyright (c) 2019-2020 Soumitra Pal

see LICENSE file


Install
=======

*judi* is tested on python 3.6.

.. code-block:: console

  $ pip install judi


Dependencies
=============

- doit

Documentation
=============

``docs`` folder contains ReST documentation based on Sphinx.

.. code-block:: console

  docs$ make html

Contributing
==============

On github create pull requests using a named feature branch.
