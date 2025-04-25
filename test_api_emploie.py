import streamlit as st
import requests
from datetime import datetime

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
def get_job_offers(query, commune, departement, region, access_token, type_contrat=None, publiee_depuis=None):
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'motsCles': query,
        'commune': commune,
        'departement': departement,
        'region': region,
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
    else:
        st.error(f"Erreur {response.status_code} : {response.text}")
        return None

# --- Streamlit App ---
st.subheader("Recherche d'offres d'emploi - France Travail")

query = st.text_input("Poste recherché", "Data Analyst")
location = st.text_input("Code INSEE", "75101")

# Renseigne ici tes propres identifiants
client_id = st.secrets.get("client_id", "PAR_outildecisionnel_54f7361a496d42854e4356df6568a5346eba4b9468c9b0067add09ba9f318a4c")
client_secret = st.secrets.get("client_secret", "0c1a9a6ed2afcc5f1a730e0a1a747dfc8cd81d039ec95005f851bac1e206d216")

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
    access_token = get_access_token(client_id, client_secret)

    if access_token:
        job_offers = get_job_offers(query, location, access_token, type_contrat, publiee_depuis)

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
                st.warning("Aucune offre d'emploi trouvée.")
        else:
            st.error("Erreur lors de la récupération des offres.")
