import pandas as pd

# Charger le CSV
df_csv = pd.read_csv("data/ajout_variable.csv")
df_csv['code_commune_INSEE'] = df_csv['code_commune_INSEE'].apply(lambda x: str(x).zfill(5))

# Charger le fichier Excel
df_xlsx = pd.read_excel("data/base_cc_comparateur.xlsx")
df_xlsx['CODGEO'] = df_xlsx['CODGEO'].apply(lambda x: str(x).zfill(5))

# Renommer la colonne pour correspondre
rename_df = df_xlsx.rename(columns={'CODGEO': 'code_commune_INSEE'})

# Garder seulement les colonnes nécessaires du CSV
df_filtre = df_csv[['code_commune_INSEE', 'latitude', 'longitude']]

# Jointure gauche sur la colonne 'code_commune_INSEE'
df_jointure = pd.merge(rename_df, df_filtre, how='left', on='code_commune_INSEE')

# Aperçu des premières lignes
print(df_jointure.head())

# Enregistrer le résultat dans un fichier Excel
df_jointure.to_excel("data/data_final.xlsx", index=False)




############################## PARTIE GARE #######################################

df_csv2 = pd.read_csv("data/gares-de-voyageurs.csv")
# Renommer la colonne pour correspondre
df_csv2_rename = df_csv2.rename(columns={'CODGEO': 'code_commune_INSEE'})

print("La base de gare ==========>")
print(df_csv2_rename.head())
