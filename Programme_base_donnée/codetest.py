import requests

def get_weather(city_name, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric',
        'lang': 'fr'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Déclenche une erreur si le code HTTP est 4xx/5xx
        data = response.json()

        if "main" in data and "weather" in data:
            print(f"📍 Météo à {data['name']}")
            print(f"🌡️ Température : {data['main']['temp']}°C")
            print(f"🤔 Ressentie : {data['main']['feels_like']}°C")
            print(f"🌤️ Conditions : {data['weather'][0]['description']}")
        else:
            print("⚠️ Données météo incomplètes.")
    
    except requests.exceptions.HTTPError as err:
        print("❌ Erreur HTTP :", err)
    except requests.exceptions.RequestException as err:
        print("❌ Erreur de requête :", err)
    except Exception as e:
        print("❌ Erreur inattendue :", e)

# 🔑 Ta clé API
API_KEY = "6aea17a766b369d16fdcf84a0b16fdac"
VILLE = "Paris"

get_weather(VILLE, API_KEY)
