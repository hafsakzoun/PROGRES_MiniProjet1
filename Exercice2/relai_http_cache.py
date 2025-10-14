from socket import *
import threading
import sys

# Cache global (clé = URI, valeur = réponse HTTP complète)
cache = {}

def handle_client(socketClient, serverName, serverPort):
    '''Gère la requête HTTP d’un client avec un mécanisme de cache'''
    try:
        # Créer une socket vers le serveur HTTP distant
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((serverName, serverPort))
        print(f"Connecté au serveur HTTP {serverName}:{serverPort}")

        # Réception de la requête HTTP du client
        request = socketClient.recv(4096)
        if not request:
            print("Client déconnecté sans envoyer de requête.")
            return

        # Décoder pour lire la première ligne de la requête
        request_str = request.decode('utf-8', errors='ignore')
        print(f"Requête reçue :\n{request_str.splitlines()[0]}")

        # Extraire l'URI à partir de la ligne GET
        uri = None
        for line in request_str.splitlines():
            if line.startswith("GET"):
                parts = line.split()
                if len(parts) >= 2:
                    uri = parts[1]
                    break

        if not uri:
            print("Aucune URI trouvée dans la requête.")
            return

        # Vérifier si la ressource est déjà dans le cache
        if uri in cache:
            print(f"[CACHE HIT] Envoi de la ressource '{uri}' depuis le cache")
            socketClient.sendall(cache[uri])
        else:
            print(f"[CACHE MISS] Récupération de '{uri}' depuis le serveur")

            # Transmettre la requête au serveur HTTP
            serverSocket.sendall(request)

            # Réception de la réponse complète
            response_chunks = []
            while True:
                data = serverSocket.recv(4096)
                if not data:
                    break
                response_chunks.append(data)

            response = b"".join(response_chunks)

            # Stocker dans le cache
            cache[uri] = response
            print(f"Ressource '{uri}' mise en cache (taille : {len(response)} octets)")

            # Transmettre la réponse au client
            socketClient.sendall(response)

    except Exception as e:
        print(f"Erreur: {e}")

    finally:
        socketClient.close()
        serverSocket.close()
        print("Connexion fermée")


def relai(relay_port, server_name, server_port):
    '''Relai HTTP avec cache'''
    try:
        relaySocket = socket(AF_INET, SOCK_STREAM)
        relaySocket.bind(('', relay_port))
        relaySocket.listen(5)
        print(f"Relai HTTP avec cache actif sur le port {relay_port}, relié au serveur {server_name}:{server_port}")

        while True:
            clientSocket, addr = relaySocket.accept()
            print(f"Nouvelle connexion client : {addr}")

            # Thread pour chaque client
            thread = threading.Thread(target=handle_client, args=(clientSocket, server_name, server_port))
            thread.start()

    except Exception as e:
        print(f"Erreur réseau : {e}")

    finally:
        relaySocket.close()
        print("Relai fermé")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage : python3 relai_cache.py <port_relais> <serveur_http> <port_http>")
        sys.exit(1)

    relay_port = int(sys.argv[1])
    server_name = sys.argv[2]
    server_port = int(sys.argv[3])
    relai(relay_port, server_name, server_port)