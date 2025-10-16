from socket import *
import threading
import sys
import os
from urllib.parse import urlparse

WWW_DIR = "files"  # dossier contenant les fichiers à servir

def handle_client(connectionSocket, addr):
    print(f"[SERVEUR] Connexion établie avec {addr}")
    try:
        while True: #si on a plusieurs requêtes sur la même connexion
            request = connectionSocket.recv(4096).decode('utf-8', errors='ignore')
            if not request:
                return

            # Extraire la ligne GET
            request_line = request.splitlines()[0]
            print(f"[SERVEUR] {request_line}")
            
            parts = request_line.split()
            if len(parts) < 2 or parts[0] != "GET":
                response = "HTTP/1.1 400 Bad Request\r\n\r\nBad Request"
                connectionSocket.sendall(response.encode('utf-8'))
                return

            # Extraire le chemin à partir d'une URI complète (support proxy)
            uri = parts[1]
            parsed = urlparse(uri)
            path = parsed.path
            if path == "/":
                path = "/index.html"

            filepath = os.path.join(WWW_DIR, path.lstrip("/"))

            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    body = f.read()
                response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + body
            else:
                response = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"

            connectionSocket.sendall(response)
            
    except OSError as e:
        print(f"Erreur réseau: {e}")
    finally:
        connectionSocket.close()
        print(f"[SERVEUR] Connexion fermée avec {addr}")

def serveur_http(port):
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', port))
        serverSocket.listen(5)
        print(f"[SERVEUR] HTTP prêt sur le port {port}")

        while True:
            connectionSocket, addr = serverSocket.accept()
            thread = threading.Thread(target=handle_client, args=(connectionSocket, addr))
            thread.start()

    except OSError as e:
        print(f"Erreur réseau: {e}")
    
    except gaierror:
        print("Erreur liée à l'adresse")
    
    except timeout:
        print("Délai d'attente expiré")

    finally:
        serverSocket.close()
        print("[SERVEUR] Fermé")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python serveur_http.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    serveur_http(port)