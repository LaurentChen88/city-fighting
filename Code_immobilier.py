import pandas as pd 

df_immobilier=pd.read_csv("data/immobilier.csv",sep=",")

print(df_immobilier.columns())