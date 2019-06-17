import pandas as pd

class ParamDb(object):
  """Parameter database"""
  def __init__(self, name=''):
    self.name = name
    self.df = pd.DataFrame({'JUDI': ['*']})

  def add_param(self, param_info, name=None):
    if isinstance(param_info, list):
      param_info = {name: param_info}
    if isinstance(param_info, dict):
      param_info = pd.DataFrame(param_info)
    if isinstance(param_info, pd.Series):
      param_info = pd.DataFrame([param_info])
    if not isinstance(param_info, pd.DataFrame):
      print("Error! input data must be a list, series or dataframe!!!")
      return 1
    self.df = self.df.assign(key=1).merge(param_info.assign(key=1), on='key', how='outer').drop('key', 1)

  def copy(self, name=''):
    other = ParamDb(name)
    other.df = self.df.copy()
    return other

  def mask(self, mask_cols):
    self.df = self.df.drop(mask_cols, 1).drop_duplicates()

  def filter(self, name, values):
    self.df = self.df[self.df[name].isin(values)]

  def sort_columns(self, cols):
    print(cols)
    self.df = self.df.set_index(cols).sort_index().reset_index()

  def show(self):
    print(self.name, ':')
    if 'JUDI' in self.df.columns:
      print(self.df.drop('JUDI', 1))
    else:
      print(self.df)
    

JUDI_PARAM = ParamDb("global pdb")

def add_param(param_info, name = None):
  """Add a parameter or a group of parameters in the global parameter database

  Args:
     param_info (list/dict/Pandas Series/DataFrame): Information about the parameter or group of parameters.
     If not already so, param_info is converted to a pandas DataFrame and then it is added to the global
     parameter database via a Cartesian product.

  Kwargs:
     name (str): Used if param_info is a list and denotes the name of the parameter.

  Returns:
     int.  The return code: 0 for success and 1 for error!

  Raises:
     None
  """
  JUDI_PARAM.add_param(param_info, name)
  return 0

def remove_params(cols):
  JUDI_PARAM.mask(cols)

def show_param_db():
  """Print the global parameter database
  """
  JUDI_PARAM.show()


def filter_param_vals(param, values):
  JUDI_PARAM.filter(param, values)


def copy_param_db():
  return JUDI_PARAM.copy()


def mask_global_param_db(mask_cols):
  param = JUDI_PARAM.copy()
  masked = JUDI_PARAM.copy()
  param_cols = list(set(param.columns) - set(mask_cols))
  param = param.drop(mask_cols, 1).drop_duplicates()
  masked = masked.drop(param_cols, 1).drop_duplicates()
  return(param, masked)


def mask_param_db(param_db, mask_cols):
  pdb = param_db.copy()
  pdb = pdb.drop(mask_cols, 1).drop_duplicates()
  return pdb


def param_diff(big, small):
  diff_cols = list(set(big.param.columns) - set(small.param.columns))
  return big.param[diff_cols].drop_duplicates()


