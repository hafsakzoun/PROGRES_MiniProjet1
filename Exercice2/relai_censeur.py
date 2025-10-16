from socket import *
import threading
import sys
from datetime import datetime

LOG_FILE = "event.log"

def load_blacklist(filename='interdit.txt'):
    '''Fonction pour charger le fichier blacklist'''
    with open(filename, 'r') as f: 
        return [line.strip() for line in f if line.strip()]

def log_event(event: str):
    """Écrit un événement dans le fichier de log avec date/heure"""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event}\n")

def handle_client(socketClient, client_addr, serverName, serverPort):
    '''Gère un client avec la censure de blacklist'''
    client_ip = client_addr[0]
    blacklist=load_blacklist()
    try:
        # Créer un socket pour se connecter au serveur
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.connect((serverName, serverPort))
        print(f"Connecté au serveur sur {serverName}:{serverPort}")

        while True:
            #Reception du msg du client
            message = socketClient.recv(2048)
            if not message:
                print("Client déconnecté")
                break
            
            #Si on a la méthode GET alors on verifie
            msg=message.decode('utf-8')
            if msg.startswith("GET"):
                uri=msg.split(' ')[1]
                #On verifie si l'uri est dans la blacklist
                if any(blocked in uri for blocked in blacklist): #si uri bloque

                    reponse = "INTERDIT\r\n\r\n"
                    
                    #on loggue l'evenement
                    log_event(f"CLIENT {client_ip} a demandé URI: {uri}")
                    
                    #on envoie la reponse au client
                    socketClient.sendall(reponse.encode('utf-8'))
                    print(f"URI censurée: {uri}")
                    continue  # Ne pas contacter le serveur

            print(f"Message reçu du client: {message.decode('utf-8')}")

            # Envoyer le message au serveur
            serverSocket.sendall(message)

            #Reception de la reponse du serveur
            response = serverSocket.recv(2048)
            if not response:
                print("Serveur déconnecté")
                break

            print(f"Réponse reçue du serveur : {response.decode('utf-8')}")

            # Envoyer la réponse au client
            socketClient.sendall(response)

    except OSError as e:
        print(f"Erreur réseau: {e}")

    except gaierror:
        print("Erreur liée à l'adresse")

    except timeout:
        print("Délai d'attente expiré")

    finally:
        socketClient.close()
        serverSocket.close()
        print("Connexion fermée")

def relai(relay_port, server_name, server_port):
    '''Relai TCP'''
    try:
        relaySocket = socket(AF_INET, SOCK_STREAM)
        relaySocket.bind(('', relay_port))
        relaySocket.listen(5)
        print(f'Relai prêt sur le port {relay_port}, pour le serveur {server_name}:{server_port}')

        while True:
            # Accepter la connexion du client
            clientSocket, addr = relaySocket.accept()
            print(f"Connexion établie avec le client : {addr}")

            # Pour chaque client, on crée un thread différent
            client_thread = threading.Thread(target=handle_client, args=(clientSocket, addr, server_name, server_port))
            client_thread.start()

    except OSError as e:
        print(f"Erreur réseau: {e}")

    except gaierror:
        print("Erreur liée à l'adresse")

    except timeout:
        print("Délai d'attente expiré")

    finally:
        relaySocket.close()
        print("Relai fermé")

if __name__ == "__main__":
    #Gestion du pb d'arguments
    if len(sys.argv) != 4:
        print("Il faut entrer le numero du port du relai, l'adresse IP puis le port du serveur")
        sys.exit(1)
    
    relay_port = int(sys.argv[1])
    server_addr = sys.argv[2]
    server_port = int(sys.argv[3])
    relai(relay_port, server_addr, server_port)