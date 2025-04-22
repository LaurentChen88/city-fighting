import requests

def get_population_by_insee(insee_code):
    """
    Récupère la population d'une commune française à partir de son code INSEE.
    
    Args:
        insee_code (str): Le code INSEE de la commune
        
    Returns:
        dict: Les informations de la commune incluant sa population
        None: Si la commune n'est pas trouvée ou en cas d'erreur
    """
    url = f"https://geo.api.gouv.fr/communes/{insee_code}?fields=nom,code,population"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Génère une exception en cas d'erreur HTTP
        
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête: {e}")
        return None
    except ValueError as e:
        print(f"Erreur lors du décodage JSON: {e}")
        return None

def search_communes_by_name(name):
    """
    Recherche des communes par nom et retourne leurs informations avec population.
    
    Args:
        name (str): Le nom ou partie du nom de la commune
        
    Returns:
        list: Liste des communes correspondantes avec leurs informations
        None: En cas d'erreur
    """
    url = f"https://geo.api.gouv.fr/communes?nom={name}&fields=nom,code,population"
    
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

# Exemple d'utilisation avec un code INSEE
if __name__ == "__main__":
    # Exemple avec Paris (75056)
    insee_code = "75056"
    result = get_population_by_insee(insee_code)
    
    if result:
        print(f"Commune: {result['nom']}")
        print(f"Code INSEE: {result['code']}")
        
        if 'population' in result:
            print(f"Population: {result['population']} habitants")
        else:
            print("Population: Données non disponibles")
    else:
        print(f"Commune avec le code INSEE {insee_code} non trouvée")
    
    # Exemple de recherche par nom
    print("\nRecherche par nom:")
    search_results = search_communes_by_name("Lyon")
    
    if search_results:
        for commune in search_results:
            print(f"{commune['nom']} (INSEE: {commune['code']}): {commune.get('population', 'N/A')} habitants")