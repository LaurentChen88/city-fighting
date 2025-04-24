import requests

# Tes identifiants (garde-les secrets !)
CLIENT_ID = "PAR_outilsdecisionelles_b7ed50ac86b64973399624b7e2b3155393543b849201e6baa037c1f41abea586"
CLIENT_SECRET = "714f239d37ea74a95529b2b84d03ad92d5347c5c3155f6d1a641829041f25a55"

# 1. Récupérer le token d'accès
auth_url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
auth_data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "api_offresdemploiv2 o2dsoffre"
}

auth_response = requests.post(auth_url, data=auth_data)
access_token = auth_response.json().get("access_token")

# 2. Effectuer une recherche d'offres
headers = {
    "Authorization": f"Bearer {access_token}"
}

params = {
    "motsCles": "developpeur",
    "lieu": "Paris",
    "distance": 10,
    "nombreResultats": 5
}

search_url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
response = requests.get(search_url, headers=headers, params=params)

# 3. Afficher les résultats
offres = response.json().get("resultats", [])

for offre in offres:
    print(f"📌 Titre : {offre['intitule']}")
    print(f"📍 Lieu : {offre['lieuLibelle']}")
    print(f"🏢 Entreprise : {offre.get('entreprise', {}).get('nom')}")
    print(f"🔗 Lien : {offre['origineOffre']['urlOrigine']}")
    print("-" * 50)
