import pandas as pd 
df_final=pd.read_csv("data/data_final3.csv",sep=",")
df_final['code_commune_INSEE'] = df_final['code_commune_INSEE'].apply(lambda x: str(x).zfill(5))
print(df_final)