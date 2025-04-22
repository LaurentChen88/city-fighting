import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster

# Configuration de la page
st.set_page_config(
    page_title="City Fighting",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thème personnalisé
st.markdown("""
    <style>
    /* Thème de couleurs */
    :root {
        --primary-color: #1E90FF;
        --secondary-color: #D1D1D1;
        --background-color: #F0F0F0;
        --text-color: #333333;
        --font-family: 'Arial', sans-serif;
    }

    /* Style de la page */
    body {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: var(--font-family);
    }

    /* Style des titres */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-color);
    }

    /* Style des boutons */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }

    .stButton > button:hover {
        background-color: var(--secondary-color);
    }

    /* Style des cartes */
    .stCard {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Style des graphiques */
    .stPlotlyChart {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Bouton pour basculer entre mode clair et mode sombre
dark_mode = st.checkbox("Activer le mode sombre")

if dark_mode:
    st.markdown("""
        <style>
        :root {
            --background-color: #1E1E1E;
            --text-color: #FFFFFF;
            --primary-color: #BB86FC;
            --secondary-color: #03DAC6;
        }
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color);
        }
        .stButton > button {
            background-color: var(--primary-color);
            color: white;
        }
        .stButton > button:hover {
            background-color: var(--secondary-color);
        }
        .stCard {
            background-color: #333333;
            color: white;
        }
        .stPlotlyChart {
            background-color: #333333;
        }
        </style>
    """, unsafe_allow_html=True)

# Titre
st.title("🏙️ City Fighting - Comparateur de deux villes en France")

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
@st.cache_data
def get_weather(lat, lon, selected_hours):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': "6aea17a766b369d16fdcf84a0b16fdac",
        'units': 'metric',
        'lang': 'fr',
        'cnt': 9  # Récupérer les prévisions pour les 3 prochains jours (3 jours * 3 intervalles par jour)
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "list" in data:
            st.write(f"📍 Météo à {data['city']['name']}")
            for forecast in data['list']:
                forecast_time = pd.to_datetime(forecast['dt_txt'])
                if forecast_time.hour in selected_hours:
                    date = forecast_time.strftime('%d/%m/%Y %H:%M')
                    temp = int(round(forecast['main']['temp']))
                    feels_like = int(round(forecast['main']['feels_like']))
                    description = forecast['weather'][0]['description']
                    st.write(f"📅 **{date}**")
                    st.write(f"🌡️ Température : {temp}°C")
                    st.write(f"🤔 Ressentie : {feels_like}°C")
                    st.write(f"🌤️ Conditions : {description}")
                    st.write("---")
        else:
            st.write("⚠️ Données météo incomplètes.")

    except requests.exceptions.HTTPError as err:
        st.write("❌ Erreur HTTP :", err)
    except requests.exceptions.RequestException as err:
        st.write("❌ Erreur de requête :", err)
    except Exception as e:
        st.write("❌ Erreur inattendue :", e)

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
def update_coordinates(data, city_name):
    if pd.isna(data['longitude']) or pd.isna(data['latitude']):
        latitude, longitude = get_coordinates(city_name)
        if latitude is not None and longitude is not None:
            data['latitude'] = latitude
            data['longitude'] = longitude

    # Mettre à jour la population
    if 'code_commune_INSEE' in data:
        insee_code = data['code_commune_INSEE']
        population_data = get_population_by_insee(insee_code)
        if population_data and 'population' in population_data:
            data['Population'] = population_data['population']

def create_comparison_graph(data_1, data_2, metrics, ville_1, ville_2):
    """
    Crée un graphique comparatif basé sur les métriques fournies.

    :param data_1: Données de la première ville
    :param data_2: Données de la deuxième ville
    :param metrics: Dictionnaire des métriques (clé: label, valeur: (colonne, unité))
    :param ville_1: Nom de la première ville
    :param ville_2: Nom de la deuxième ville
    :return: Graphique Plotly
    """
    # Création du DataFrame initial
    graphe_data = pd.DataFrame({
        "Variable": list(metrics.keys()),  # Utilise les labels des métriques
        f"{ville_1}_original": [pd.to_numeric(data_1[column], errors='coerce') for column, _ in metrics.values()],
        f"{ville_2}_original": [pd.to_numeric(data_2[column], errors='coerce') for column, _ in metrics.values()],
    })

    # Remplacer les valeurs NaN par 0 pour éviter les erreurs dans les calculs
    graphe_data.fillna(0, inplace=True)

    # Ajouter les colonnes normalisées
    graphe_data[ville_1] = graphe_data[f"{ville_1}_original"] / (
        graphe_data[f"{ville_1}_original"] + graphe_data[f"{ville_2}_original"]
    )
    graphe_data[ville_2] = graphe_data[f"{ville_2}_original"] / (
        graphe_data[f"{ville_1}_original"] + graphe_data[f"{ville_2}_original"]
    )

    # Arrondir les colonnes normalisées
    graphe_data[ville_1] = graphe_data[ville_1].round(2)
    graphe_data[ville_2] = graphe_data[ville_2].round(2)

    # Transformation pour le graphe
    graphe_data = graphe_data.melt(
        id_vars=["Variable", f"{ville_1}_original", f"{ville_2}_original"],
        var_name="Ville",
        value_name="Valeur"
    )

    # Ajouter une colonne pour les valeurs originales dans le hover et arrondir
    graphe_data["Valeur_originale"] = graphe_data.apply(
        lambda row: row[f"{ville_1}_original"] if row["Ville"] == ville_1 else row[f"{ville_2}_original"], axis=1
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
            "Valeur_originale": True,  # Affiche la valeur réelle arrondie
            "Valeur": True,            # Affiche la valeur normalisée arrondie
            "Variable": True,          # Affiche la variable
            "Ville": True              # Affiche la ville
        }
    )
    return fig

# Fonction pour afficher les points d'intérêt sur la carte
def display_poi_on_map(m, bbox, poi_key, poi_type, icon_color):
    poi_data = get_overpass_data(bbox, poi_key, poi_type)
    if poi_data:
        display_poi_with_cluster(m, poi_data, icon_color)

# Fonction générique pour afficher les points d'intérêt
def display_poi(city_name, data):
    st.markdown(f"### {city_name}")

    # Sélecteur pour les points d'intérêt
    poi_options = st.multiselect(
        "Sélectionnez les points d'intérêt à afficher :",
        ["Gares", "Musées", "Restaurants", "Salles de sport"],  # Ajout de "Salles de sport"
        key=f"poi_{city_name}"
    )

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
            display_poi_on_map(m, bbox, "railway", "station", "green")
        if "Musées" in poi_options:
            display_poi_on_map(m, bbox, "tourism", "museum", "purple")
        if "Restaurants" in poi_options:
            display_poi_on_map(m, bbox, "amenity", "restaurant", "orange")
        if "Salles de sport" in poi_options:
            display_poi_on_map(m, bbox, "leisure", "sports_centre", "red")  # Ajout des salles de sport

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
        m_ecoles = folium.Map(location=[ecoles.iloc[0]['latitude_ecole'], ecoles.iloc[0]['longitude_ecole']], zoom_start=12)
        for _, ecole in ecoles.iterrows():
            folium.Marker(
                location=[ecole['latitude_ecole'], ecole['longitude_ecole']],
                popup=ecole['libellé'],
                icon=folium.Icon(color="green")
            ).add_to(m_ecoles)
        st_folium(m_ecoles, width=700, height=500, key=f"map_{city_name}")
    else:
        st.warning("Aucune école trouvée pour cette ville.")

    # Afficher le tableau
    st.dataframe(ecoles, key=f"table_{city_name}")

# Fonction pour afficher les postes de police et de pompiers
def display_security_poi(city_name, data):
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

        # Récupérer et afficher les postes de police et de pompiers
        bbox = f"{data['latitude']-0.1},{data['longitude']-0.1},{data['latitude']+0.1},{data['longitude']+0.1}"
        display_poi_on_map(m, bbox, "amenity", "police", "red")
        display_poi_on_map(m, bbox, "amenity", "fire_station", "darkred")

        st_folium(m, width=700, height=400)
    else:
        st.warning("Données géographiques manquantes pour cette ville.")

# Début de l'application
try:
    df = load_data(file_path)
    df_etablissement = load_etablissement_data(etablissement_path)

    # Ajouter une colonne "Population" avec des valeurs par défaut (NaN)
    df['Population'] = pd.NaT

    # Filtrez les villes avec une population supérieure à 20 000
    df = df[pd.to_numeric(df['Population en 2021'], errors='coerce') > 20000]

    # Enlever les doublons basés sur 'code_commune_INSEE'
    df = df.drop_duplicates(subset='code_commune_INSEE')

    # Ajouter le code département uniquement en cas d'ambiguïté
    ambiguous_cities = df['Libellé commune ou ARM'].duplicated(keep=False)  # Identifier les libellés ambigus
    df.loc[ambiguous_cities, 'Libellé commune ou ARM'] = df.loc[ambiguous_cities].apply(
        lambda row: f"{row['Libellé commune ou ARM']} ({row['Département']})", axis=1
    )

    # Sélection des villes
    villes = sorted(df["Libellé commune ou ARM"].unique())
    col1, col2 = st.columns(2)
    with col1:
        ville_1 = st.selectbox("1️⃣ Sélectionnez la première ville :", villes)
    with col2:
        ville_2 = st.selectbox("2️⃣ Sélectionnez la deuxième ville :", villes, index=1)
    data_1 = df[df["Libellé commune ou ARM"] == ville_1].squeeze()
    data_2 = df[df["Libellé commune ou ARM"] == ville_2].squeeze()

    update_coordinates(data_1, ville_1)
    update_coordinates(data_2, ville_2)

    # Onglets
    onglet_general, onglet_emploi, onglet_logement, onglet_meteo, onglet_poi, onglet_formation, onglet_securite = st.tabs([
        f"🔍 Données générales",
         "💼 Emploi",
         "🏠 Logement",
         "🌤️ Météo",
         "📍 Points d'intérêt",
         "🎓 Formation",
         "🚨 Sécurité"
         ])

    # Onglet général
    with onglet_general:
        st.subheader("🔍 Données générales")

        general_metrics = {
            "Population": ("Population", ""),
            "Superficie": ("Superficie", "km²"),
            "Région": ("Région", ""),
            "Département": ("Département", ""),
            "Niveau de vie médian": ("Médiane du niveau vie en 2021", "€"),
            "Naissances domiciliées en 2023": ("Nombre de naissances domiciliées en 2023", ""),
            "Décès domiciliés en 2023": ("Nombre de décès domiciliés en 2023", "")
        }
        col_left, col_right = st.columns(2)

        with col_left:
            display_metrics(data_1, ville_1, general_metrics, True)

        with col_right:
            display_metrics(data_2, ville_2, general_metrics, True)

        fig = create_comparison_graph(data_1, data_2, general_metrics, ville_1, ville_2)
        st.plotly_chart(fig, use_container_width=True)

    # Onglet emploi
    with onglet_emploi:
        st.subheader("💼 Emploi")

        emploi_metrics = {
            "Emplois en 2021": ("Emplois au LT en 2021", ""),
            "Entreprises actives fin 2022": ("Total des ets actifs fin 2022", ""),
            "Chômeurs 15-64 ans": ("Chômeurs 15-64 ans en 2021", "")
        }
        col_left, col_right = st.columns(2)

        with col_left:
            display_metrics(data_1, ville_1, emploi_metrics)

        with col_right:
            display_metrics(data_2, ville_2, emploi_metrics)

        fig = create_comparison_graph(data_1, data_2, emploi_metrics, ville_1, ville_2)
        st.plotly_chart(fig, use_container_width=True)

    # Onglet logement
    with onglet_logement:
        st.subheader("🏠 Logement")

        logement_metrics = {
            "Logements en 2021": ("Logements en 2021", ""),
            "Résidences principales en 2021": ("Résidences principales en 2021", ""),
            "Logements vacants en 2021": ("Logements vacants en 2021", "")
        }
        col_left, col_right = st.columns(2)

        with col_left:
            display_metrics(data_1, ville_1, logement_metrics)

        with col_right:
            display_metrics(data_2, ville_2, logement_metrics)

        fig = create_comparison_graph(data_1, data_2, logement_metrics, ville_1, ville_2)
        st.plotly_chart(fig, use_container_width=True)

    # Onglet météo
    with onglet_meteo:
        st.subheader("🌤️ Prévisions météo pour les 3 prochains jours")

        # Sélecteur d'heures
        selected_hours = st.multiselect(
            "Sélectionnez les heures pour lesquelles vous souhaitez voir les prévisions :",
            options=[15, 0, 9],
            default=[15, 0, 9]
        )

        col_left, col_right = st.columns(2)

        with col_left:
            if "latitude" in data_1 and "longitude" in data_1:
                get_weather(data_1['latitude'], data_1['longitude'], selected_hours)
            else:
                st.warning("Données géographiques manquantes pour cette ville.")

        with col_right:
            if "latitude" in data_2 and "longitude" in data_2:
                get_weather(data_2['latitude'], data_2['longitude'], selected_hours)
            else:
                st.warning("Données géographiques manquantes pour cette ville.")

    # Onglet points d'intérêt
    with onglet_poi:
        st.subheader("📍 Points d'intérêt")
        col_left, col_right = st.columns(2)

        with col_left:
            display_poi(ville_1, data_1)

        with col_right:
            display_poi(ville_2, data_2)

    with onglet_formation:
        st.subheader("🎓 Formation")
        col_left, col_right = st.columns(2)

        with col_left:
            display_formation(ville_1, data_1, df_etablissement)

        with col_right:
            display_formation(ville_2, data_2, df_etablissement)

    # Onglet sécurité
    with onglet_securite:
        st.subheader("🚨 Sécurité")
        col_left, col_right = st.columns(2)

        with col_left:
            display_security_poi(ville_1, data_1)

        with col_right:
            display_security_poi(ville_2, data_2)

except FileNotFoundError:
    st.error("❌ Fichier non trouvé : data/data_final.xlsx ou data/etablissement.csv")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
