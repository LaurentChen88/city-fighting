import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import requests
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster

# Initialisation du géolocaliseur
geolocator = Nominatim(user_agent="mon_application")

# Fonction pour obtenir la météo
@st.cache_data # Cachez les résultats des appels API avec @st.cache_data pour éviter de refaire les mêmes requêtes à chaque exécution
def get_weather(lat, lon, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric',
        'lang': 'fr'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "main" in data and "weather" in data:
            st.write(f"📍 Météo à {data['name']}")
            st.write(f"🌡️ Température : {data['main']['temp']}°C")
            st.write(f"🤔 Ressentie : {data['main']['feels_like']}°C")
            st.write(f"🌤️ Conditions : {data['weather'][0]['description']}")
        else:
            st.write("⚠️ Données météo incomplètes.")

    except requests.exceptions.HTTPError as err:
        st.write("❌ Erreur HTTP :", err)
    except requests.exceptions.RequestException as err:
        st.write("❌ Erreur de requête :", err)
    except Exception as e:
        st.write("❌ Erreur inattendue :", e)

# Fonction pour récupérer les données des gares à l'aide de l'API Overpass
@st.cache_data
def get_gares_data(bbox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["railway"="station"]({bbox});
      way["railway"="station"]({bbox});
      relation["railway"="station"]({bbox});
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

# Fonction pour récupérer les données des musées à l'aide de l'API Overpass
@st.cache_data
def get_musees_data(bbox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["tourism"="museum"]({bbox});
      way["tourism"="museum"]({bbox});
      relation["tourism"="museum"]({bbox});
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

# Fonction pour récupérer les données des restaurants à l'aide de l'API Overpass
@st.cache_data
def get_restaurants_data(bbox):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="restaurant"]({bbox});
      way["amenity"="restaurant"]({bbox});
      relation["amenity"="restaurant"]({bbox});
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


# Fonction pour obtenir les coordonnées géographiques d'une ville à partir de son code INSEE
@st.cache_data
def get_coordinates_from_insee(code_insee):
    url = f"https://api-adresse.data.gouv.fr/search/?q={code_insee}&type=municipality&autocomplete=0"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            return coords[1], coords[0]  # Latitude, Longitude
    return None, None

# Configuration de la page
st.set_page_config(
    page_title="Comparateur de villes - City Fighting",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ Comparateur de deux villes")

# Chargement des données
file_path = "data/data_final.xlsx"
etablissement_path = "data/etablissement_final.csv"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

@st.cache_data
def load_etablissement_data(path):
    return pd.read_csv(path)

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


@st.cache_data
def create_comparison_graph(data_1, data_2, variables_a_comparer, ville_1, ville_2):
    graphe_data = pd.DataFrame({
        "Variable": list(variables_a_comparer.values()),
        ville_1: [data_1[k] for k in variables_a_comparer.keys()],
        ville_2: [data_2[k] for k in variables_a_comparer.keys()],
    })

    graphe_data = graphe_data.melt(id_vars="Variable", var_name="Ville", value_name="Valeur")

    fig = px.bar(
        graphe_data,
        x="Variable",
        y="Valeur",
        color="Ville",
        barmode="group",
        title="📉 Comparatif des indicateurs clés"
    )
    return fig


try:
    df = load_data(file_path)
    df_etablissement = load_etablissement_data(etablissement_path)

    # Enlever les doublons basés sur 'code_commune_INSEE'
    df = df.drop_duplicates(subset='code_commune_INSEE')

    # Ajouter un suffixe unique pour les doublons
    df['Libellé commune ou ARM'] = df['Libellé commune ou ARM'] + \
        df.groupby('Libellé commune ou ARM').cumcount().apply(lambda x: f" ({x})" if x > 0 else "")

    # Sélection des villes
    villes = sorted(df["Libellé commune ou ARM"].unique())
    col1, col2 = st.columns(2)
    with col1:
        ville_1 = st.selectbox("📍 Sélectionnez la première ville :", villes)
    with col2:
        ville_2 = st.selectbox("🏙️ Sélectionnez la deuxième ville :", villes, index=1)
    data_1 = df[df["Libellé commune ou ARM"] == ville_1].squeeze()
    data_2 = df[df["Libellé commune ou ARM"] == ville_2].squeeze()

    # Vérifier si les coordonnées manquent et les récupérer si nécessaire pour data_1
    if pd.isna(data_1['longitude']) or pd.isna(data_1['latitude']):
        latitude, longitude = get_coordinates(ville_1)
        if latitude is not None and longitude is not None:
            data_1['latitude'] = latitude
            data_1['longitude'] = longitude

    # Vérifier si les coordonnées manquent et les récupérer si nécessaire pour data_2
    if pd.isna(data_2['longitude']) or pd.isna(data_2['latitude']):
        latitude, longitude = get_coordinates(ville_2)
        if latitude is not None and longitude is not None:
            data_2['latitude'] = latitude
            data_2['longitude'] = longitude

    # Onglets
    tab1, tab2, tab3 = st.tabs(["🔍 Comparatif global", f"🏘️ {ville_1}", f"🏘️ {ville_2}"])

    with tab1:
        st.subheader("🔍 Comparaison graphique")

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"### {ville_1}")
            population_1 = pd.to_numeric(data_1["Population en 2021"], errors='coerce')
            if not pd.isna(population_1):
                st.metric("Population 2021", int(population_1))
            else:
                st.warning("Donnée manquante pour la population 2021 de cette ville.")

            logements_1 = pd.to_numeric(data_1["Logements en 2021"], errors='coerce')
            if not pd.isna(logements_1):
                st.metric("Logements en 2021", int(logements_1))
            else:
                st.warning("Donnée manquante pour les logements 2021 de cette ville.")

            taux_pauvrete_1 = pd.to_numeric(data_1["Taux de pauvreté en 2021"], errors='coerce')
            if not pd.isna(taux_pauvrete_1):
                st.metric("Taux de pauvreté", f"{taux_pauvrete_1} %")
            else:
                st.warning("Donnée manquante pour le taux de pauvreté de cette ville.")

            chomeurs_1 = pd.to_numeric(data_1["Chômeurs 15-64 ans en 2021"], errors='coerce')
            if not pd.isna(chomeurs_1):
                st.metric("Chômeurs 15-64 ans", int(chomeurs_1))
            else:
                st.warning("Donnée manquante pour les chômeurs 15-64 ans de cette ville.")

            naissances_1 = pd.to_numeric(data_1["Naissances entre 2015 et 2020"], errors='coerce')
            if not pd.isna(naissances_1):
                st.metric("Naissances 2015-2020", int(naissances_1))
            else:
                st.warning("Donnée manquante pour les naissances 2015-2020.")

            deces_1 = pd.to_numeric(data_1["Décès entre 2015 et 2020"], errors='coerce')
            if not pd.isna(deces_1):
                st.metric("Décès 2015-2020", int(deces_1))
            else:
                st.warning("Donnée manquante pour les décès 2015-2020.")

            residences_principales_1 = pd.to_numeric(data_1["Résidences principales en 2021"], errors='coerce')
            if not pd.isna(residences_principales_1):
                st.metric("Résidences principales", int(residences_principales_1))
            else:
                st.warning("Donnée manquante pour les résidences principales de cette ville.")

            logements_vacants_1 = pd.to_numeric(data_1["Logements vacants en 2021"], errors='coerce')
            if not pd.isna(logements_vacants_1):
                st.metric("Logements vacants", int(logements_vacants_1))
            else:
                st.warning("Donnée manquante pour les logements vacants de cette ville.")

            emplois_1 = pd.to_numeric(data_1["Emplois au LT en 2021"], errors='coerce')
            if not pd.isna(emplois_1):
                st.metric("Emplois", int(emplois_1))
            else:
                st.warning("Donnée manquante pour les emplois de cette ville.")

            entreprises_actives_1 = pd.to_numeric(data_1["Total des ets actifs fin 2022"], errors='coerce')
            if not pd.isna(entreprises_actives_1):
                st.metric("Entreprises actives", int(entreprises_actives_1))
            else:
                st.warning("Donnée manquante pour les entreprises actives de cette ville.")

            niveau_vie_1 = pd.to_numeric(data_1["Médiane du niveau vie en 2021"], errors='coerce')
            if not pd.isna(niveau_vie_1):
                st.metric("Niveau de vie médian", f"{niveau_vie_1} €")
            else:
                st.warning("Donnée manquante pour le niveau de vie médian de cette ville.")

        with col_right:
            st.markdown(f"### {ville_2}")
            population_2 = pd.to_numeric(data_2["Population en 2021"], errors='coerce')
            if not pd.isna(population_2):
                st.metric("Population 2021", int(population_2))
            else:
                st.warning("Donnée manquante pour la population 2021 de cette ville.")

            logements_2 = pd.to_numeric(data_2["Logements en 2021"], errors='coerce')
            if not pd.isna(logements_2):
                st.metric("Logements en 2021", int(logements_2))
            else:
                st.warning("Donnée manquante pour les logements 2021 de cette ville.")

            taux_pauvrete_2 = pd.to_numeric(data_2["Taux de pauvreté en 2021"], errors='coerce')
            if not pd.isna(taux_pauvrete_2):
                st.metric("Taux de pauvreté", f"{taux_pauvrete_2} %")
            else:
                st.warning("Donnée manquante pour le taux de pauvreté de cette ville.")

            chomeurs_2 = pd.to_numeric(data_2["Chômeurs 15-64 ans en 2021"], errors='coerce')
            if not pd.isna(chomeurs_2):
                st.metric("Chômeurs 15-64 ans", int(chomeurs_2))
            else:
                st.warning("Donnée manquante pour les chômeurs 15-64 ans de cette ville.")

            naissances_2 = pd.to_numeric(data_2["Naissances entre 2015 et 2020"], errors='coerce')
            if not pd.isna(naissances_2):
                st.metric("Naissances 2015-2020", int(naissances_2))
            else:
                st.warning("Donnée manquante pour les naissances 2015-2020.")

            deces_2 = pd.to_numeric(data_2["Décès entre 2015 et 2020"], errors='coerce')
            if not pd.isna(deces_2):
                st.metric("Décès 2015-2020", int(deces_2))
            else:
                st.warning("Donnée manquante pour les décès 2015-2020.")

            residences_principales_2 = pd.to_numeric(data_2["Résidences principales en 2021"], errors='coerce')
            if not pd.isna(residences_principales_2):
                st.metric("Résidences principales", int(residences_principales_2))
            else:
                st.warning("Donnée manquante pour les résidences principales de cette ville.")

            logements_vacants_2 = pd.to_numeric(data_2["Logements vacants en 2021"], errors='coerce')
            if not pd.isna(logements_vacants_2):
                st.metric("Logements vacants", int(logements_vacants_2))
            else:
                st.warning("Donnée manquante pour les logements vacants de cette ville.")

            emplois_2 = pd.to_numeric(data_2["Emplois au LT en 2021"], errors='coerce')
            if not pd.isna(emplois_2):
                st.metric("Emplois", int(emplois_2))
            else:
                st.warning("Donnée manquante pour les emplois de cette ville.")

            entreprises_actives_2 = pd.to_numeric(data_2["Total des ets actifs fin 2022"], errors='coerce')
            if not pd.isna(entreprises_actives_2):
                st.metric("Entreprises actives", int(entreprises_actives_2))
            else:
                st.warning("Donnée manquante pour les entreprises actives de cette ville.")

            niveau_vie_2 = pd.to_numeric(data_2["Médiane du niveau vie en 2021"], errors='coerce')
            if not pd.isna(niveau_vie_2):
                st.metric("Niveau de vie médian", f"{niveau_vie_2} €")
            else:
                st.warning("Donnée manquante pour le niveau de vie médian de cette ville.")

        st.markdown("---")
        st.subheader("📊 Graphe comparatif")

        variables_a_comparer = {
            "Population en 2021": "Population",
            "Logements en 2021": "Logements",
            "Chômeurs 15-64 ans en 2021": "Chômage",
            # "Taux de pauvreté en 2021": "Pauvreté (%)",
            "Emplois au LT en 2021": "Emplois",
            "Médiane du niveau vie en 2021": "Niveau de vie (€)",
            "Naissances entre 2015 et 2020": "Naissances",
            "Décès entre 2015 et 2020": "Décès",
            "Résidences principales en 2021": "Résidences principales",
            "Logements vacants en 2021": "Logements vacants",
            "Total des ets actifs fin 2022": "Entreprises actives",
        }

        fig = create_comparison_graph(data_1, data_2, variables_a_comparer, ville_1, ville_2)
        st.plotly_chart(fig, use_container_width=True)

        # Compteur des variables supérieures
        positive_variables = [
            "Population en 2021",
            "Logements en 2021",
            "Emplois au LT en 2021",
            "Naissances entre 2015 et 2020",
            "Résidences principales en 2021",
            "Total des ets actifs fin 2022",
            "Médiane du niveau vie en 2021"
        ]

        count_ville_1 = sum([1 for k in positive_variables if pd.to_numeric(data_1[k], errors='coerce') > pd.to_numeric(data_2[k], errors='coerce')])
        count_ville_2 = sum([1 for k in positive_variables if pd.to_numeric(data_2[k], errors='coerce') > pd.to_numeric(data_1[k], errors='coerce')])

        st.markdown(f"**Nombre de variables supérieures :**")
        st.markdown(f"- {ville_1} : {count_ville_1}")
        st.markdown(f"- {ville_2} : {count_ville_2}")

    # Fonction pour afficher les points d'intérêt sur la carte
    def display_poi_on_map(m, data, bbox, poi_type, icon_color):
        poi_data = None
        if poi_type == "Gares":
            poi_data = get_gares_data(bbox)
        elif poi_type == "Musées":
            poi_data = get_musees_data(bbox)
        elif poi_type == "Restaurants":
            poi_data = get_restaurants_data(bbox)

        if poi_data:
            display_poi_with_cluster(m, poi_data, icon_color)

    # Onglet Ville 1
    with tab2:
        st.header(f"📍 Informations détaillées : {ville_1}")
        wiki_url_1 = f"https://fr.wikipedia.org/wiki/{ville_1.replace(' ', '_')}"
        st.markdown(f"🔗 [Page Wikipédia de {ville_1}]({wiki_url_1})")

        # Afficher la météo pour la ville 1
        st.subheader("Météo actuelle")
        get_weather(data_1['latitude'], data_1['longitude'], "6aea17a766b369d16fdcf84a0b16fdac")

        # Sélecteur pour choisir les points d'intérêt à afficher
        poi_options_ville_1 = st.multiselect(
            "Sélectionnez les points d'intérêt à afficher :",
            ["Gares", "Musées", "Restaurants"], 
            key="poi_ville_1"
        )

        # Afficher la carte pour localiser la ville 1
        if "latitude" in data_1 and "longitude" in data_1:
            m = folium.Map(location=[data_1["latitude"], data_1["longitude"]], zoom_start=12)
            folium.Marker(
                location=[data_1["latitude"], data_1["longitude"]],
                popup=ville_1,
                tooltip=ville_1,
                icon=folium.Icon(color="blue")
            ).add_to(m)

            # Récupérer et afficher les données des points d'intérêt sélectionnés
            bbox = f"{data_1['latitude']-0.1},{data_1['longitude']-0.1},{data_1['latitude']+0.1},{data_1['longitude']+0.1}"
            if "Gares" in poi_options_ville_1:
                display_poi_on_map(m, data_1, bbox, "Gares", "green")
            if "Musées" in poi_options_ville_1:
                display_poi_on_map(m, data_1, bbox, "Musées", "purple")
            if "Restaurants" in poi_options_ville_1:
                display_poi_on_map(m, data_1, bbox, "Restaurants", "orange")

            st_folium(m, width=700, height=400)
        else:
            st.warning("Données géographiques manquantes pour cette ville.")

        st.write("### Démographie")
        st.write(f"- Population 2021 : {int(pd.to_numeric(data_1['Population en 2021'], errors='coerce'))}")
        st.write(f"- Naissances 2015-2020 : {data_1['Naissances entre 2015 et 2020']}")
        st.write(f"- Décès 2015-2020 : {data_1['Décès entre 2015 et 2020']}")

        st.write("### Logement")
        st.write(f"- Logements : {int(pd.to_numeric(data_1['Logements en 2021'], errors='coerce'))}")
        st.write(f"- Résidences principales : {data_1['Résidences principales en 2021']}")
        st.write(f"- Vacants : {data_1['Logements vacants en 2021']}")

        st.write("### Emploi et économie")
        st.write(f"- Emplois : {data_1['Emplois au LT en 2021']}")
        st.write(f"- Chômeurs : {data_1['Chômeurs 15-64 ans en 2021']}")
        st.write(f"- Entreprises actives : {data_1['Total des ets actifs fin 2022']}")

        st.write("### Revenus")
        st.write(f"- Taux de pauvreté : {data_1['Taux de pauvreté en 2021']} %")
        st.write(f"- Niveau de vie médian : {data_1['Médiane du niveau vie en 2021']} €")

        # Afficher les écoles pour la ville 1
        st.write("### Établissements scolaires")
        ecoles_ville_1 = df_etablissement[df_etablissement['Numéro Région'] == data_1['Région']]

        # Utiliser des colonnes pour afficher la carte et le tableau côte à côte
        col_map, col_table = st.columns(2)

        with col_map:
            if not ecoles_ville_1.empty:
                m_ecoles = folium.Map(location=[ecoles_ville_1.iloc[0]['latitude_ecole'], ecoles_ville_1.iloc[0]['longitude_ecole']], zoom_start=12)

                for _, ecole in ecoles_ville_1.iterrows():
                    folium.Marker(
                        location=[ecole['latitude_ecole'], ecole['longitude_ecole']],
                        popup=ecole['libellé'],  # Remplacez par le nom de la colonne contenant le nom de l'école
                        icon=folium.Icon(color="green")
                    ).add_to(m_ecoles)

                st_folium(m_ecoles, width=700, height=500)
            else:
                st.warning("Aucune école trouvée pour cette ville.")

        with col_table:
            st.dataframe(ecoles_ville_1)

        # Afficher les données des points d'intérêt sélectionnés
        if "Gares" in poi_options_ville_1:
            st.write("### Gares")
            gares_data_1 = get_gares_data(bbox)
            if gares_data_1:
                gares_df_1 = pd.DataFrame([
                    {
                        'name': element.get('tags', {}).get('name', 'N/A'),
                        'latitude': element['lat'],
                        'longitude': element['lon']
                    }
                    for element in gares_data_1['elements'] if 'lat' in element and 'lon' in element and 'name' in element.get('tags', {})
                ])
                st.dataframe(gares_df_1)
            else:
                st.warning("Aucune gare trouvée pour cette ville.")

        if "Musées" in poi_options_ville_1:
            st.write("### Musées")
            musees_data_1 = get_musees_data(bbox)
            if musees_data_1:
                musees_df_1 = pd.DataFrame([
                    {
                        'name': element.get('tags', {}).get('name', 'N/A'),
                        'latitude': element['lat'],
                        'longitude': element['lon']
                    }
                    for element in musees_data_1['elements'] if 'lat' in element and 'lon' in element and 'name' in element.get('tags', {})
                ])
                st.dataframe(musees_df_1)
            else:
                st.warning("Aucun musée trouvé pour cette ville.")

        if "Restaurants" in poi_options_ville_1:
            st.write("### Restaurants")
            restaurants_data_1 = get_restaurants_data(bbox)
            if restaurants_data_1:
                restaurants_df_1 = pd.DataFrame([
                    {
                        'name': element.get('tags', {}).get('name', 'N/A'),
                        'latitude': element['lat'],
                        'longitude': element['lon']
                    }
                    for element in restaurants_data_1['elements'] if 'lat' in element and 'lon' in element and 'name' in element.get('tags', {})
                ])
                st.dataframe(restaurants_df_1)
            else:
                st.warning("Aucun restaurant trouvé pour cette ville.")

    # Onglet Ville 2
    with tab3:
        st.header(f"📍 Informations détaillées : {ville_2}")
        wiki_url_2 = f"https://fr.wikipedia.org/wiki/{ville_2.replace(' ', '_')}"
        st.markdown(f"🔗 [Page Wikipédia de {ville_2}]({wiki_url_2})")

        # Afficher la météo pour la ville 2
        st.subheader("Météo actuelle")
        get_weather(data_2['latitude'], data_2['longitude'], "6aea17a766b369d16fdcf84a0b16fdac")

        # Sélecteur pour choisir les points d'intérêt à afficher
        poi_options_ville_2 = st.multiselect(
            "Sélectionnez les points d'intérêt à afficher :",
            ["Gares", "Musées", "Restaurants"],
            key="poi_ville_2"
        )

        # Afficher la carte pour localiser la ville 2
        if "latitude" in data_2 and "longitude" in data_2:
            m = folium.Map(location=[data_2["latitude"], data_2["longitude"]], zoom_start=12)
            folium.Marker(
                location=[data_2["latitude"], data_2["longitude"]],
                popup=ville_2,
                tooltip=ville_2,
                icon=folium.Icon(color="blue")
            ).add_to(m)

            # Récupérer et afficher les données des points d'intérêt sélectionnés
            bbox = f"{data_2['latitude']-0.1},{data_2['longitude']-0.1},{data_2['latitude']+0.1},{data_2['longitude']+0.1}"
            if "Gares" in poi_options_ville_2:
                display_poi_on_map(m, data_2, bbox, "Gares", "green")
            if "Musées" in poi_options_ville_2:
                display_poi_on_map(m, data_2, bbox, "Musées", "purple")
            if "Restaurants" in poi_options_ville_2:
                display_poi_on_map(m, data_2, bbox, "Restaurants", "orange")

            st_folium(m, width=700, height=400)
        else:
            st.warning("Données géographiques manquantes pour cette ville.")

        st.write("### Démographie")
        st.write(f"- Population 2021 : {int(pd.to_numeric(data_2['Population en 2021'], errors='coerce'))}")
        st.write(f"- Naissances 2015-2020 : {data_2['Naissances entre 2015 et 2020']}")
        st.write(f"- Décès 2015-2020 : {data_2['Décès entre 2015 et 2020']}")

        st.write("### Logement")
        st.write(f"- Logements : {int(pd.to_numeric(data_2['Logements en 2021'], errors='coerce'))}")
        st.write(f"- Résidences principales : {data_2['Résidences principales en 2021']}")
        st.write(f"- Vacants : {data_2['Logements vacants en 2021']}")

        st.write("### Emploi et économie")
        st.write(f"- Emplois : {data_2['Emplois au LT en 2021']}")
        st.write(f"- Chômeurs : {data_2['Chômeurs 15-64 ans en 2021']}")
        st.write(f"- Entreprises actives : {data_2['Total des ets actifs fin 2022']}")

        st.write("### Revenus")
        st.write(f"- Taux de pauvreté : {data_2['Taux de pauvreté en 2021']} %")
        st.write(f"- Niveau de vie médian : {data_2['Médiane du niveau vie en 2021']} €")

        # Afficher les écoles pour la ville 2
        st.write("### Établissements scolaires")
        ecoles_ville_2 = df_etablissement[df_etablissement['Numéro Région'] == data_2['Région']]

        # Utiliser des colonnes pour afficher la carte et le tableau côte à côte
        col_map, col_table = st.columns(2)

        with col_map:
            if not ecoles_ville_2.empty:
                m_ecoles = folium.Map(location=[ecoles_ville_2.iloc[0]['latitude_ecole'], ecoles_ville_2.iloc[0]['longitude_ecole']], zoom_start=12)

                for _, ecole in ecoles_ville_2.iterrows():
                    folium.Marker(
                        location=[ecole['latitude_ecole'], ecole['longitude_ecole']],
                        popup=ecole['libellé'],  # Remplacez par le nom de la colonne contenant le nom de l'école
                        icon=folium.Icon(color="green")
                    ).add_to(m_ecoles)

                st_folium(m_ecoles, width=700, height=500)
            else:
                st.warning("Aucune école trouvée pour cette ville.")

        with col_table:
            st.dataframe(ecoles_ville_2)

        # Afficher les données des points d'intérêt sélectionnés
        if "Gares" in poi_options_ville_2:
            st.write("### Gares")
            gares_data_2 = get_gares_data(bbox)
            if gares_data_2:
                gares_df_2 = pd.DataFrame([
                    {
                        'name': element.get('tags', {}).get('name', 'N/A'),
                        'latitude': element['lat'],
                        'longitude': element['lon']
                    }
                    for element in gares_data_2['elements'] if 'lat' in element and 'lon' in element and 'name' in element.get('tags', {})
                ])
                st.dataframe(gares_df_2)
            else:
                st.warning("Aucune gare trouvée pour cette ville.")

        if "Musées" in poi_options_ville_2:
            st.write("### Musées")
            musees_data_2 = get_musees_data(bbox)
            if musees_data_2:
                musees_df_2 = pd.DataFrame([
                    {
                        'name': element.get('tags', {}).get('name', 'N/A'),
                        'latitude': element['lat'],
                        'longitude': element['lon']
                    }
                    for element in musees_data_2['elements'] if 'lat' in element and 'lon' in element and 'name' in element.get('tags', {})
                ])
                st.dataframe(musees_df_2)
            else:
                st.warning("Aucun musée trouvé pour cette ville.")

        if "Restaurants" in poi_options_ville_2:
            st.write("### Restaurants")
            restaurants_data_2 = get_restaurants_data(bbox)
            if restaurants_data_2:
                restaurants_df_2 = pd.DataFrame([
                    {
                        'name': element.get('tags', {}).get('name', 'N/A'),
                        'latitude': element['lat'],
                        'longitude': element['lon']
                    }
                    for element in restaurants_data_2['elements'] if 'lat' in element and 'lon' in element and 'name' in element.get('tags', {})
                ])
                st.dataframe(restaurants_df_2)
            else:
                st.warning("Aucun restaurant trouvé pour cette ville.")

except FileNotFoundError:
    st.error("❌ Fichier non trouvé : data/data_final.xlsx ou data/etablissement.csv")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
