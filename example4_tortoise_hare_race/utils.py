
class Paramspace:
    """A wrapper for pandas dataframes that provides helpers for using them as a parameter
    space in Snakemake.
    This is heavily inspired by @soumitrakp work on JUDI (https://github.com/ncbi/JUDI).
    """

    def __init__(self, dataframe):
        self.dataframe = dataframe

    @property
    def wildcard_pattern(self):
        """Wildcard pattern over all columns of the underlying dataframe of the form
        column1~{column1}/column2~{column2}/***
        """
        return "/".join(map("{0}~{{{0}}}".format, self.dataframe.columns))

    @property
    def instance_patterns(self):
        """Iterator over all instances of the parameter space (dataframe rows),
        formatted as file patterns of the form column1~{value1}/column2~{value2}/...
        """
        return (
            "/".join("{}~{}".format(name, value) for name, value in row.items())
            for index, row in self.dataframe.iterrows()
        )

    def instance(self, wildcards):
        """Obtain instance (dataframe row) with the given wildcard values."""
        import pandas as pd

        return {
            name: pd.Series([value]).astype(self.dataframe.dtypes[name])
            for name in wildcards.items()
            if name in self.dataframe.columns
        }

    def partially_expanded_patterns(self, wildcards):
        """Iterator over all instances of the parameter space (dataframe rows),
        that are filtered by the wildcards values, formatted as file patterns
        of the form column1~{z1}/column2~{z2}/... where z1 is {column1} if
        column1 is in wildscards, otherwise value1
        """
        fixed = {name:value for name, value in wildcards.items()
                 if name in self.dataframe.columns}
        qstring = '&'.join(f"({name} == {value})"
                           for name, value in fixed.items())
        tmp_dataframe = (self.dataframe if not qstring else
                         self.dataframe.query(qstring))
        return (
            "/".join(f"{name}~{{{name}}}" if name in fixed else
                     f"{name}~{value}"  for name, value in row.items())
            for index, row in tmp_dataframe.iterrows()
        )


    #def __getattr__(self, name):
    #    import pandas as pd

    #    ret = getattr(self.dataframe, name)
    #    if isinstance(ret, pd.DataFrame):
    #        return Paramspace(ret)
    #    return ret

    #def __getitem__(self, key):
    #    import pandas as pd

    #    ret = self.dataframe[key]
    #    if isinstance(ref, pd.DataFrame):
    #        return Paramspace(ret)
    #    return ret

class Filespace:

    def __init__(self, fname, paramspace, topdir = '', name = None):
        import os

        self.paramspace = paramspace
        self.fname = fname
        name = name or os.path.splitext(fname)[0]
        self.basedir = f"{topdir}/{name}" if topdir else name

    def expand_wildcards(self, wildcards):
        if wildcards is None:
            return "/".join([self.basedir,
                             self.paramspace.wildcard_pattern,
                             self.fname])
        return (
            "/".join([self.basedir, pattern, self.fname])
            for pattern in self.paramspace.partially_expanded_patterns(wildcards)
        )

    @property
    def expand(self):
        return self.expand_wildcards({})

    def __call__(self, wildcards=None):
        return self.expand_wildcards(wildcards)

