from socket import *
import threading
import sys

def handle_client(connectionSocket, addr):
    '''Gère la communication avec un client spécifique'''
    print(f"Connexion établie avec le client : {addr}")

    try:
        while True:
            # Réception du message du client
            message = connectionSocket.recv(2048)
            if not message:
                print(f"Client déconnecté : {addr}")
                break

            print(f"Message reçu de {addr} : {message.decode('utf-8')}")
            
            # Réponse en majuscules
            response = message.decode('utf-8').upper()
            connectionSocket.sendall(response.encode('utf-8'))

    except OSError as e:
        print(f"Erreur réseau avec {addr}: {e}")

    finally:
        connectionSocket.close()
        print(f"Connexion fermée avec {addr}")


def serveur(port):
    '''Serveur TCP multithreadé'''
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', port))
        serverSocket.listen(5)
        print(f"Serveur prêt sur le port {port}")

        while True:
            # Attendre une nouvelle connexion client
            connectionSocket, addr = serverSocket.accept()
            
            # Créer un thread pour chaque client
            client_thread = threading.Thread(target=handle_client, args=(connectionSocket, addr))
            client_thread.start()

    except OSError as e:
        print(f"Erreur réseau: {e}")

    except gaierror:
        print("Erreur liée à l'adresse")

    except timeout:
        print("Délai d'attente expiré")

    finally:
        serverSocket.close()
        print("Serveur fermé")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Il faut entrer le numéro du port")
        sys.exit(1)
    
    port = int(sys.argv[1])
    serveur(port)
