import sys
import json

LOG_FILE = "http_sniffer_log.json"

def search_uri(search_term):
    try:
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)
    except FileNotFoundError:
        print(f"Le fichier {LOG_FILE} est introuvable.")
        return
    except json.JSONDecodeError:
        print(f"Erreur lors de la lecture du fichier {LOG_FILE}.")
        return

    # Stocker les résultats uniques
    results = set()

    for entry in log_data:
        uri = entry.get("uri", "")
        size = entry.get("response_size", 0)
        client_ip = entry.get("client_ip", "")
        if search_term in uri and size > 0:
            results.add((client_ip, uri, size))

    if results:
        print(f"=== Résultats pour '{search_term}' ===")
        for client_ip, uri, size in sorted(results):
            print(f"Client {client_ip} → URI {uri} ({size} octets)")
    else:
        print(f"Aucun résultat trouvé pour '{search_term}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python3 recherche_log.py <mot_ou_URI>")
        sys.exit(1)

    search_term = sys.argv[1]
    search_uri(search_term)
