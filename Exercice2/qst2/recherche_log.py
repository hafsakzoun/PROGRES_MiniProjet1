import sys
import re

LOG_FILE = "http_sniffer.log"

def search_uri(search_term):
    clients = set()

    with open(LOG_FILE, "r") as log:
        for line in log:
            # On cherche les lignes avec une URI correspondante et une réponse non vide
            match = re.search(r"CLIENT=(\S+)\s+URI=(\S+)\s+RESPONSE_SIZE=(\d+)", line)
            if match:
                client_ip, uri, size = match.groups()
                size = int(size)
                if search_term in uri and size > 0:
                    clients.add((client_ip, uri, size))

    if clients:
        print(f"=== Résultats pour '{search_term}' ===")
        for client_ip, uri, size in clients:
            print(f"Client {client_ip} → URI {uri} ({size} octets)")
    else:
        print(f"Aucun résultat trouvé pour '{search_term}'.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python3 recherche_log.py <mot_ou_URI>")
        sys.exit(1)

    search_term = sys.argv[1]
    search_uri(search_term)