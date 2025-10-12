# relai_http_cache.py
from socket import *
from select import select
import sys
from threading import Thread

if len(sys.argv) != 3:
    print("Usage: python3 relai_http_cache.py <server_ip> <server_port>")
    sys.exit(1)

server_ip = sys.argv[1]
server_port = int(sys.argv[2])

# Serveur d'écoute du relai
relaySocket = socket(AF_INET, SOCK_STREAM)
relaySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 
relaySocket.bind(('', 5012))
relaySocket.listen(7)
print("Relai HTTP avec cache prêt sur le port 5012...")

# Cache en mémoire (dictionnaire URI -> réponse HTTP complète)
http_cache = {}

# La fonction get_uri() récupère l’URI de la requête GET

def get_uri(request_data): 
    try:
        lines = request_data.decode('utf-8').splitlines()
        request_line = lines[0]  # ex: GET /index.html HTTP/1.1
        method, uri, _ = request_line.split()
        if method.upper() == "GET":
            return uri
    except:
        pass
    return None

def gestion_clients(clientSocket, server_ip, server_port):
    try:
        while True:
            data = clientSocket.recv(4096)
            if not data:
                break

            uri = get_uri(data)
            if uri and uri in http_cache:
                # URI déjà en cache -> renvoyer la réponse stockée
                print(f"[CACHE] Renvoi de {uri} au client")
                clientSocket.sendall(http_cache[uri])
                continue

            # Sinon, transmettre au serveur
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.connect((server_ip, server_port))
            serverSocket.sendall(data)

            response = b""
            while True:
                part = serverSocket.recv(4096)
                if not part:
                    break
                response += part

            # Stocker la réponse en cache si URI valide
            if uri:
                http_cache[uri] = response
                print(f"[CACHE] Stockage de {uri}")

            clientSocket.sendall(response)
            serverSocket.close()

    except Exception as e:
        print("Erreur relayage HTTP:", e)
    finally:
        clientSocket.close()
        print("Client déconnecté.")

# Boucle principale pour accepter plusieurs clients
while True:
    clientSocket, clientAddress = relaySocket.accept()
    print("Client connecté :", clientAddress)
    Thread(target=gestion_clients, args=(clientSocket, server_ip, server_port)).start()
