import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Configuration de la page
st.set_page_config(
    page_title="Comparateur de villes - City Fighting",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ Comparateur de deux villes")

# Chargement des données
file_path = "data/data_final.xlsx"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

try:
    df = load_data(file_path)

    # Sélection des villes
    villes = sorted(df["Libellé commune ou ARM"].unique())
    col1, col2 = st.columns(2)
    with col1:
        ville_1 = st.selectbox("📍 Sélectionnez la première ville :", villes)
    with col2:
        ville_2 = st.selectbox("🏙️ Sélectionnez la deuxième ville :", villes, index=1)

    data_1 = df[df["Libellé commune ou ARM"] == ville_1].squeeze()
    data_2 = df[df["Libellé commune ou ARM"] == ville_2].squeeze()

    # Onglets
    tab1, tab2, tab3 = st.tabs(["🔍 Comparatif global", f"🏘️ {ville_1}", f"🏘️ {ville_2}"])

    with tab1:
        st.subheader("🔍 Comparaison graphique")

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"### {ville_1}")
            # Conversion des valeurs en nombres, avec gestion des erreurs
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
            # Conversion des valeurs en nombres, avec gestion des erreurs
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
            "Taux de pauvreté en 2021": "Pauvreté (%)",
            "Emplois au LT en 2021": "Emplois",
            "Médiane du niveau vie en 2021": "Niveau de vie (€)",
            "Naissances entre 2015 et 2020": "Naissances",
            "Décès entre 2015 et 2020": "Décès",
            "Résidences principales en 2021": "Résidences principales",
            "Logements vacants en 2021": "Logements vacants",
            "Total des ets actifs fin 2022": "Entreprises actives",
        }

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
        st.plotly_chart(fig, use_container_width=True)

        # Compteur des variables supérieures (seulement pour les variables positives)
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

    # Onglet Ville 1
    with tab2:
        st.header(f"📍 Informations détaillées : {ville_1}")

        # Carte
        if "latitude" in data_1 and "longitude" in data_1:
            m = folium.Map(location=[data_1["latitude"], data_1["longitude"]], zoom_start=12)
            folium.Marker(
                location=[data_1["latitude"], data_1["longitude"]],
                popup=ville_1,
                tooltip=ville_1,
            ).add_to(m)
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

    # Onglet Ville 2
    with tab3:
        st.header(f"📍 Informations détaillées : {ville_2}")

        # Carte
        if "latitude" in data_2 and "longitude" in data_2:
            m = folium.Map(location=[data_2["latitude"], data_2["longitude"]], zoom_start=12)
            folium.Marker(
                location=[data_2["latitude"], data_2["longitude"]],
                popup=ville_2,
                tooltip=ville_2,
            ).add_to(m)
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

except FileNotFoundError:
    st.error("❌ Fichier non trouvé : `data/data_final.xlsx`")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
