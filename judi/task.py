import pandas as pd

from .paramdb import *
from .file import *
from .utils import *

from doit.tools import run_once

def print_nested_df(orig):
  dfs = [None]
  def dedf(x):
    if isinstance(x, pd.DataFrame):
      i = len(dfs)
      dfs.append(x)
      return f"df{i}"
    return x
  dfs[0] = orig.applymap(dedf)
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
    kw = {k:v for k,v in kw.items() if k in ['param', 'mask', 'mask_row', 'keep', 'inputs', 'targets', 'run', 'actions']}
    kw['doc'] = cls.__doc__
    kw['basename'] = cls.__name__ 
    kw['clean'] = True 
    kw['verbosity'] = 2 

    global JUDI_PARAM
    param = (kw.pop('param') if 'param' in kw else JUDI_PARAM).copy()

    mask = kw.pop('mask') if 'mask' in kw else None
    if mask: param.mask(mask)
    
    mask_row = kw.pop('mask_row') if 'mask_row' in kw else None
    if mask_row: param.query(mask_row)

    keep = kw.pop('keep') if 'keep' in kw else None
    if keep: param.keep(keep)

    # A JUDI task must define targets and optionally inputs
    targets = kw.pop('targets')
    file_dicts = [targets]
    inputs = None
    if 'inputs' in kw:
      inputs = kw.pop('inputs')
      file_dicts += [inputs]
    

    cfg_cols = param.df.columns.tolist()
    cfg_cols_wo_spl = list(filter(lambda x: x != 'JUDI', cfg_cols))

    def engroup(x, cols):
      #print(x)
      #we need to reindex the dataframe, otherwise it gives some error
      return pd.DataFrame({fkey:[x.drop(cols, axis='columns').reindex()]})

    # For each input/target file f create D_{t,f} table
    # and merge the information to the param.df db
    for files in file_dicts:
      for fkey in files.keys():
        #print("============", fkey, "=============")
        grp_cols = list(filter(lambda x: x in cfg_cols, files[fkey].param.df.columns))
        #print(grp_cols)
        #print(files[fkey].param.df)
        dtf = files[fkey].param.df.groupby(grp_cols).apply(engroup, cols=grp_cols)
        #print(dtf)
        #print("~~~~~~~*********\nnested dtf")
        #print_nested_df(dtf)
        dtf.index = dtf.index.droplevel(len(grp_cols))
        dtf = dtf.reset_index()
        #print("******************\nnested dtf")
        #print_nested_df(dtf)
        param.df = param.df.merge(dtf)
        #print("##################\nnested df")
        #print_nested_df(param.df)

    # add name only after saving the original config columns
    param.df['name'] = param.df[cfg_cols].apply(lambda x: get_cfg_str(x), axis='columns')
    param.df['parcfg'] = param.df[cfg_cols].apply(lambda x: get_cfg_str_unsrt(x), axis='columns')

    #print_nested_df(param.df)
    def substitute(arg, t):
      if isinstance(arg, str):
        if arg[0] == '$':
          plist = t[arg[1:]]['path'].tolist()
          return(plist[0] if len(plist) == 1 else plist)
        elif arg[0] == '#':
          if arg == '##':
            return(t[cfg_cols_wo_spl])
          else:
            #print(kw['basename'])
            #print(arg)
            #print(t[arg[1:]])
            return(t[arg[1:]])
        else:
          return(arg)
      else:
        return(arg)

    for (j, t) in param.df.iterrows():
      #print(t['parcfg'])
      newkw = kw.copy()
      newkw['name'] = t['name'] 
      newkw['targets'] = [p for f in targets.keys() for p in get_file_paths(t, f)]

      if inputs:
        newkw['file_dep'] = [p for f in inputs.keys() for p in get_file_paths(t, f)]
      else :
        # if inputs not define, make targets to be built only once
        newkw['uptodate'] = [run_once]


      if 'actions' not in newkw:
        #get the name of the arguments of run
        varnames = newkw['run'].__code__.co_varnames[1:] # first variable is 'self' which should be ignored
        newkw['actions'] = [(newkw.pop('run'), [get_file_paths(t, v) for v in varnames])] # TODO: list as argument
      else:
        actions = []
        for action in newkw['actions']:
          newargs = []
          newactkws = {}
          if isinstance(action, (list,tuple)):
            if (len(action) > 2):
              act, args, act_kw = action
            else:
              act, args = action
              act_kw = {}
          else:
            act = action
          for arg in args:
            newargs.append(substitute(arg, t))
          for act_key in act_kw:
            newactkws[act_key] = substitute(act_kw[act_key], t)
          if isinstance(act, str):
            for i, v in enumerate(newargs):
              if isinstance(v, list):
                newargs[i] = ' '.join(v)
            newact = act.format(*newargs)
            newargs = []
          else:
            newact = act
          actions += [(newact, newargs, newactkws) if len(newargs) + len(newactkws) else (newact)]
        newkw['actions'] = actions
      if show_details:
        print("------------------")
        for key, val in newkw.items():
          print(key, "\t:", val)
      yield newkw

