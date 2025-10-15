from socket import *
import threading
import sys
import re
import time
import json
import base64
import os

CACHE_FILE = "cache.json"
TTL = 60  # secondes

# Dictionnaire global pour le cache
# Format : { uri: { "response": bytes, "timestamp": float } }
cache = {}

# ------------------------- Fonctions de persistance -------------------------
def load_cache():
    global cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                for uri, value in data.items():
                    # Décoder le contenu base64 en bytes
                    cache[uri] = {
                        "response": base64.b64decode(value["response"]),
                        "timestamp": value["timestamp"]
                    }
            print(f"[INFO] Cache chargé depuis {CACHE_FILE} ({len(cache)} entrées)")
        except Exception as e:
            print(f"[ERREUR] Chargement du cache : {e}")


def save_cache():
    global cache
    try:
        data_to_save = {}
        for uri, value in cache.items():
            data_to_save[uri] = {
                "response": base64.b64encode(value["response"]).decode('utf-8'),
                "timestamp": value["timestamp"]
            }
        with open(CACHE_FILE, "w") as f:
            json.dump(data_to_save, f)
        print(f"[INFO] Cache sauvegardé dans {CACHE_FILE} ({len(cache)} entrées)")
    except Exception as e:
        print(f"[ERREUR] Sauvegarde du cache : {e}")

# ------------------------- Gestion client -------------------------
def handle_client(socketClient, serverName, serverPort):
    global cache
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((serverName, serverPort))
        print(f"[INFO] Connecté au serveur {serverName}:{serverPort}")

        while True:
            request = socketClient.recv(4096)
            if not request:
                print("[INFO] Client déconnecté.")
                break

            decoded_request = request.decode('utf-8', errors='ignore')
            first_line = decoded_request.splitlines()[0] if decoded_request else ''
            print(f"[CLIENT] {first_line}")

            match = re.match(r"GET\s+(\S+)\s+HTTP", decoded_request)
            if match:
                uri = match.group(1)
                print(f"[CACHE] URI demandée : {uri}")

                # Vérifier si dans le cache et TTL
                if uri in cache:
                    age = time.time() - cache[uri]["timestamp"]
                    if age < TTL:
                        print(f"[CACHE] Réponse trouvée pour {uri} (âge {int(age)}s), envoi direct.")
                        socketClient.sendall(cache[uri]["response"])
                        continue
                    else:
                        print(f"[CACHE] {uri} expirée (âge {int(age)}s), suppression du cache.")
                        del cache[uri]

                # Pas en cache → envoyer au serveur
                print(f"[CACHE] {uri} non trouvée, requête transmise au serveur.")
                serverSocket.sendall(request)

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

                if response:
                    cache[uri] = {"response": response, "timestamp": time.time()}
                    save_cache()
                    print(f"[CACHE] Réponse stockée pour {uri} (taille: {len(response)} octets)")

                socketClient.sendall(response)

            else:
                # Pas une requête GET → simple relais
                serverSocket.sendall(request)
                response = serverSocket.recv(4096)
                socketClient.sendall(response)

    except Exception as e:
        print(f"[ERREUR] {e}")

    finally:
        socketClient.close()
        serverSocket.close()
        print("[INFO] Connexion fermée.")

# ------------------------- Serveur relai -------------------------
def relai(relay_port, server_name, server_port):
    try:
        relaySocket = socket(AF_INET, SOCK_STREAM)
        relaySocket.bind(('', relay_port))
        relaySocket.listen(5)
        print(f"[RELAI] Prêt sur le port {relay_port} → Serveur {server_name}:{server_port}")

        while True:
            clientSocket, addr = relaySocket.accept()
            print(f"[RELAI] Nouvelle connexion client : {addr}")
            client_thread = threading.Thread(target=handle_client, args=(clientSocket, server_name, server_port))
            client_thread.start()

    except Exception as e:
        print(f"[ERREUR RELAI] {e}")

    finally:
        relaySocket.close()
        print("[RELAI] Fermé.")

# ------------------------- Main -------------------------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage : python relai_cache_persist.py <port_relais> <adresse_serveur> <port_serveur>")
        sys.exit(1)
    
    load_cache()
    relay_port = int(sys.argv[1])
    server_name = sys.argv[2]
    server_port = int(sys.argv[3])
    relai(relay_port, server_name, server_port)