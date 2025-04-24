import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st

# Fonction pour récupérer les données touristiques à l'aide de l'API Overpass
def get_tourisme_data(bbox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["tourism"]({bbox});
      way["tourism"]({bbox});
      relation["tourism"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.get(overpass_url, params={'data': overpass_query}, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Fonction pour obtenir les coordonnées géographiques d'une ville à partir de son code INSEE
def get_coordinates_from_insee(code_insee):
    # Utiliser l'API Geocoding de l'IGN pour obtenir les coordonnées
    url = f"https://api-adresse.data.gouv.fr/search/?q={code_insee}&type=municipality&autocomplete=0"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            return coords[1], coords[0]  # Latitude, Longitude
    return None, None

# Exemple de codes INSEE (vous pouvez remplacer par vos propres codes INSEE)
codes_insee = ['75056', '13055', '69123']  # Exemple de codes INSEE pour Paris, Marseille, Lyon

# Récupérer les coordonnées géographiques pour chaque code INSEE
coordinates = {}
for code_insee in codes_insee:
    lat, lon = get_coordinates_from_insee(code_insee)
    if lat and lon:
        coordinates[code_insee] = (lat, lon)

# Récupérer les données touristiques pour chaque code INSEE
tourisme_data = []
for code_insee, (lat, lon) in coordinates.items():
    bbox = f"{lat-0.1},{lon-0.1},{lat+0.1},{lon+0.1}"  # Définir une boîte englobante autour des coordonnées
    data = get_tourisme_data(bbox)
    if data:
        for element in data['elements']:
            if 'lat' in element and 'lon' in element:
                tourisme_data.append({
                    'code_insee': code_insee,
                    'name': element.get('tags', {}).get('name', 'N/A'),
                    'tourism': element.get('tags', {}).get('tourism', 'N/A'),
                    'latitude': element['lat'],
                    'longitude': element['lon']
                })

# Convertir les données en DataFrame
df_tourisme = pd.DataFrame(tourisme_data)


