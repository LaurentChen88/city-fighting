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

    # Sélectionner deux villes
    villes = sorted(df["Libellé commune ou ARM"].unique())
    col1, col2 = st.columns(2)

    with col1:
        ville_1 = st.selectbox("📍 Sélectionnez la première ville :", villes)

    with col2:
        ville_2 = st.selectbox("🏙️ Sélectionnez la deuxième ville :", villes, index=1)

    # Extraire les deux villes
    data_1 = df[df["Libellé commune ou ARM"] == ville_1].squeeze()
    data_2 = df[df["Libellé commune ou ARM"] == ville_2].squeeze()

    # Affichage côte à côte
    st.markdown("---")
    st.subheader("🔍 Comparaison graphique")

    left, right = st.columns(2)

    with left:
        st.markdown(f"### {ville_1}")
        st.metric("Population 2021", int(data_1["Population en 2021"]))
        st.metric("Logements en 2021", int(data_1["Logements en 2021"]))
        st.metric("Taux de pauvreté", f"{data_1['Taux de pauvreté en 2021']} %")
        st.metric("Chômeurs 15-64 ans", int(data_1["Chômeurs 15-64 ans en 2021"]))

    with right:
        st.markdown(f"### {ville_2}")
        st.metric("Population 2021", int(data_2["Population en 2021"]))
        st.metric("Logements en 2021", int(data_2["Logements en 2021"]))
        st.metric("Taux de pauvreté", f"{data_2['Taux de pauvreté en 2021']} %")
        st.metric("Chômeurs 15-64 ans", int(data_2["Chômeurs 15-64 ans en 2021"]))

    # Graphique comparatif
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

    # Préparer les données
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

except FileNotFoundError:
    st.error("❌ Fichier non trouvé : `data/base_cc_comparateur.xlsx`")
except Exception as e:
    st.error(f"❌ Erreur : {e}")
