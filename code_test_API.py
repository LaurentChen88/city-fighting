import requests

def get_navitia_stops(city_name, api_key, lon, lat, distance=500):
    url = "https://api.navitia.io/v1/coverage/fr-idf/places"
    params = {
        'q': f"coord:{lon}:{lat}",
        'type[]': 'stop_point',
        'distance': distance,
        'count': 10
    }
    headers = {
        'Authorization': api_key
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()

        if 'places' in data:
            print(f"Arrêts de transport à proximité de {city_name} :")
            for place in data['places']:
                print(f"- {place['name']} (Distance : {place['distance']} m)")
        else:
            print("Aucun arrêt trouvé.")

    except requests.exceptions.HTTPError as err:
        print("Erreur HTTP :", err)
    except requests.exceptions.RequestException as err:
        print("Erreur de requête :", err)
    except Exception as e:
        print("Erreur inattendue :", e)

# Exemple d'utilisation
API_KEY = "VOTRE_CLE_API_NAVITIA"
VILLE = "Paris"
LON = 2.3522  # Longitude de Paris
LAT = 48.8566  # Latitude de Paris

get_navitia_stops(VILLE, API_KEY, LON, LAT)
