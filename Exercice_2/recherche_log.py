import sys
import json

LOG_FILE = "http_sniffer_log.json"

def search_uri(search_term):
    """
    Recherche dans le fichier JSON des entrées dont l'URI contient search_term
    et dont la taille de réponse est > 0. Affiche les résultats uniques.
    """
    try:
        # Ouvre et charge le fichier JSON contenant les logs
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)
    except FileNotFoundError:
        # Gestion si le fichier n'existe pas
        print(f"Le fichier {LOG_FILE} est introuvable.")
        return
    except json.JSONDecodeError:
        # Gestion si le fichier n'est pas un JSON valide
        print(f"Erreur lors de la lecture du fichier {LOG_FILE}.")
        return

    # Utiliser un set pour éviter les doublons (même IP/URI/taille)
    results = set()

    # Parcours chaque entrée du log (chaque entrée est un dict)
    for entry in log_data:
        uri = entry.get("uri", "")                 # récupérer l'URI (ou chaîne vide)
        size = entry.get("response_size", 0)      # récupérer la taille de la réponse
        client_ip = entry.get("client_ip", "")    # récupérer l'IP du client
        # Si le terme recherché est dans l'URI et que la réponse n'est pas vide
        if search_term in uri and size > 0:
            results.add((client_ip, uri, size))  # ajouter au set de résultats

    # Affichage des résultats triés 
    if results:
        print(f"=== Résultats pour '{search_term}' ===")
        for client_ip, uri, size in sorted(results):
            # Affiche sous la forme : Client <IP> → URI <uri> (<taille> octets)
            print(f"Client {client_ip} → URI {uri} ({size} octets)")
    else:
        # Aucun résultat trouvé
        print(f"Aucun résultat trouvé pour '{search_term}'.")

if __name__ == "__main__":
    # Vérifie qu'un seul argument (le terme de recherche) a été fourni
    if len(sys.argv) != 2:
        print("Usage : python3 recherche_log.py <mot_ou_URI>")
        sys.exit(1)

    # Récupère le terme de recherche depuis la ligne de commande
    search_term = sys.argv[1]
    search_uri(search_term)