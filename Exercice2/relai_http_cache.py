from socket import *
import threading
import sys
import re
import time
import json
import base64
import os

CACHE_FILE = "cache.json"
TTL = 60  # durée de vie d’une réponse dans le cache en secondes

# Dictionnaire global pour le cache
# Format : { uri: { "response": bytes, "timestamp": float } }
cache = {}

# ------------------------- Fonctions de persistance -------------------------
def load_cache():
    """
    Charge le cache depuis un fichier JSON (si le fichier existe)
    Les réponses sont stockées en base64 pour pouvoir les sauver dans JSON
    """
    global cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                for uri, value in data.items():
                    cache[uri] = {
                        "response": base64.b64decode(value["response"]),
                        "timestamp": value["timestamp"],
                        "content_type": value.get("content_type", "unknown")
                    }
            print(f"[INFO] Cache chargé depuis {CACHE_FILE} ({len(cache)} entrées)")
        except Exception as e:
            print(f"[ERREUR] Chargement du cache : {e}")


def save_cache():
    """
    Sauvegarde le cache courant dans un fichier JSON.
    Les réponses en bytes sont encodées en base64 pour la compatibilité JSON
    """
    global cache
    try:
        data_to_save = {}
        for uri, value in cache.items():
            data_to_save[uri] = {
                "response": base64.b64encode(value["response"]).decode('utf-8'),
                "timestamp": value["timestamp"],
                "content_type": value.get("content_type", "unknown")
            }
        with open(CACHE_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)
        print(f"[INFO] Cache sauvegardé dans {CACHE_FILE} ({len(cache)} entrées)")
    except Exception as e:
        print(f"[ERREUR] Sauvegarde du cache : {e}")

# ------------------------- Gestion client -------------------------
def handle_client(socketClient, serverName, serverPort):
    """
    Fonction qui gère la communication
    """
    global cache
    try:        
        # Connexion au serveur final
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((serverName, serverPort))
        print(f"[INFO] Connecté au serveur {serverName}:{serverPort}")

        while True:
            # Réception de la requête du client
            request = socketClient.recv(4096)
            if not request:
                print("[INFO] Client déconnecté.")
                break

            decoded_request = request.decode('utf-8', errors='ignore')
            first_line = decoded_request.splitlines()[0] if decoded_request else ''
            print(f"[CLIENT] {first_line}")
            
            # Vérifier si c'est une requête GET
            match = re.match(r"GET\s+(\S+)\s+HTTP", decoded_request)
            if match:
                uri = match.group(1)
                print(f"[CACHE] URI demandée : {uri}")

                # Vérifier si la réponse est déjà en cache et non expirée
                if uri in cache:
                    age = time.time() - cache[uri]["timestamp"]
                    if age < TTL:
                        # Réponse trouvée dans le cache → on la renvoie directement
                        print(f"[CACHE] Réponse trouvée pour {uri} (âge {int(age)}s), envoi direct.")
                        socketClient.sendall(cache[uri]["response"])
                        continue
                    else:
                        # Cache expiré → suppression
                        print(f"[CACHE] {uri} expirée (âge {int(age)}s), suppression du cache.")
                        del cache[uri]

                # Pas en cache → envoyer au serveur
                print(f"[CACHE] {uri} non trouvée, requête transmise au serveur.")
                serverSocket.sendall(request)
                # Réception de la réponse complète du serveur
                response = b""
                serverSocket.settimeout(1)
                try:
                    while True:
                        data = serverSocket.recv(4096)
                        if not data:
                            break
                        response += data
                except timeout:
                    # Timeout → fin de la réception
                    pass
                # Stocker la réponse dans le cache
                if response:
                    # Extraire le type de contenu depuis les headers HTTP
                    content_type = "unknown"
                    headers_end = response.find(b"\r\n\r\n")
                    if headers_end != -1:
                        headers = response[:headers_end].decode('utf-8', errors='ignore')
                        match = re.search(r"Content-Type:\s*([^\r\n]+)", headers, re.IGNORECASE)
                        if match:
                            content_type = match.group(1).strip()

                    # Normaliser l'URI pour le cache (toujours chemin relatif)
                    normalized_uri = re.sub(r"^http://[^/]+", "", uri)

                    cache[normalized_uri] = {
                        "response": response,
                        "timestamp": time.time(),
                        "content_type": content_type
                    }
                    save_cache()
                    print(f"[CACHE] Réponse stockée pour {normalized_uri} ({len(response)} octets, type: {content_type})")
                # Transmettre la réponse au client
                socketClient.sendall(response)

            else:
                #Pour les autres requêtes HTTP, simple relais
                serverSocket.sendall(request)
                response = serverSocket.recv(4096)
                socketClient.sendall(response)

    except Exception as e:
        print(f"[ERREUR] {e}")

    finally:
        # Fermeture des connexions
        socketClient.close()
        serverSocket.close()
        print("[INFO] Connexion fermée.")

# ------------------------- Serveur relai -------------------------
def relai(relay_port, server_name, server_port):
    """
    Serveur relais multi-threadé
    Écoute sur relay_port et crée un thread par client
    Chaque thread appelle handle_client pour gérer la communication
    """
    try:
        relaySocket = socket(AF_INET, SOCK_STREAM)
        relaySocket.bind(('', relay_port))
        relaySocket.listen(5)
        print(f"[RELAI] Prêt sur le port {relay_port} → Serveur {server_name}:{server_port}")

        while True:
            clientSocket, addr = relaySocket.accept()
            print(f"[RELAI] Nouvelle connexion client : {addr}")
            # Thread pour gérer le client indépendamment
            client_thread = threading.Thread(target=handle_client, args=(clientSocket, server_name, server_port))
            client_thread.start()

    except Exception as e:
        print(f"[ERREUR RELAI] {e}")

    finally:
        relaySocket.close()
        print("[RELAI] Fermé.")

# ------------------------- Main -------------------------
if __name__ == "__main__":
    # Vérification des arguments : <port_relais> <adresse_serveur> <port_serveur>
    if len(sys.argv) != 4:
        print("Usage : python relai_cache_persist.py <port_relais> <adresse_serveur> <port_serveur>")
        sys.exit(1)

    # Charger le cache au démarrage
    load_cache()
    relay_port = int(sys.argv[1])
    server_name = sys.argv[2]
    server_port = int(sys.argv[3])
    
    # Lancer le serveur relai
    relai(relay_port, server_name, server_port)