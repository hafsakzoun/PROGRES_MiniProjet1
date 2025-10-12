#relai se comporte comme le serveur TCP

from socket import *
from select import select
import sys
from threading import Thread

#  Vérification des argument
if len(sys.argv) != 3:
    print("Usage: python3 relai_tcp.py <server_ip> <server_port>")
    sys.exit(1)

# Lecture des arguments
server_ip = sys.argv[1]
server_port = int(sys.argv[2])

# 1: Création du serveur d’écoute du relai
relaySocket = socket(AF_INET, SOCK_STREAM)
relaySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Permet de relancer sans erreur
relaySocket.bind(('', 5012))   # Le relai écoute sur le port 5000
relaySocket.listen(7)          # Autoriser plusieurs connexions simultanées (7 dans notre cas)
print("Relai prêt, en attente d’un client sur le port 5012...")

def gestion_clients(clientSocket, server_ip, server_port):
    try:
        # 2️: Connexion du relai au vrai serveur
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((server_ip, server_port))
        print("Connecté au serveur réel :", server_ip, server_port)

        # 3️: Relayage bidirectionnel des données
        while True:
            ready, _, _ = select([clientSocket, serverSocket], [], [])

            for sock in ready:
                data = sock.recv(4096)
                if not data:
                    # Si une des connexions se ferme, on quitte
                    print("Connexion terminée avec :", 
                          "client" if sock is clientSocket else "serveur")
                    return
                # Si le message vient du client alors le relai est vers le serveur
                if sock is clientSocket:
                    serverSocket.sendall(data)
                # Si le message vient du serveur donc le relai est vers le client
                else:
                    clientSocket.sendall(data)

    except Exception as e:
        print("Erreur relayage:", e)

    finally:
        clientSocket.close()
        serverSocket.close()
        print("Client et serveur déconnectés proprement.")

# Boucle principale pour accepter plusieurs clients
while True:
    clientSocket, clientAddress = relaySocket.accept()
    print("Client connecté :", clientAddress)
    thread = Thread(target=gestion_clients, args=(clientSocket, server_ip, server_port))
    thread.start()
