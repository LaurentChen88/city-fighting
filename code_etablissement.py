import pandas as pd

# Lire le fichier CSV pour df_etablissement
df_etablissement = pd.read_csv("data/Etablissement.csv", sep=";")

# Convertir 'Code postal' en chaîne de caractères, si ce n'est pas déjà le cas
df_etablissement['Code postal'] = df_etablissement['Code postal'].astype(str)

# Extraire uniquement le département du code postal (les 2 premiers caractères)
df_etablissement['Code postal'] = df_etablissement['Code postal'].str[:2]

# Renommer la colonne 'Code postal' en 'Département'
df_etablissement.rename(columns={'Code postal': 'Région'}, inplace=True)

# Garder uniquement les colonnes spécifiées
df_etablissement = df_etablissement[['libellé', 'nom court', 'secteur d\'établissement', 
                                     'Région', 'Page Wikipédia en français']]

#df_etablissement.to_csv("data/etablissement2.csv", index=False)

df_etablissement.to_csv("data/etablissement2.csv", index=False)
