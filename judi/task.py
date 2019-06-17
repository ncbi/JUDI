import pandas as pd

from .paramdb import *
from .file import *
from .utils import *

def print_nested_df(cfg):
  dfs = [cfg]
  def dedf(x):
    if isinstance(x, pd.DataFrame):
      dfs.append(x)
      return "df{}".format(len(dfs))
    return x
  dfs[0] = cfg.applymap(dedf)
  for i, df in enumerate(dfs):
    print(f"df{i}:\n", df)

def get_file_paths(pdb_row, file_key):
  return pdb_row[file_key]['path'].tolist()


class Task(object):
  """Base Task"""
  @classmethod
  def create_doit_tasks(cls):
    show_details = 0
    if show_details:
      print(f"\n=================== Working on {cls} =============\n")
    if cls is Task:
        return # avoid create tasks from base class 'Task'
    # Build a dictionary from the class variables
    kw = dict((a, getattr(cls, a)) for a in dir(cls) if not a.startswith('_')) 
    # We are interested only in few class variables
    kw = {k:v for k,v in kw.items() if k in ['param', 'mask', 'inputs', 'targets', 'run', 'actions']}
    kw['doc'] = cls.__doc__
    kw['basename'] = cls.__name__ 
    kw['clean'] = True 
    kw['verbosity'] = 2 

    global JUDI_PARAM
    param = (kw.pop('param') if 'param' in kw else JUDI_PARAM).copy()

    mask = kw.pop('mask') if 'mask' in kw else None
    if mask: param.mask(mask)

    inputs = kw.pop('inputs')
    targets = kw.pop('targets')

    cfg_cols = param.df.columns.tolist()
    cfg_cols_wo_spl = list(filter(lambda x: x != 'JUDI', cfg_cols))

    # For each input/target file f create D_{t,f} table
    # and merge the information to the param.df db
    for files in [inputs, targets]:
      for fkey in files.keys():
        grp_cols = list(filter(lambda x: x in cfg_cols, files[fkey].param.df.columns))
        engroup = lambda x: pd.DataFrame({fkey:[x.drop(columns=grp_cols)]})
        dtf = files[fkey].param.df.groupby(grp_cols).apply(engroup)
        dtf.index = dtf.index.droplevel(len(grp_cols))
        dtf = dtf.reset_index()
        #print_nested_df(dtf)
        param.df = param.df.merge(dtf)

    # add name only after saving the original config columns
    param.df['name'] = param.df[cfg_cols].apply(lambda x: get_cfg_str(x), axis='columns')
    param.df['parcfg'] = param.df[cfg_cols].apply(lambda x: get_cfg_str_unsrt(x), axis='columns')

    for (j, t) in param.df.iterrows():
      newkw = kw.copy()
      newkw['name'] = t['name'] 
      newkw['targets'] = [p for f in targets.keys() for p in get_file_paths(t, f)]
      newkw['file_dep'] = [p for f in inputs.keys() for p in get_file_paths(t, f)]

      if 'actions' not in newkw:
        #get the name of the arguments of run
        varnames = newkw['run'].__code__.co_varnames[1:] # first variable is 'self' which should be ignored
        newkw['actions'] = [(newkw.pop('run'), [get_file_paths(t, v) for v in varnames])] # TODO: list as argument
      else:
        actions = []
        for action in newkw['actions']:
          newargs = []
          if isinstance(action, (list,tuple)):
            act, args = action
          else:
            act = action
          for arg in args:
            if isinstance(arg, str):
              if arg[0] == '$':
                plist = t[arg[1:]]['path'].tolist()
                newargs.append(plist[0] if len(plist) == 1 else plist)
              elif arg[0] == '#':
                if arg == '##':
                  newargs.append(t[cfg_cols_wo_spl])
                else:
                  newargs.append(t[arg[1:]])
              else:
                newargs.append(arg)
            else:
              newargs.append(arg)
          if isinstance(act, str):
            for i, v in enumerate(newargs):
              if isinstance(v, list):
                newargs[i] = ' '.join(v)
            newact = act.format(*newargs)
            newargs = []
          else:
            newact = act
          actions += [(newact, newargs) if len(newargs) else (newact)]
        newkw['actions'] = actions
      if show_details:
        print("------------------")
        for key, val in newkw.items():
          print(key, "\t:", val)
      yield newkw

