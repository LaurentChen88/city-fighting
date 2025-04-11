import pandas as pd

# Lire le fichier CSV pour df_etablissement
df_etablissement = pd.read_csv("data/Etablissement.csv", sep=";")

# Convertir 'Code postal' en chaîne de caractères, si ce n'est pas déjà le cas
df_etablissement['Code postal'] = df_etablissement['Code postal'].astype(str)

# Extraire uniquement le département du code postal (les 2 premiers caractères)
df_etablissement['Departement2'] = df_etablissement['Code postal'].str[:2]

# Dictionnaire de correspondance entre les départements et les numéros de région en France (sans outre-mer)
departement_to_region_number = {
    '01': 84, '02': 32, '03': 84, '04': 93, '05': 93, '06': 93, '07': 84, '08': 44, '09': 76, '10': 44,
    '11': 76, '12': 76, '13': 93, '14': 28, '15': 84, '16': 75, '17': 75, '18': 24, '19': 75, '21': 27,
    '22': 53, '23': 75, '24': 75, '25': 27, '26': 84, '27': 28, '28': 24, '29': 53, '30': 76, '31': 76,
    '32': 76, '33': 75, '34': 76, '35': 53, '36': 24, '37': 24, '38': 84, '39': 27, '40': 75, '41': 24,
    '42': 84, '43': 84, '44': 52, '45': 24, '46': 76, '47': 75, '48': 76, '49': 52, '50': 28, '51': 44,
    '52': 44, '53': 52, '54': 44, '55': 44, '56': 53, '57': 44, '58': 27, '59': 32, '60': 32, '61': 28,
    '62': 32, '63': 84, '64': 75, '65': 76, '66': 76, '67': 44, '68': 44, '69': 84, '70': 27, '71': 27,
    '72': 52, '73': 84, '74': 84, '75': 11, '76': 28, '77': 11, '78': 11, '79': 75, '80': 32, '81': 76,
    '82': 76, '83': 93, '84': 93, '85': 52, '86': 75, '87': 75, '88': 44, '89': 27, '90': 27, '91': 11,
    '92': 11, '93': 11, '94': 11, '95': 11
}

# Créer la colonne 'Numéro Région' en utilisant le dictionnaire de correspondance
df_etablissement['Numéro Région'] = df_etablissement['Departement2'].map(departement_to_region_number)

# Remplacer les valeurs manquantes par une valeur par défaut (par exemple, 0)
df_etablissement['Numéro Région'].fillna(0, inplace=True)

# Convertir la colonne 'Numéro Région' en entiers
df_etablissement['Numéro Région'] = df_etablissement['Numéro Région'].astype(int)

# Garder uniquement les colonnes spécifiées
colonnes_a_garder = ['Numéro Région', 'libellé', 'nom court', 'secteur d\'établissement',
                     'Région', 'Departement2', 'Page Wikipédia en français']
df_etablissement = df_etablissement[colonnes_a_garder]

# Afficher le DataFrame mis à jour
print(df_etablissement)

# Décommenter pour sauvegarder le DataFrame dans un fichier CSV
df_etablissement.to_csv("data/etablissement_final.csv", index=False)
