import pandas as pd
from rpy2.robjects.packages import importr
import pandas as pd
import numpy as np

# Name of the R package you want to use
ptable = importr('ptable')

class CellKey:
    """
    CellKey class represents the the CKM proposed by the Australian Bureau of Statistics (ABS) (Leaver and Marley 2011).

    Attributes
    ----------

    df : pandas df
        input table.

    perturbation_table : pandas df (optional)
        perturbation table.
    """
    def __init__(self, df, perturbation_table = None ):
         self.df = df
         self.perturbation_table = perturbation_table

    def generate_frequency_table(self, list_of_features):
        """
        Generates freqency table.

        Attributes
        ----------

        list_of_features : list
            list of column names that will be grouped in order to generate frequency table.

        Returns
        -------
        freq_table: pandas df
            frequency table.
        """
        count_df = self.df.groupby(list_of_features).size().reset_index(name='count')  # Count occurrences
        count_df['ckeys'] = self.df.groupby(list_of_features)['rkeys'].sum().reset_index(drop=True)  # Sum 'record keys'
        count_df['ckeys'] = count_df['ckeys'].apply(lambda x: x % 1)
        freq_table = pd.pivot_table(count_df,
                                    index=list_of_features,
                                    values=['count', 'ckeys'], 
                                    aggfunc={'count': 'sum', 'ckeys': 'sum'},
                                    fill_value=0,
                                    dropna=False).reset_index()
        return freq_table
        
    def add_row_key(self, nr_digits=7, seed=123):
        """
        Generates row key.

        Attributes
        ----------

        nr_digits : int
            number of digits in row keys

        seed : int
            initial value for random number generation.
        """
        if seed is not None:
            if not isinstance(seed, int):
                raise ValueError("`seed` must be an integer.")
        else:
            seed = 123

        if not isinstance(nr_digits, int):
            raise ValueError("`nr_digits` is not an integer.")
        if nr_digits < 5:
            raise ValueError("`nr_digits` must be >= 5.")
        if nr_digits > 20:
            raise ValueError("`nr_digits` must be <= 20.")
        
        np.random.seed(seed)
        rkeys = np.round(np.random.uniform(0, 1, size=len(self.df)), nr_digits)

        self.df['rkeys'] = rkeys

    def generate_perturbation_table(self, D = 4, V = 3, js = 2, pstay = 0.5, optim = 1, mono = True):
        """
        Generates perturbation table with the function create_ptable from R package ptable.

        Attributes
        ----------
        D : int
            max perturbation value.

        V : int
            varience.

        js : int
            threshold value for blocking of small frequencies (i.e. the perturbation will not produce positive cell values that are equal to or smaller than the threshold value).

        pstay : int
            optional parameter to set the probability (0 < p < 1) of an original frequency to remain unperturbed.

        optim : int
            optimization parameter: 1 standard approach (default) with regular constraints, 4 alternative approach with simplified constraints (may work if constraints using the standard approach are violated).

        mono : bool
            (logical) vector specifying optimization parameter for monotony condition.

        """
        D = 8
        V = 7
        js = 4
        ptab = ptable.create_ptable(D = D, V = V, js = js, pstay = pstay, optim = optim, mono = mono, table = 'cnts').do_slot("pTable")
        self.perturbation_table = pd.DataFrame(ptab).T
        self.perturbation_table = self.perturbation_table.rename(columns={0: 'i', 1: 'j', 2: 'p', 3: 'v', 4: 'p_lb', 5: 'p_ub'})

    def apply_method(self, freq_table):
        """
        Applies perturbation to the given frequency table.

        Attributes
        ----------

        freq_table: pandas df
            frequency table.

        Returns
        -------
        freq_table: pandas df
            perturbated frequency table.
        """
        for index, row_f in freq_table.iterrows():
            count = row_f['count']
            i = min(count, max(self.perturbation_table['i']))
            p_i = self.perturbation_table.loc[self.perturbation_table['i'] == i]
            
            # Find the row where 'cell_key' falls within the range specified by 'p_lb' and 'p_ub'
            matching_row = p_i[(p_i['p_lb'] <= row_f['ckeys']) & (row_f['ckeys'] < p_i['p_ub'])]
            if not matching_row.empty:
                freq_table.at[index, 'count'] = count + matching_row['v'].values[0]
            
        freq_table.drop('ckeys', axis=1, inplace=True)
        return freq_table
    

df = pd.read_csv("covid_de.csv")
print("Original data:\n",df.head(10))
ck = CellKey(df)
ck.add_row_key()
freq_table = ck.generate_frequency_table(["gender", "age_group"])
ck.generate_perturbation_table()
result = ck.apply_method(freq_table)
print("with cellkey:\n",result)