# JUDI - Bioinformatics Pipeline: *Just Do It*

*judi* comes from the idea of bringing the power and efficiency of *doit* to
execute any kind of task under many combinations of parameter settings.


## Sample Code

Snippet from [tutorial](example2), save it as ``dodo.py``. Also download [a.txt](example2/a.txt) and [b.txt](example2/b.txt).

```python
from judi import File, Task, add_param, show_param_db, combine_csvs

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
```

Run from terminal:

```console
$ doit list
CombineCounts
GetCounts
Task
$ doit
. GetCounts:n~2
. GetCounts:n~1
. CombineCounts:
```

## Project Details

 - Website & docs - [https://pyjudi.readthedocs.io](https://pyjudi.readthedocs.io)
 - Project management on github - [https://github.com/ncbi/JUDI](https://github.com/ncbi/JUDI)

## License

The MIT License
Copyright (c) 2019-2020 Soumitra Pal

see LICENSE file


## Install

*judi* is tested on python 3.6.

```console
$ pip install judi
```

## Dependencies

- doit

## Documentation

``docs`` folder contains ReST documentation based on Sphinx.

```console
$ make html
```

## Contributing

On github create pull requests using a named feature branch.
