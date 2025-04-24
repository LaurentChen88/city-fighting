import streamlit as st
import pandas as pd
import requests

# Fonction pour récupérer les offres d'emploi depuis l'API Adzuna
def get_job_offers(query, location, api_key):
    url = "https://api.adzuna.com/v1/api/jobs"
    params = {
        'app_id': api_key,
        'app_key': api_key,
        'what': query,
        'where': location,
        'results_per_page': 10,  # Limite le nombre de résultats
        'sort_by': 'date'  # Trier par date
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur lors de la récupération des offres d'emploi : {response.status_code}")
        return None

# Interface utilisateur pour saisir les critères de recherche
st.title("Recherche d'offres d'emploi")

query = st.text_input("Poste recherché", "Développeur Python")
location = st.text_input("Lieu", "Paris")
api_key = "64901f5cac19a00a72a0867f6f1791eb"  # Utilisez la clé API fournie

if st.button("Rechercher"):
    job_offers = get_job_offers(query, location, api_key)

    if job_offers:
        jobs = job_offers.get('results', [])
        if jobs:
            df = pd.DataFrame(jobs)
            st.dataframe(df[['title', 'company', 'location', 'description', 'redirect_url']])
        else:
            st.warning("Aucune offre d'emploi trouvée.")
    else:
        st.error("Erreur lors de la récupération des offres d'emploi.")
