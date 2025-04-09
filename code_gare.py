import pandas as pd

# Chargement du fichier des gares
df_csv2 = pd.read_csv("data/gares-de-voyageurs.csv", sep=";")

# Renommer la colonne "Code commune" en "code_commune_INSEE"
df_csv2.rename(columns={'Code commune': 'code_commune_INSEE'}, inplace=True)

# Formater les codes INSEE sur 5 chiffres
df_csv2['code_commune_INSEE'] = df_csv2['code_commune_INSEE'].apply(lambda x: str(x).zfill(5))

# Séparer la colonne "Position géographique" en longitude et latitude
df_csv2[['longitude_gare', 'latitude_gare']] = df_csv2['Position géographique'].str.split(",", expand=True)

# Convertir les coordonnées en float
df_csv2['longitude_gare'] = df_csv2['longitude_gare'].astype(float)
df_csv2['latitude_gare'] = df_csv2['latitude_gare'].astype(float)

# Garder uniquement les colonnes nécessaires
df_gare_final = df_csv2[['code_commune_INSEE', 'longitude_gare', 'latitude_gare']]

# Aperçu des données des gares
print("Colonnes conservées :")
print(df_gare_final.head())

# Chargement de la base principale
df = pd.read_csv("data/data_final2.csv",sep=";")

# Jointure sur le code INSEE
df_jointure = pd.merge(df, df_gare_final, how='left', on='code_commune_INSEE')

# Aperçu du résultat
print("Résultat de la jointure :")
print(df_jointure.head())

df_jointure.to_csv("data/data_final3.csv", index=False)
