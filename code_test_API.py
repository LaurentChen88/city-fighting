import requests

def get_city_photos(city_name, api_key):
    url = f"https://api.unsplash.com/search/photos"
    params = {
        'query': city_name,
        'client_id': api_key,
        'per_page': 5  # Nombre d'images à récupérer
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Déclenche une erreur si le code HTTP est 4xx/5xx
        data = response.json()

        if "results" in data:
            print(f"📸 Photos de {city_name}:")
            for index, photo in enumerate(data["results"]):
                print(f"Photo {index + 1}:")
                print(f"URL de l'image: {photo['urls']['regular']}")
                print(f"Photographe: {photo['user']['name']}")
                print(f"Description: {photo['alt_description']}")
                print("-" * 50)
        else:
            print(f"⚠️ Aucune photo trouvée pour {city_name}.")

    except requests.exceptions.HTTPError as err:
        print("❌ Erreur HTTP :", err)
    except requests.exceptions.RequestException as err:
        print("❌ Erreur de requête :", err)
    except Exception as e:
        print("❌ Erreur inattendue :", e)

# Ta clé API Unsplash
API_KEY = "2_paTq4anmtqT_ZY38WLHENxJ9hP_EhcJsWI8kxGTO8"
ville = "Paris"  # Remplace "Paris" par la ville de ton choix

get_city_photos(ville, API_KEY)
