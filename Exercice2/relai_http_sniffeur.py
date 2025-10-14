from socket import *
import threading
import sys
import datetime
import re

LOG_FILE = "http_sniffer.log"
lock = threading.Lock()  # Pour éviter les écritures simultanées dans le log


def log_event(client_ip, uri, response_size):
    """Écrit dans le fichier de log un événement HTTP GET et la réponse correspondante."""
    with lock:
        with open(LOG_FILE, "a") as log:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"[{timestamp}] CLIENT={client_ip} URI={uri} RESPONSE_SIZE={response_size}\n")


def handle_client(clientSocket, serverName, serverPort, client_addr):
    """Relai TCP qui agit comme sniffeur HTTP"""
    try:
        # Connexion au serveur distant
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((serverName, serverPort))

        while True:
            # Récupérer la requête du client
            request = clientSocket.recv(4096)
            if not request:
                break

            # Décoder la requête pour trouver l’URI du GET
            try:
                request_str = request.decode('utf-8', errors='ignore')
                match = re.search(r"GET\s+(\S+)\s+HTTP", request_str)
                if match:
                    uri = match.group(1)
                    print(f"[GET] Client {client_addr[0]} a demandé {uri}")
                    log_event(client_addr[0], uri, response_size=0)  # réponse encore inconnue
                else:
                    uri = None
            except Exception:
                uri = None

            # Transmettre la requête au serveur distant
            serverSocket.sendall(request)

            # Réception de la réponse du serveur
            response = b""
            while True:
                data = serverSocket.recv(4096)
                if not data:
                    break
                response += data

                # Envoyer la réponse au client au fur et à mesure
                clientSocket.sendall(data)

            # Si c’est une réponse à un GET et qu’elle n’est pas vide, on logue sa taille
            if uri and len(response) > 0:
                print(f"[RESP] Réponse non vide ({len(response)} octets) pour {uri}")
                log_event(client_addr[0], uri, len(response))

    except Exception as e:
        print(f"Erreur : {e}")

    finally:
        clientSocket.close()
        serverSocket.close()
        print(f"Connexion fermée avec {client_addr}")


def relai(port_relais, server_name, server_port):
    """Relai TCP agissant comme sniffeur HTTP"""
    try:
        relaySocket = socket(AF_INET, SOCK_STREAM)
        relaySocket.bind(('', port_relais))
        relaySocket.listen(5)
        print(f"Relai HTTP sniffeur en écoute sur le port {port_relais} → {server_name}:{server_port}")

        while True:
            clientSocket, addr = relaySocket.accept()
            print(f"Connexion client : {addr}")
            thread = threading.Thread(target=handle_client, args=(clientSocket, server_name, server_port, addr))
            thread.start()

    except Exception as e:
        print(f"Erreur réseau : {e}")

    finally:
        relaySocket.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage : python3 relai_sniffeur.py <port_relais> <serveur_http> <port_http>")
        sys.exit(1)

    port_relais = int(sys.argv[1])
    server_name = sys.argv[2]
    server_port = int(sys.argv[3])
    relai(port_relais, server_name, server_port)