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
    layout="wide"
)
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
@st.cache_data # Cachez les résultats des appels API avec @st.cache_data pour éviter de refaire les mêmes requêtes à chaque exécution
def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': "6aea17a766b369d16fdcf84a0b16fdac",
        'units': 'metric',
        'lang': 'fr'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "main" in data and "weather" in data:
            st.write(f"📍 Météo à {data['name']}")
            st.write(f"🌡️ Température : {int(round(data['main']['temp']))}°C")
            st.write(f"🤔 Ressentie : {int(round(data['main']['feels_like']))}°C")
            st.write(f"🌤️ Conditions : {data['weather'][0]['description']}")
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


# Vérifier si les coordonnées manquent et les récupérer si nécessaire
def update_coordinates(data, city_name):
    if pd.isna(data['longitude']) or pd.isna(data['latitude']):
        latitude, longitude = get_coordinates(city_name)
        if latitude is not None and longitude is not None:
            data['latitude'] = latitude
            data['longitude'] = longitude


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


# fonction générique pour afficher les points d'intérêt
def display_poi(city_name, data):
    st.markdown(f"### {city_name}")

    # Sélecteur pour les points d'intérêt
    poi_options = st.multiselect(
        "Sélectionnez les points d'intérêt à afficher :",
        ["Gares", "Musées", "Restaurants"],
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

        st_folium(m, width=700, height=400)
    else:
        st.warning("Données géographiques manquantes pour cette ville.")


# fonction générique qui prend en paramètre les métriques à afficher et les données associées
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

# fonction générique pour afficher les formations
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


# début de l'application
try:
    df = load_data(file_path)
    df_etablissement = load_etablissement_data(etablissement_path)

    # filtrez les villes avec une population supérieure à 20 000
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
    onglet_general, onglet_emploi, onglet_logement, onglet_meteo, onglet_poi, onglet_formation = st.tabs([
        f"🔍 Données générales", 
         "💼 Emploi", 
         "🏠 Logement", 
         "🌤️ Météo", 
         "📍 Points d'intérêt",
         "🎓 Formation"
         ])

    # onglet général
    with onglet_general:
        st.subheader("🔍 Données générales")

        general_metrics = {
            "Population 2021": ("Population en 2021", ""), 
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

    # onglet emploi
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

    # onglet logement
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

    # onglet météo
    with onglet_meteo:
        st.subheader("🌤️ Météo actuelle")
        
        col_left, col_right = st.columns(2)

        with col_left:
            if "latitude" in data_1 and "longitude" in data_1:
                get_weather(data_1['latitude'], data_1['longitude'])
            else:
                st.warning("Données géographiques manquantes pour cette ville.")

        with col_right:
            if "latitude" in data_2 and "longitude" in data_2:
                get_weather(data_2['latitude'], data_2['longitude'])
            else:
                st.warning("Données géographiques manquantes pour cette ville.")

    # onglet points d'intérêt
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


except FileNotFoundError:
    st.error("❌ Fichier non trouvé : data/data_final.xlsx ou data/etablissement.csv")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
