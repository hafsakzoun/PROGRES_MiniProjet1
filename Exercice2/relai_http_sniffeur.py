# relai_http_sniffer.py
from socket import *
from threading import Thread
import sys
from datetime import datetime

if len(sys.argv) != 3:
    print("Usage: python3 relai_http_sniffer.py <server_ip> <server_port>")
    sys.exit(1)

server_ip = sys.argv[1]
server_port = int(sys.argv[2])

# Création du socket d’écoute du relai
relaySocket = socket(AF_INET, SOCK_STREAM)
relaySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
relaySocket.bind(('', 5013))
relaySocket.listen(7)
print("Relai HTTP Sniffer en écoute sur le port 5013...")

# Fichier log
LOG_FILE = "http_sniffer.log"

def log_event(event: str):
    """Écrit un événement dans le fichier de log avec date/heure"""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event}\n")

def get_uri(request_data):
    """Extrait l’URI d’une requête GET"""
    try:
        lines = request_data.decode('utf-8', errors='ignore').splitlines()
        if len(lines) == 0:
            return None
        request_line = lines[0]  # ex: GET /index.html HTTP/1.1
        method, uri, _ = request_line.split()
        if method.upper() == "GET":
            return uri
    except:
        pass
    return None

def gestion_clients(clientSocket, clientAddress, server_ip, server_port):
    try:
        while True:
            data = clientSocket.recv(4096)
            if not data:
                break

            uri = get_uri(data)
            if uri:
                log_event(f"CLIENT {clientAddress[0]} a demandé URI: {uri}")

            # Transfert de la requête au serveur
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.connect((server_ip, server_port))
            serverSocket.sendall(data)

            # Réception de la réponse
            response = b""
            while True:
                part = serverSocket.recv(4096)
                if not part:
                    break
                response += part

            # Log de la réponse si non vide
            if uri and len(response) > 0:
                log_event(f"Réponse reçue du serveur pour {uri} (Client: {clientAddress[0]}, Taille: {len(response)} octets)")

            # Renvoi au client
            clientSocket.sendall(response)
            serverSocket.close()

    except Exception as e:
        print("Erreur dans le relai:", e)
    finally:
        clientSocket.close()
        print("Client déconnecté :", clientAddress)

# Boucle principale
while True:
    clientSocket, clientAddress = relaySocket.accept()
    print("Client connecté :", clientAddress)
    Thread(target=gestion_clients, args=(clientSocket, clientAddress, server_ip, server_port)).start()