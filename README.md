# cellkey
Method applies noise to statistical tables.

Python solution for the Cell Key method, inspired by the 'cellkey' R package.<br>
The solution also utilizes the 'ptable' library, which is written in R.

## Usage
An example of how to use the method.
```python
from cellkey import CellKey

df = pd.read_csv("covid_munich_january_2023.csv")
ck = CellKey(df)
ck.add_row_key()
freq_table = ck.generate_frequency_table(["gender", "age_group"])
ck.generate_perturbation_table()
result = ck.apply_method(freq_table)
```
