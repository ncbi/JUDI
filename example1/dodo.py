from judi import File, Task, add_param, combine_csvs

add_param('100 101 102 103'.split(), 'sample')
add_param('1 2'.split(), 'group')

REF = 'hg_refs/hg19.fa'
path_gen = lambda x: '{}_{}.fq'.format(x['sample'],x['group'])

class AlignFastq(Task):
  inputs = {'reads': File('orig_fastq', root = '.', path = path_gen)}
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
