from socket import *
import threading
import sys
import re
import json
import time
import os

LOG_FILE = "http_sniffer_log.json"

# Chargement ou création du fichier de log
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        try:
            log_data = json.load(f)
        except:
            log_data = []
else:
    log_data = []

log_lock = threading.Lock()  # pour éviter les conflits entre threads

def save_log():
    global log_data
    with log_lock:
        with open(LOG_FILE, "w") as f:
            json.dump(log_data, f, indent=2)

def handle_client(socketClient, serverName, serverPort, clientAddr):
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((serverName, serverPort))
        print(f"[INFO] Connecté au serveur {serverName}:{serverPort}")

        while True:
            request = socketClient.recv(4096)
            if not request:
                break

            decoded_request = request.decode('utf-8', errors='ignore')
            first_line = decoded_request.splitlines()[0] if decoded_request else ''
            print(f"[CLIENT {clientAddr}] {first_line}")

            # Chercher URI
            match = re.match(r"GET\s+(\S+)\s+HTTP", decoded_request)
            uri = match.group(1) if match else None

            # Envoyer au serveur
            serverSocket.sendall(request)

            # Recevoir la réponse
            response = b""
            serverSocket.settimeout(1)
            try:
                while True:
                    data = serverSocket.recv(4096)
                    if not data:
                        break
                    response += data
            except timeout:
                pass

            # Log si GET et réponse non vide
            if uri and len(response) > 0:
                entry = {
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "client_ip": clientAddr[0],
                    "uri": uri,
                    "response_size": len(response)
                }
                with log_lock:
                    log_data.append(entry)
                save_log()
                print(f"[LOG] {entry}")

            # Renvoyer la réponse au client
            socketClient.sendall(response)

    except Exception as e:
        print(f"[ERREUR] {e}")

    finally:
        socketClient.close()
        serverSocket.close()
        print(f"[INFO] Connexion fermée avec {clientAddr}")

def relai_sniffeur(relay_port, server_name, server_port):
    relaySocket = socket(AF_INET, SOCK_STREAM)
    relaySocket.bind(('', relay_port))
    relaySocket.listen(5)
    print(f"[RELAI] Sniffeur HTTP prêt sur le port {relay_port} → Serveur {server_name}:{server_port}")

    try:
        while True:
            clientSocket, addr = relaySocket.accept()
            print(f"[RELAI] Nouvelle connexion client : {addr}")
            t = threading.Thread(target=handle_client, args=(clientSocket, server_name, server_port, addr))
            t.start()
    except KeyboardInterrupt:
        print("[RELAI] Fermeture demandée.")
    finally:
        relaySocket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage : python relai_sniffeur.py <port_relais> <adresse_serveur> <port_serveur>")
        sys.exit(1)

    relay_port = int(sys.argv[1])
    server_name = sys.argv[2]
    server_port = int(sys.argv[3])
    relai_sniffeur(relay_port, server_name, server_port)