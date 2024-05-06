from cellkey import CellKey

df = pd.read_csv("covid_munich_january_2023.csv")
print("Original data:\n",df.head(10))
ck = CellKey(df)
ck.add_row_key()
freq_table = ck.generate_frequency_table(["gender", "age_group"])
ck.generate_perturbation_table()
result = ck.apply_method(freq_table)
print("with cellkey:\n",result)
