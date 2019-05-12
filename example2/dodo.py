from judi import File, Task, add_param, show_param_db, combine_csvs


add_param([1, 2], 'n')

show_param_db()

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

