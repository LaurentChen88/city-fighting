import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration
st.set_page_config(
    page_title="Comparateur de villes - City Fighting",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ Comparateur de deux villes")

# Charger les données
file_path = "data/base_cc_comparateur.xlsx"

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
            st.metric("Population 2021", int(data_1["Population en 2021"]))
            st.metric("Logements en 2021", int(data_1["Logements en 2021"]))
            st.metric("Taux de pauvreté", f"{data_1['Taux de pauvreté en 2021']} %")
            st.metric("Chômeurs 15-64 ans", int(data_1["Chômeurs 15-64 ans en 2021"]))

        with col_right:
            st.markdown(f"### {ville_2}")
            st.metric("Population 2021", int(data_2["Population en 2021"]))
            st.metric("Logements en 2021", int(data_2["Logements en 2021"]))
            st.metric("Taux de pauvreté", f"{data_2['Taux de pauvreté en 2021']} %")
            st.metric("Chômeurs 15-64 ans", int(data_2["Chômeurs 15-64 ans en 2021"]))

        st.markdown("---")
        st.subheader("📊 Graphe comparatif")

        variables_a_comparer = {
            "Population en 2021": "Population",
            "Logements en 2021": "Logements",
            "Chômeurs 15-64 ans en 2021": "Chômage",
            "Taux de pauvreté en 2021": "Pauvreté (%)",
            "Emplois au LT en 2021": "Emplois",
            "Médiane du niveau vie en 2021": "Niveau de vie (€)",
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

    # Onglet ville 1
    with tab2:
        st.header(f"📍 Informations détaillées : {ville_1}")
        st.write("### Démographie")
        st.write(f"- Population 2021 : {int(data_1['Population en 2021'])}")
        st.write(f"- Naissances 2015-2020 : {data_1['Naissances entre 2015 et 2020']}")
        st.write(f"- Décès 2015-2020 : {data_1['Décès entre 2015 et 2020']}")

        st.write("### Logement")
        st.write(f"- Logements : {int(data_1['Logements en 2021'])}")
        st.write(f"- Résidences principales : {data_1['Résidences principales en 2021']}")
        st.write(f"- Vacants : {data_1['Logements vacants en 2021']}")

        st.write("### Emploi et économie")
        st.write(f"- Emplois : {data_1['Emplois au LT en 2021']}")
        st.write(f"- Chômeurs : {data_1['Chômeurs 15-64 ans en 2021']}")
        st.write(f"- Entreprises actives : {data_1['Total des ets actifs fin 2022']}")

        st.write("### Revenus")
        st.write(f"- Taux de pauvreté : {data_1['Taux de pauvreté en 2021']} %")
        st.write(f"- Niveau de vie médian : {data_1['Médiane du niveau vie en 2021']} €")

    # Onglet ville 2
    with tab3:
        st.header(f"📍 Informations détaillées : {ville_2}")
        st.write("### Démographie")
        st.write(f"- Population 2021 : {int(data_2['Population en 2021'])}")
        st.write(f"- Naissances 2015-2020 : {data_2['Naissances entre 2015 et 2020']}")
        st.write(f"- Décès 2015-2020 : {data_2['Décès entre 2015 et 2020']}")

        st.write("### Logement")
        st.write(f"- Logements : {int(data_2['Logements en 2021'])}")
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
    st.error("❌ Fichier non trouvé : `data/base_cc_comparateur.xlsx`")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
