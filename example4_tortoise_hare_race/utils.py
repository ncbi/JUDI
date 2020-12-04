
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

        print("In instance for: \n", self.dataframe)
        print(wildcards.items())


        return {
            name: pd.Series([value]).astype(self.dataframe.dtypes[name])
            for name in wildcards.items()
            if name in self.dataframe.columns
        }

    def __getattr__(self, name):
        import pandas as pd

        ret = getattr(self.dataframe, name)
        if isinstance(ret, pd.DataFrame):
            return Paramspace(ret)
        return ret

    def __getitem__(self, key):
        import pandas as pd

        ret = self.dataframe[key]
        if isinstance(ref, pd.DataFrame):
            return Paramspace(ret)
        return ret

