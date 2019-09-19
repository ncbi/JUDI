import pandas as pd
from .paramdb import *
from .utils import *

class File(object):
  """A file in JUDI is an object of class File and is instantiated by calling the following constructor"""
  def __init__(self, name, param = None, mask = None, keep = None, path = None, root = './judi_files'):
    """Create a JUDI file instance.

    Args:
       name (str): Name of the JUDI file to be created.

    Kwargs:
       param (ParamDb): Parameter database associated with the JUDI file. If param is empty,
       the golbal parameter database is taken to be associated with the file.
       
       mask (list of str): The list of parameters that are to be masked from the parameter database.

       keep (list of str): The list of parameters that are to be kept in the parameter database and remaining be removed.

       path: Specification of the physical path of the files associated with the JUDI file that is used
       to generate a column 'path' in the parameter database of the JUDI file. It can be
       of the following types: 1) callable: a user provider path generator that is passed to pandas apply function,
       2) string or list of strings: actual path(s) to the physical files, and 3)
       None: JUDI automatically generates a path for each row.

       root (str): Top level directory where the physical files associated with the JUDI file are created.
    """
    self.param = (param if param else JUDI_PARAM).copy(name)
    if mask: self.param.mask(mask)
    if keep: self.param.keep(keep)
    if not self.param.df.empty:
      #if len(set(self.param.df.columns) - set(JUDI_PARAM.df.columns)):
      #  print("Error: columns of param do not match with global param!!")
      #  exit(-1)
      self.param.df['name'] = name
      if not path:
        if not 'path' in self.param.df.columns:
          self.param.df['path'] = self.param.df.apply(lambda x: get_cfg_str(x), axis='columns')
          self.param.df['path'] = self.param.df.apply(lambda x: "/".join([e for e in [x['path'], x['name']] if e]), axis = 'columns')
      elif callable(path):
        self.param.df['path'] = self.param.df.apply(path, axis='columns')
      else:
        self.param.df['path'] = path
      if root:
        self.param.df['path'] = self.param.df.apply(lambda x: "/".join([e for e in [root, x['path']] if e]), axis = 'columns')
      for path in self.param.df['path'].tolist():
        ensure_dir(path)

  def copy(self, name=None):
    # to make sure that the path name copied exactly, we need to pass root as None
    newf = File(name, param=self.param, root=None)
    return newf

  def rename(self, chdict):
    self.param.df.rename(columns=chdict, inplace=True)

  def query(self, q):
    new = self.copy()
    new.param.df.query(q, inplace=True)
    return new

