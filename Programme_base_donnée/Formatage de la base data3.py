import pandas as pd 

# Import de la table data_final3 

df_final=pd.read_csv("data/data_final3.csv",sep=",")
df_final['code_commune_INSEE'] = df_final['code_commune_INSEE'].apply(lambda x: str(x).zfill(5))
print(df_final)

# Import de la table ajout de variable pour ajouter la variable code_departement pour faire la correspondance avec la table etablissement2 (variable Région2)
df_variable = pd.read_csv("data/ajout_variable.csv", sep=",")
df_filtre = df_variable[['code_departement','code_commune_INSEE','code_postal']]
df_filtre['code_commune_INSEE'] = df_filtre['code_commune_INSEE'].apply(lambda x: str(x).zfill(5))

print(df_filtre)


# Jointure gauche sur la colonne 'code_commune_INSEE'
df_jointure = pd.merge(df_final, df_filtre, how='left', on='code_commune_INSEE')

print(df_jointure)

#df_jointure.to_csv("data/data_final4.xlsx", index=False)