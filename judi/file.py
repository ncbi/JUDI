import pandas as pd
from .paramdb import *
from .utils import *

class File(object):
  """A file in JUDI is an object of class File and is instantiated by calling the following constructor"""
  def __init__(self, basename, name = None, param = None, mask = None, keep = None, path = None,
               flat = True, root = './judi_files'):
    """Create a JUDI file instance.

    Args:
       basename (str): Base name of the JUDI file to be created.

    Kwargs:
       name (str) : This is an overall (kind of) identifier for the JUDI file.
       Currently it is used only for setting top-level-folder when flat is set
       false (see below). If None, it is set by replacing all dots (.) in basename
       with underscores (_), just to make sure that the top-level-folder does not
       look like a file having extension in it.

       param (ParamDb): Parameter database associated with the JUDI file. If param is empty,
       the golbal parameter database is taken to be associated with the file.

       mask (list of str): The list of parameters that are to be masked from the parameter database.

       keep (list of str): The list of parameters that are to be kept in the parameter database and
       remaining be removed.

       path: Specification of the physical path of the files associated with the JUDI file that is used
       to generate a column 'path' in the parameter database of the JUDI file. It can be of the
       following types:
           1) callable: a user provider path generator that is passed to pandas apply function,
           2) string or list of strings: actual path(s) to the physical files, and
           3) None: JUDI automatically generates a path for each row.

       flat (boolean): Whether to create the physical paths of a JUDI file under
       a flat directory structure such as
       "<root>/param1~value1,param2~value2,../<basename>" or a hierarchical one
       "<root>/name/param1~value1/param2~value2/../<basename>"

       root (str): Top level directory where the physical files associated with the JUDI file are created.
    """
    self.param = (param if param else JUDI_PARAM).copy(name)
    if mask: self.param.mask(mask)
    if keep: self.param.keep(keep)
    if (not name) and (basename):
        name = basename.replace('.', '_')
    self.param.df.drop_duplicates(inplace=True)
    if not self.param.df.empty:
      self.param.df['name'] = name
      if not path:
        if not 'path' in self.param.df.columns:
          if flat:
            self.param.df['path'] = self.param.df.apply(lambda x: get_cfg_str(x), axis='columns')
            self.param.df['path'] = self.param.df.apply(lambda x: "/".join([e for e in [x['path'], x['name']] if e]), axis = 'columns')
          else:
            self.param.df['path'] = self.param.df.apply(lambda x: get_cfg_str(x, param_sep='/'), axis='columns')
            self.param.df['path'] = self.param.df.apply(lambda x: "/".join([e for e in [x['name'], x['path'], basename] if e]), axis = 'columns')
      elif callable(path):
        self.param.df['path'] = self.param.df.apply(path, axis='columns')
      else:
        self.param.df['path'] = path
      if root:
        self.param.df['path'] = self.param.df.apply(lambda x: "/".join([e for e in [root, x['path']] if e]), axis = 'columns')
      #for path in self.param.df['path'].tolist():
      #  print(path)
      #  #ensure_dir(path)

  def copy(self, name=None):
    # to make sure that the path name copied exactly, we need to pass root as None
    newf = File(basename=None, name=name, param=self.param, root=None)
    return newf

  def rename(self, chdict):
    self.param.df.rename(columns=chdict, inplace=True)

  def query(self, q):
    new = self.copy()
    new.param.df.query(q, inplace=True)
    return new

