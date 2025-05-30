import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster
from collections import defaultdict, Counter
import plotly.graph_objects as go
from datetime import datetime
from meteostat import Point, Daily
import matplotlib.pyplot as plt
import os

# Configuration de la page
st.set_page_config(
    page_title="City Fighting",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre
st.title("🏙️ City Fighting - Comparateur de villes en France")

# Initialisation du géolocaliseur
geolocator = Nominatim(user_agent="mon_application")

# Chargement des données
file_path = "data/data_final.xlsx"
etablissement_path = "data/etablissement_final.csv"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

@st.cache_data
def load_etablissement_data(path):
    return pd.read_csv(path)

# Fonction pour obtenir la météo
# L'API OpenWeather renvoie les prévisions horaires pour 5 jours avec un intervalle de 3 heures
@st.cache_data
def get_weather(city_name, latitude=None, longitude=None):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    # Tentative avec le nom de la ville
    params = {
        'q': city_name,
        'appid': "6aea17a766b369d16fdcf84a0b16fdac",
        'units': 'metric',
        'lang': 'fr'
    }

    try:
        # Première tentative avec le nom de la ville
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        st.write(f"📍 Météo à {data['city']['name']}")
    except requests.exceptions.HTTPError:
        # Si le nom de la ville échoue, basculer sur les coordonnées
        if latitude is not None and longitude is not None:
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': "6aea17a766b369d16fdcf84a0b16fdac",
                'units': 'metric',
                'lang': 'fr'
            }
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                st.write(f"📍 Météo à {data['city']['name']}")
            except Exception as e:
                st.error(f"❌ Erreur lors de la récupération des données météo via coordonnées : {e}")
                return
        else:
            st.error(f"❌ Nom de la ville non reconnu et coordonnées manquantes pour {city_name}.")
            return
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {e}")
        return

    # Grouper les prévisions par date
    daily_data = defaultdict(list)
    for forecast in data['list']:
        dt = pd.to_datetime(forecast['dt_txt'])
        daily_data[dt.date()].append(forecast)

    # Stocker les données de température pour le graphique global
    temperature_data = []

    for date, forecasts in daily_data.items():
        # Convertir la date dans daily_data en string au format 'YYYY-MM-DD'
        date_obj = pd.to_datetime(date).strftime('%Y-%m-%d')  # Convertir en string pour la comparaison
        day_name = pd.to_datetime(date).strftime('%A %d/%m')  # Définir day_name à partir de la date

        # Températures et conditions des prévisions horaires
        temps = [f['main']['temp'] for f in forecasts]
        conditions_en = [f['weather'][0]['main'] for f in forecasts]
        conditions_fr = [f['weather'][0]['description'] for f in forecasts]
        icons = [f['weather'][0]['icon'] for f in forecasts]

        # Température actuelle uniquement pour aujourd'hui
        current_date = datetime.today().strftime('%Y-%m-%d')  # Date actuelle au format 'YYYY-MM-DD'

        # Vérification si la date correspond à aujourd'hui (en s'assurant que les deux valeurs sont des strings)
        if date_obj == current_date:
            current_temp = int(temps[0])  # La première température des prévisions horaires correspond à la température actuelle
        else:
            current_temp = None  # Pas de température actuelle pour les autres jours

        # Température minimale et maximale pour la journée (pour tous les jours)
        temp_min = int(min(temps))
        temp_max = int(max(temps))

        # Condition météorologique majoritaire
        condition_majoritaire_en = Counter(conditions_en).most_common(1)[0][0]
        condition_majoritaire_fr = Counter(conditions_fr).most_common(1)[0][0]
        icon_majoritaire = Counter(icons).most_common(1)[0][0]
        icon_url = f"http://openweathermap.org/img/wn/{icon_majoritaire}@2x.png"

        # Vitesse du vent pour le jour
        wind_speed = sum(f['wind']['speed'] for f in forecasts) / len(forecasts)  # Moyenne des vitesses du vent sur la journée en m/s
        wind_speed_kmh = wind_speed * 3.6  # Conversion m/s en km/h

        avg_humidity = round(sum(f['main']['humidity'] for f in forecasts) / len(forecasts))  # Moyenne de l'humidité
        avg_pressure = round(sum(f['main']['pressure'] for f in forecasts) / len(forecasts))  # Moyenne de la pression

        # Emoji correspondant à la condition météorologique
        weather_emojis = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️",
            "Smoke": "💨",
            "Dust": "🌪️",
            "Sand": "🏜️",
            "Ash": "🌋",
            "Squall": "🌬️",
            "Tornado": "🌪️"
        }

        # Choisir l'emoji en fonction de la condition météo majoritaire
        emoji = weather_emojis.get(condition_majoritaire_en, "🌈")

        # Affichage dans les colonnes
        col1, col2, col3 = st.columns([3, 1, 2])
        col1.markdown(f"### 📅 {day_name}")
        col2.image(icon_url, width=60)  # Icône OpenWeather

        # Si c'est aujourd'hui, affiche la température actuelle
        if current_temp is not None:
            wind_speed = forecasts[0]['wind']['speed']  # Vitesse du vent en m/s
            col3.markdown(f"🌡️ Température actuelle : **{current_temp}°C**  \n{emoji} **{condition_majoritaire_fr}**")
        else:
            col3.markdown(f"🔼 Max : **{temp_max}°C**  \n🔽 Min : **{temp_min}°C**  \n{emoji} **{condition_majoritaire_fr}**")

        # Détail graphique avec bouton
        with st.expander("➕ Détails"):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"💨 Vent : **{wind_speed_kmh:.1f} km/h**")
            col2.markdown(f"💧 Humidité : **{avg_humidity}%**")
            col3.markdown(f"🌡️ Pression : **{avg_pressure} hPa**")

            heures = [pd.to_datetime(f['dt_txt']).strftime('%H:%M') for f in forecasts]
            temp_h = [round(f['main']['temp']) for f in forecasts]  # Arrondir la température

            # Création du graphique avec Plotly
            fig = go.Figure()

            # Ajout des points avec tooltips
            fig.add_trace(go.Scatter(
                x=heures,
                y=temp_h,
                mode='markers+lines',
                marker=dict(color='royalblue', size=8),
                text=[f"Temps: {t}°C" for t in temp_h],  # Tooltip avec la température
                hoverinfo='text',  # Affichage uniquement du texte
            ))

            # Titre et labels avec une meilleure mise en forme
            fig.update_layout(
                title=f'Température - {day_name}',
                title_x=0.5,
                title_font=dict(size=16, family='Arial', color='darkslategray'),
                xaxis_title='Heure',
                yaxis_title='Température (°C)',
                xaxis=dict(
                    tickangle=45,
                    showgrid=False,  # Retirer les lignes de grille sur l'axe X
                ),
                yaxis=dict(
                    showgrid=False,  # Retirer les lignes de grille sur l'axe Y
                ),
                template="plotly_white",  # Thème clair sans grille
                height=500,
                plot_bgcolor='white',  # Enlever le fond de la grille
            )

            # Uniformiser l'échelle des graphiques
            fig.update_yaxes(range=[-10, 40])  # Exemple de plage de température

            # Affichage du graphique interactif
            st.plotly_chart(fig)

            # Séparateur
            st.markdown("---")

        # Ajouter les données de température pour le graphique global
        for forecast in forecasts:
            temperature_data.append({
                'city': city_name,
                'date': pd.to_datetime(forecast['dt_txt']),
                'temp': forecast['main']['temp']
            })

    return temperature_data

# Fonction générique pour récupérer les données des points d'intérêt (gares, musées, restaurants, etc.) à l'aide de l'API Overpass
@st.cache_data
def get_overpass_data(bbox, key, value):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["{key}"="{value}"]({bbox});
      way["{key}"="{value}"]({bbox});
      relation["{key}"="{value}"]({bbox});
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

def display_poi_with_cluster(m, poi_data, icon_color):
    cluster = MarkerCluster().add_to(m)
    for element in poi_data['elements']:
        if 'lat' in element and 'lon' in element and 'name' in element.get('tags', {}):
            folium.Marker(
                location=[element['lat'], element['lon']],
                popup=element.get('tags', {}).get('name', 'N/A'),
                icon=folium.Icon(color=icon_color)
            ).add_to(cluster)

# Fonction pour récupérer la latitude et longitude
@st.cache_data
def get_coordinates(city_name):
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Erreur lors de la récupération des coordonnées pour {city_name}: {e}")
        return None, None

# Fonction pour récupérer la population à partir du code INSEE
def get_population_by_insee(insee_code):
    url = f"https://geo.api.gouv.fr/communes/{insee_code}?fields=nom,code,population"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête: {e}")
        return None
    except ValueError as e:
        print(f"Erreur lors du décodage JSON: {e}")
        return None

# Vérifier si les coordonnées manquent et les récupérer si nécessaire
def update_coordinates(df, city_name):
    row_index = df[df["Libellé commune ou ARM"] == city_name].index
    if not row_index.empty:
        row_index = row_index[0]
        if pd.isna(df.at[row_index, 'longitude']) or pd.isna(df.at[row_index, 'latitude']):
            latitude, longitude = get_coordinates(city_name)
            if latitude is not None and longitude is not None:
                df.at[row_index, 'latitude'] = latitude
                df.at[row_index, 'longitude'] = longitude

        # Vérifier et mettre à jour la population
        if 'code_commune_INSEE' in df.columns:
            insee_code = df.at[row_index, 'code_commune_INSEE']
            population_data = get_population_by_insee(insee_code)
            if population_data and 'population' in population_data:
                df.at[row_index, 'Population'] = population_data['population']

def create_comparison_graph(city_data_list, metrics, city_names):
    """
    Crée un graphique comparatif basé sur les métriques fournies pour plusieurs villes.

    :param city_data_list: Liste des données des villes
    :param metrics: Dictionnaire des métriques (clé: label, valeur: (colonne, unité))
    :param city_names: Liste des noms des villes
    :return: Graphique Plotly
    """
    # Initialisation du DataFrame
    df_data = {
        "Variable": list(metrics.keys())  # Utilise les labels des métriques
    }

    # Ajout des valeurs originales pour chaque ville
    for i, (data, name) in enumerate(zip(city_data_list, city_names)):
        df_data[f"{name}_original"] = [pd.to_numeric(data[column], errors='coerce') for column, _ in metrics.values()]

    # Création du DataFrame
    graphe_data = pd.DataFrame(df_data)

    # Remplacer les valeurs NaN par 0 pour éviter les erreurs dans les calculs
    graphe_data.fillna(0, inplace=True)

    # Normalisation des valeurs pour chaque variable
    for var_idx in range(len(metrics)):
        total = sum(graphe_data.iloc[var_idx][f"{name}_original"] for name in city_names)
        if total > 0:  # Éviter division par zéro
            for name in city_names:
                graphe_data.at[var_idx, name] = graphe_data.iloc[var_idx][f"{name}_original"] / total
        else:
            for name in city_names:
                graphe_data.at[var_idx, name] = 0

    # Arrondir les colonnes normalisées
    for name in city_names:
        graphe_data[name] = graphe_data[name].round(2)

    # Transformation pour le graphe
    id_vars = ["Variable"] + [f"{name}_original" for name in city_names]
    graphe_data = graphe_data.melt(
        id_vars=id_vars,
        value_vars=city_names,
        var_name="Ville",
        value_name="Valeur"
    )

    # Ajouter une colonne pour les valeurs originales dans le hover
    graphe_data["Valeur_originale"] = graphe_data.apply(
        lambda row: row[f"{row['Ville']}_original"], axis=1
    ).round(2)

    # Création du graphe
    fig = px.bar(
        graphe_data,
        x="Variable",
        y="Valeur",
        color="Ville",
        barmode="group",
        title="📉 Comparatif des indicateurs clés (normalisé)",
        hover_data={
            "Valeur_originale": True,
            "Valeur": True,
            "Variable": True,
            "Ville": True
        }
    )
    return fig

# Fonction pour afficher les points d'intérêt sur la carte
def display_poi_on_map(m, bbox, poi_key, poi_type, icon_color):
    poi_data = get_overpass_data(bbox, poi_key, poi_type)
    if poi_data:
        display_poi_with_cluster(m, poi_data, icon_color)

# Fonction générique pour afficher les points d'intérêt
def display_poi(city_name, data, poi_options):
    st.markdown(f"### {city_name}")

    # Afficher la carte
    if "latitude" in data and "longitude" in data:
        m = folium.Map(location=[data["latitude"], data["longitude"]], zoom_start=12)
        folium.Marker(
            location=[data["latitude"], data["longitude"]],
            popup=city_name,
            tooltip=city_name,
            icon=folium.Icon(color="blue")
        ).add_to(m)

        # Récupérer et afficher les points d'intérêt
        bbox = f"{data['latitude']-0.1},{data['longitude']-0.1},{data['latitude']+0.1},{data['longitude']+0.1}"
        if "Gares" in poi_options:
            display_poi_on_map(m, bbox, "railway", "station", "cadetblue")
        if "Musées" in poi_options:
            display_poi_on_map(m, bbox, "tourism", "museum", "purple")
        if "Restaurants" in poi_options:
            display_poi_on_map(m, bbox, "amenity", "restaurant", "orange")
        if "Centres sportifs" in poi_options:
            display_poi_on_map(m, bbox, "leisure", "sports_centre", "green")
        if "Cinémas et Théâtres" in poi_options:
            display_poi_on_map(m, bbox, "amenity", "cinema", "red")
            display_poi_on_map(m, bbox, "amenity", "theatre", "darkpurple")
        if "Banques et Distributeurs" in poi_options:
            display_poi_on_map(m, bbox, "amenity", "bank", "gray")
            display_poi_on_map(m, bbox, "amenity", "atm", "lightgray")
        if "Hôpitaux et Cliniques" in poi_options:
            display_poi_on_map(m, bbox, "amenity", "hospital", "pink")
            display_poi_on_map(m, bbox, "amenity", "clinic", "lightred")
        if "Sécurité" in poi_options:
            display_poi_on_map(m, bbox, "amenity", "police", "darkblue")
            display_poi_on_map(m, bbox, "amenity", "fire_station", "darkred")

        st_folium(m, width=700, height=400)
    else:
        st.warning("Données géographiques manquantes pour cette ville.")

# Fonction générique qui prend en paramètre les métriques à afficher et les données associées
def display_metrics(data, city_name, metrics, wiki_url=False):
    """
    Affiche des métriques génériques pour une ville.

    :param data: Données de la ville
    :param city_name: Nom de la ville
    :param metrics: Dictionnaire des métriques à afficher (clé: label, valeur: (colonne, unité))
    :param wiki_url: URL de la page Wikipédia (facultatif)
    """
    st.markdown(f"### {city_name}")

    # Afficher le lien Wikipédia si fourni
    if wiki_url:
        wiki_url = f"https://fr.wikipedia.org/wiki/{city_name.replace(' ', '_')}"
        st.markdown(f"🔗 [Page Wikipédia de {city_name}]({wiki_url})")

    for label, (column, unit) in metrics.items():
        value = pd.to_numeric(data[column], errors='coerce')
        if not pd.isna(value):
            formatted_value = f"{int(value):,}".replace(",", " ")  # Formatage avec des espaces
            st.metric(label, f"{formatted_value} {unit}".strip())  # Ajout de l'unité
        else:
            st.warning(f"Donnée manquante pour {label.lower()} de cette ville.")

# Fonction générique pour afficher les formations
def display_formation(city_name, data, df_etablissement):
    st.markdown(f"### {city_name}")
    ecoles = df_etablissement[df_etablissement['Numéro Région'] == data['Région']]

    # Afficher la carte
    if not ecoles.empty:
        # Initialisation de la carte
        m_ecoles = folium.Map(location=[ecoles.iloc[0]['latitude_ecole'], ecoles.iloc[0]['longitude_ecole']], zoom_start=12)

        # Cluster des marqueurs
        cluster = MarkerCluster().add_to(m_ecoles)

        for _, ecole in ecoles.iterrows():
            folium.Marker(
                location=[ecole['latitude_ecole'], ecole['longitude_ecole']],
                popup=ecole['libellé'],
                icon=folium.Icon(color="green")
            ).add_to(cluster)

        # Affichage avec Streamlit
        st_folium(m_ecoles, width=700, height=500, key=f"map_{city_name}")
    else:
        st.warning("Aucune école trouvée pour cette ville.")

    # Afficher le tableau des écoles avec des colonnes spécifiques
    colonnes_a_afficher = ['libellé', 'nom court', "secteur d'établissement", 'Région', 'Page Wikipédia en français']
    ecoles_reduites = ecoles[colonnes_a_afficher] if not ecoles.empty else pd.DataFrame(columns=colonnes_a_afficher)
    st.dataframe(ecoles_reduites.reset_index(drop=True), key=f"table_{city_name}")

# Fonction pour récupérer et afficher les données météorologiques saisonnières
def display_seasonal_weather(city_name, latitude, longitude):
    st.subheader(f"Données météorologiques saisonnières pour {city_name}")

    # 📍 Coordonnées de la ville
    location = Point(latitude, longitude)

    # 🗓️ Période
    start = pd.to_datetime('1990-01-01')
    end = pd.to_datetime('2020-12-31')

    # 📊 Récupérer données journalières
    data = Daily(location, start, end).fetch()
    data = data.dropna(subset=['tavg'])

    # 🎯 Fonctions pour classer les dates par saison
    def get_season(date):
        Y = 2000
        date_fixed = date.replace(year=Y)
        if pd.Timestamp(f"{Y}-03-21") <= date_fixed <= pd.Timestamp(f"{Y}-06-20"):
            return 'Printemps'
        elif pd.Timestamp(f"{Y}-06-21") <= date_fixed <= pd.Timestamp(f"{Y}-09-22"):
            return 'Été'
        elif pd.Timestamp(f"{Y}-09-23") <= date_fixed <= pd.Timestamp(f"{Y}-12-20"):
            return 'Automne'
        else:
            return 'Hiver'

    data['season'] = data.index.map(get_season)
    data['year'] = data.index.year

    # 📊 Moyenne par saison et par année
    seasonal_avg = data.groupby(['year', 'season'])['tavg'].mean().unstack()

    # 🔢 Moyenne globale sur 1990–2020
    seasonal_means = seasonal_avg.mean()

    # 📋 Affichage du tableau
    st.write("\n📌 Moyenne globale sur 30 ans par saison:")
    st.write(seasonal_means.round(2))

    # 📈 Graphique
    plt.figure(figsize=(12, 6))
    for season in seasonal_avg.columns:
        plt.plot(seasonal_avg.index, seasonal_avg[season], label=season)
        plt.axhline(seasonal_means[season], linestyle='--', label=f'{season} moyenne ({seasonal_means[season]:.1f}°C)')

    # Fixer l'échelle de l'axe Y
    plt.ylim(-5, 30)  # Exemple : de -5°C à 30°C

    plt.title(f"Évolution des températures saisonnières à {city_name} (1990–2020)")
    plt.xlabel("Année")
    plt.ylabel("Température moyenne (°C)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)


def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return "Date invalide"

# --- Étape 1 : Récupérer dynamiquement le token ---
def get_access_token(client_id, client_secret):
    url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "api_offresdemploiv2 o2dsoffre"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        st.error(f"Erreur lors de la récupération du token : {response.status_code} - {response.text}")
        return None

# --- Étape 2 : Appeler l'API des offres ---
def get_job_offers(query, departement, access_token, type_contrat=None, publiee_depuis=None):
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'motsCles': query,
        'departement': departement,
        "distance": 0,
        'page': 1,
        'limit': 10
    }
    if type_contrat:
        params["typeContrat"] = type_contrat
    if publiee_depuis is not None:
        params["publieeDepuis"] = publiee_depuis

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 204:
        # Aucun contenu trouvé
        return None
    else:
        st.error(f"Erreur {response.status_code} : {response.text}")
        return None



# Début de l'application
try:
    df = load_data(file_path)
    df_etablissement = load_etablissement_data(etablissement_path)

    # Filtrer les villes avec une population supérieure à 20 000
    df = df[pd.to_numeric(df['Population en 2021'], errors='coerce') > 20000]

    # Enlever les doublons basés sur 'code_commune_INSEE'
    df = df.drop_duplicates(subset='code_commune_INSEE')

    # Ajouter le code département uniquement en cas d'ambiguïté
    ambiguous_cities = df['Libellé commune ou ARM'].duplicated(keep=False)  # Identifier les libellés ambigus
    df.loc[ambiguous_cities, 'Libellé commune ou ARM'] = df.loc[ambiguous_cities].apply(
        lambda row: f"{row['Libellé commune ou ARM']} ({row['Département']})", axis=1
    )

    # Initialisation de la session state pour les villes
    if 'num_cities' not in st.session_state:
        st.session_state.num_cities = 2  # Par défaut, 2 villes

    # Sélection des villes
    villes = sorted(df["Libellé commune ou ARM"].unique())

    # Container pour aligner les sélecteurs et les boutons
    st.write("### Sélection des villes")
    city_selectors = st.container()

    # Création de colonnes pour les sélecteurs de villes et les boutons + et -
    with city_selectors:
        # Calculer les largeurs des colonnes pour les sélecteurs et les boutons
        # Les boutons prennent moins d'espace que les sélecteurs
        col_widths = [1] * st.session_state.num_cities + [0.1, 0.1]  # Ajout d'une colonne pour le bouton -
        cols = st.columns(col_widths)

        # Ajout des sélecteurs de villes
        city_data = []
        city_names = []

        for i in range(st.session_state.num_cities):
            with cols[i]:
                index = min(i, len(villes)-1)  # Pour éviter l'erreur d'index
                selected_city = st.selectbox(f"{i+1}️⃣ Ville {i+1}", villes, index=index, key=f"city_{i}")

                # Mettre à jour les coordonnées dans le DataFrame principal
                update_coordinates(df, selected_city)

                # Récupérer les données mises à jour pour la ville sélectionnée
                city_data.append(df[df["Libellé commune ou ARM"] == selected_city].squeeze())
                city_names.append(selected_city)

        # Bouton + à côté des sélecteurs
        with cols[-2]:
            # Ajouter un espace pour aligner le bouton verticalement avec les sélecteurs
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕", key="add_city_button", help="Ajouter une ville supplémentaire à comparer"):
                if st.session_state.num_cities < 4:  # Limite à 5 villes pour éviter les problèmes d'affichage
                    st.session_state.num_cities += 1
                    st.rerun()  # Utilisation de st.rerun() au lieu de st.experimental_rerun()

        # Bouton - à côté du bouton +
        with cols[-1]:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➖", key="remove_city_button", help="Enlever une ville de la comparaison"):
                if st.session_state.num_cities > 2:  # Garder au moins 2 villes pour la comparaison
                    st.session_state.num_cities -= 1
                    st.rerun()  # Utilisation de st.rerun() au lieu de st.experimental_rerun()

    # Onglets
    onglet_general, onglet_emploi, onglet_logement, onglet_meteo, onglet_poi, onglet_formation, onglet_created_by = st.tabs([
        f"🔍 Données générales",
        "💼 Emploi",
        "🏠 Logement",
        "🌤️ Météo",
        "📍 Points d'intérêt",
        "🎓 Formation",
        "ℹ️ A propos"
    ])

    # Onglet général
    with onglet_general:
        st.subheader("🔍 Données générales")

        general_metrics = {
            "Population (2022)": ("Population", ""),
            "Superficie": ("Superficie", "km²"),
            "Niveau de vie médian (2021)": ("Médiane du niveau vie en 2021", "€"),
            "Naissances domiciliées (2023)": ("Nombre de naissances domiciliées en 2023", ""),
            "Décès domiciliés (2023)": ("Nombre de décès domiciliés en 2023", "")
        }

        # Créer des colonnes en fonction du nombre de villes
        cols = st.columns(st.session_state.num_cities)
        for i, (col, data, name) in enumerate(zip(cols, city_data, city_names)):
            with col:
                display_metrics(data, name, general_metrics, True)

        # Graphique comparatif
        fig = create_comparison_graph(city_data, general_metrics, city_names)
        st.plotly_chart(fig, use_container_width=True)

    # Onglet emploi
    with onglet_emploi:
        st.subheader("💼 Emploi")

        emploi_metrics = {
            "Emplois (2021)": ("Emplois au LT en 2021", ""),
            "Entreprises actives fin 2022": ("Total des ets actifs fin 2022", ""),
            "Chômeurs 15-64 ans": ("Chômeurs 15-64 ans en 2021", "")
        }

        cols = st.columns(st.session_state.num_cities)
        for i, (col, data, name) in enumerate(zip(cols, city_data, city_names)):
            with col:
                display_metrics(data, name, emploi_metrics)

        fig = create_comparison_graph(city_data, emploi_metrics, city_names)
        st.plotly_chart(fig, use_container_width=True)

        ###### RECHERCHE D'EMPLOI ######
        st.subheader("Recherche d'offres d'emploi - France Travail")

        query = st.text_input("Poste recherché", "Data Analyst")

        # Renseigne ici tes propres identifiants
        client_id = st.secrets.get("client_id", "PAR_outildecisionnel_54f7361a496d42854e4356df6568a5346eba4b9468c9b0067add09ba9f318a4c")
        CLIENT_ID = os.getenv('CLIENT_ID') 
        client_secret = st.secrets.get("client_secret", "0c1a9a6ed2afcc5f1a730e0a1a747dfc8cd81d039ec95005f851bac1e206d216")
        CLIENT_SECRET = os.getenv('CLIENT_SECRET') 

        type_contrat = st.selectbox(
            "Type de contrat",
            options=["", "CDI", "CDD", "MIS", "SAI", "LIB", "AUTRE"],
            format_func=lambda x: "Tous les types" if x == "" else x
        )

        publiee_depuis = st.selectbox(
            "Afficher les offres publiées depuis :",
            options=[1, 3, 7, 14, 31],
            index=2,  # valeur par défaut : 7 jours
            format_func=lambda x: f"{x} jour{'s' if x > 1 else ''}"
        )


        if st.button("Rechercher"):
            access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

            if access_token:
                cols = st.columns(st.session_state.num_cities)
                for i, (col, data, name) in enumerate(zip(cols, city_data, city_names)):
                    with col:
                        st.markdown(f"### Offres d'emploi pour {name}")
                        departement = data.get("Département")

                        job_offers = get_job_offers(query, departement, access_token, type_contrat, publiee_depuis)

                        if job_offers:
                            jobs = job_offers.get('resultats', [])
                            if jobs:
                                # Traitement léger des données pour affichage
                                for job in jobs:
                                    st.subheader(job.get("intitule", ""))
                                    st.markdown(f"**🏢 Entreprise** : {job.get('entreprise', {}).get('nom', 'N/A')}")
                                    st.markdown(f"**📍 Lieu** : {job.get('lieuTravail', {}).get('libelle', 'N/A')}")

                                    date = job.get("dateCreation")
                                    if date is not None:
                                        st.markdown(f"**📅 Publiée le** : {format_date(date)}")

                                    secteur = job.get("secteurActiviteLibelle")
                                    if secteur:
                                        st.markdown(f"**🏭 Secteur d'activité** : {secteur}")

                                    contrat = job.get("typeContrat")
                                    if contrat:
                                        st.markdown(f"**📄 Contrat** : {contrat}")

                                    salaire = job.get("salaire")
                                    if salaire:
                                        salaire_libelle = salaire.get("libelle")
                                        st.markdown(f"**💰 Salaire** : {salaire_libelle}")
                                    else:
                                        st.markdown("**💰 Salaire** : Non précisé")

                                    lien = job.get("origineOffre", {}).get("urlOrigine")
                                    if lien:
                                        st.markdown(f"[🔗 Voir l'offre]({lien})")
                                    else:
                                        st.markdown("*Lien non disponible*")

                                    st.write("---")
                            else:
                                st.warning(f"Aucune offre d'emploi trouvée pour {name}.")
                        else:
                            st.warning(f"Aucune offre d'emploi trouvée pour {name}.")  


    # Onglet logement
    with onglet_logement:
        st.subheader("🏠 Logement")

        logement_metrics = {
            "Logements (2021)": ("Logements en 2021", ""),
            "Résidences principales (2021)": ("Résidences principales en 2021", ""),
            "Logements vacants (2021)": ("Logements vacants en 2021", "")
        }

        cols = st.columns(st.session_state.num_cities)
        for i, (col, data, name) in enumerate(zip(cols, city_data, city_names)):
            with col:
                display_metrics(data, name, logement_metrics)

        fig = create_comparison_graph(city_data, logement_metrics, city_names)
        st.plotly_chart(fig, use_container_width=True)

    # Onglet météo
    with onglet_meteo:
        st.subheader("🌤️ Météo")

        # Liste pour stocker les données de température pour le graphique global
        all_temperature_data = []

        cols = st.columns(st.session_state.num_cities)
        for i, (col, data, name) in enumerate(zip(cols, city_data, city_names)):
            with col:
                latitude = data.get('latitude', None)
                longitude = data.get('longitude', None)
                temperature_data = get_weather(name, latitude=latitude, longitude=longitude)
                all_temperature_data.extend(temperature_data)

                # Afficher les données météorologiques saisonnières
                display_seasonal_weather(name, latitude, longitude)

        # Graphique global de l'évolution de la température sur la semaine
        if all_temperature_data:
            df_temperature = pd.DataFrame(all_temperature_data)
            fig = px.line(
                df_temperature,
                x='date',
                y='temp',
                color='city',
                title="Évolution de la température sur la semaine",
                labels={
                    "date": "Date et heure",
                    "temp": "Température (°C)",
                    "city": "Ville"
                }
            )
            fig.update_yaxes(range=[-10, 40])  # Uniformiser l'échelle des températures
            st.plotly_chart(fig, use_container_width=True)

    # Onglet points d'intérêt
    with onglet_poi:
        st.subheader("📍 Points d'intérêt")

        # Sélecteur centralisé pour les points d'intérêt
        poi_options = st.multiselect(
            "Sélectionnez les points d'intérêt à afficher :",
            [
                "Gares",
                "Musées",
                "Restaurants",
                "Centres sportifs",
                "Cinémas et Théâtres",
                "Banques et Distributeurs",
                "Hôpitaux et Cliniques",
                "Sécurité"
            ],
            key="poi_selector"
        )

        cols = st.columns(st.session_state.num_cities)
        for i, (col, data, name) in enumerate(zip(cols, city_data, city_names)):
            with col:
                display_poi(name, data, poi_options)

    # Onglet formation
    with onglet_formation:
        st.subheader("🎓 Formation")

        cols = st.columns(st.session_state.num_cities)
        for i, (col, data, name) in enumerate(zip(cols, city_data, city_names)):
            with col:
                display_formation(name, data, df_etablissement)

    # Onglet "Créé par"
    with onglet_created_by:
        st.subheader("ℹ️ A propos")
        st.markdown(f"### Contributeurs")
        members = [
            {
                "image": "static/images/thomas-img.jpg",
                "name": "Thomas BELAID",
                "linkedin": "https://www.linkedin.com/in/thomas-belaid-6a4095250/",
                "portfolio": "https://thomaassb.github.io/PortFolio-TB.github.io/",
                "github": "https://github.com/ThomaasSB"
            },
            {
                "image": "static/images/laurent-img.jpg",
                "name": "Laurent CHEN",
                "linkedin": "https://www.linkedin.com/in/laurent-chen8/",
                "portfolio": "https://laurentchen88.github.io/portfolio/",
                "github": "https://github.com/LaurentChen88"
            },
            {
                "image": "static/images/mohammed-img.jpg",
                "name": "Mohammed BOUKOUIREN",
                "linkedin": "https://www.linkedin.com/in/mohammed-boukouiren/",
                "github": "https://github.com/2mow"
            }
        ]
        
        cols = st.columns(len(members))

        # CSS pour styliser les boutons
        st.markdown("""
            <style>
            .button, .button:link, .button:visited, .button:hover, .button:active {
                display: inline-block;
                padding: 10px 20px;
                margin: 5px 0;
                font-size: 14px;
                font-weight: bold;
                color: white !important;
                text-align: center;
                text-decoration: none !important;
                border-radius: 5px;
            }
            .portfolio {
                background-color: #4CAF50;
            }
            .button:hover {
                opacity: 0.8;
            }
            </style>
        """, unsafe_allow_html=True)

        

        for col, member in zip(cols, members):
            with col:
                # Afficher l'image
                st.image(member['image'], width=150, caption=member['name'])
                
                # Logos LinkedIn, GitHub et Portfolio
                st.markdown(f"""
                    <div style="display: flex; gap: 10px; margin: 0 0 25px 20px;">
                        <a href="{member['linkedin']}" target="_blank">
                            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" style="width: 32px; height: 32px;">
                        </a>
                        <a href="{member['github']}" target="_blank">
                            <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" alt="GitHub" style="width: 32px; height: 32px;">
                        </a>
                        {"<a href='" + member['portfolio'] + "' target='_blank'><img src='https://cdn-icons-png.flaticon.com/512/1006/1006771.png' alt='Portfolio' style='width: 32px; height: 32px;'></a>" if 'portfolio' in member else ""}
                    </div>
                """, unsafe_allow_html=True)

        # Section "Réalisé entre..."
        st.markdown("""
            <div style="margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 10px; border: 1px solid #ddd;">
                <h4 style="text-align: center; color: #333;">📅 Réalisé entre mars et avril 2025</h4>
                <p style="text-align: center; color: #555;">
                    Ce projet a été réalisé dans le cadre du projet outil décisionnel en fin de 3ème année en BUT Science des Données
                    à l'IUT de Paris - Rives de Seine.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Section "Source de données"
        st.markdown("""
            <div style="margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 10px; border: 1px solid #ddd;">
                <h4 style="color: #333;">📚 Source de données</h4>
                <ul style="color: #555; line-height: 1.6;">
                    <li>🌍 <strong>Population</strong> : <a href="https://geo.api.gouv.fr" target="_blank">geo.api.gouv.fr</a></li>
                    <li>📊 <strong>Données générales, emploi, logement, formation</strong> : <a href="https://data.gouv.fr" target="_blank">data.gouv.fr</a></li>
                    <li>💼 <strong>Offres d'emploi</strong> : <a href="https://www.data.gouv.fr/fr/dataservices/api-offres-demploi/" target="_blank">data.gouv.fr</a></li>
                    <li>☁️ <strong>Météo</strong> : <a href="https://openweathermap.org" target="_blank">API OpenWeatherMap</a> et <a href="https://meteostat.net" target="_blank">meteostat.net</a></li>
                    <li>📍 <strong>Points d'intérêt</strong> : <a href="https://overpass-api.de" target="_blank">API Overpass</a></li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("❌ Fichier non trouvé : data/data_final.xlsx ou data/etablissement.csv")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
