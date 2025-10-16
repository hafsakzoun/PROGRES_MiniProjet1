from socket import *
import threading
import sys
import re
import json
import time
import os

LOG_FILE = "http_sniffer_log.json"
log_lock = threading.Lock()  # pour éviter les conflits entre threads

# Charger ou initialiser le log
if os.path.exists(LOG_FILE):
    try:
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        log_data = []
else:
    log_data = []

def save_log():
    """Sauvegarde le log JSON de manière thread-safe"""
    with log_lock:
        with open(LOG_FILE, "w") as f:
            json.dump(log_data, f, indent=2)

def handle_client(client_socket, server_name, server_port, client_addr):
    """Gère la communication entre un client et le serveur HTTP"""
    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.connect((server_name, server_port))
        print(f"[INFO] Connecté au serveur {server_name}:{server_port}")

        while True:
            request = client_socket.recv(4096)
            if not request:
                break

            decoded_request = request.decode('utf-8', errors='ignore')
            first_line = decoded_request.splitlines()[0] if decoded_request else ''
            print(f"[CLIENT {client_addr}] {first_line}")

            # Vérifier si c'est un GET
            match = re.match(r"GET\s+(\S+)\s+HTTP", decoded_request)
            uri = match.group(1) if match else None

            # Transmettre la requête au serveur
            server_socket.sendall(request)

            # Recevoir la réponse complète
            response = b""
            server_socket.settimeout(1)
            try:
                while True:
                    data = server_socket.recv(4096)
                    if not data:
                        break
                    response += data
            except timeout:
                pass

            # Enregistrer dans le log si GET et réponse non vide
            if uri and len(response) > 0:
                entry = {
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "client_ip": client_addr[0],
                    "uri": uri,
                    "response_size": len(response)
                }
                with log_lock:
                    log_data.append(entry)
                save_log()
                print(f"[LOG] {entry}")

            # Renvoyer la réponse au client
            client_socket.sendall(response)

    except Exception as e:
        print(f"[ERREUR] {e}")

    finally:
        client_socket.close()
        server_socket.close()
        print(f"[INFO] Connexion fermée avec {client_addr}")

def relai_sniffeur(relay_port, server_name, server_port):
    """Démarre le relai HTTP sniffeur multithread"""
    relay_socket = socket(AF_INET, SOCK_STREAM)
    relay_socket.bind(('', relay_port))
    relay_socket.listen(5)
    print(f"[RELAI] Sniffeur HTTP prêt sur le port {relay_port} → Serveur {server_name}:{server_port}")

    try:
        while True:
            client_socket, addr = relay_socket.accept()
            print(f"[RELAI] Nouvelle connexion client : {addr}")
            t = threading.Thread(target=handle_client, args=(client_socket, server_name, server_port, addr))
            t.start()
    except KeyboardInterrupt:
        print("[RELAI] Fermeture demandée.")
    finally:
        relay_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage : python relai_sniffeur.py <port_relais> <adresse_serveur> <port_serveur>")
        sys.exit(1)

    relay_port = int(sys.argv[1])
    server_name = sys.argv[2]
    server_port = int(sys.argv[3])
    relai_sniffeur(relay_port, server_name, server_port)