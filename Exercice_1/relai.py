from socket import *
import threading
import sys

def handle_client(socketClient, serverName, serverPort):
    '''Relais les requêtes du client au serveur et transmet la réponse du serveur au client'''
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

            print(f"Message reçu du client: {message.decode('utf-8')}")

            # Envoyer le message au serveur final
            serverSocket.sendall(message)

            #Reception de la reponse du serveur
            response = serverSocket.recv(2048)
            if not response:
                print("Serveur final déconnecté")
                break

            print(f"Réponse reçue du serveur final: {response.decode('utf-8')}")

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
            client_thread = threading.Thread(target=handle_client, args=(clientSocket, server_name, server_port))
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
    server_name = sys.argv[2]
    server_port = int(sys.argv[3])
    relai(relay_port, server_name, server_port)