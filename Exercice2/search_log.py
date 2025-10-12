# search_log.py
import re

LOG_FILE = "http_sniffer.log"

def search_uri(uri_part):
    """Recherche les IPs associées à une URI (ou partie d’URI)"""
    clients = set()
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # Si une réponse correspond à l’URI recherchée
        if "Réponse reçue du serveur" in line and uri_part in line:
            # Extraire l’adresse IP du client
            match = re.search(r"Client:\s*([\d\.]+)", line)
            if match:
                clients.add(match.group(1))

    if clients:
        print(f"Clients ayant obtenu une réponse pour '{uri_part}':")
        for ip in clients:
            print(f" - {ip}")
    else:
        print(f"Aucun client trouvé pour '{uri_part}'.")

if __name__ == "__main__":
    uri = input("Entrez l'URI (ou partie d'URI) à rechercher : ")
    search_uri(uri)