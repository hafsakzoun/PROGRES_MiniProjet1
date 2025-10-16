from socket import *
import sys
import threading

def handle_client(connectionSocket, addr):
    '''Gère la communication avec un client'''
    try:
        print(f"Connexion établie avec le client : {addr}")
        
        while True:  # Si on a plusieurs messages
            message = connectionSocket.recv(2048)
            if not message:
                print(f"Client déconnecté : {addr}")
                break

            print(f"Message reçu : {message.decode()}")
            # On renvoie le message en majuscule
            response = message.decode('utf-8').upper()
            connectionSocket.sendall(response.encode('utf-8'))

    except OSError as e:
        print(f"Erreur réseau: {e}")

    finally:
        connectionSocket.close()
        print(f"Connexion fermée avec le client : {addr}")


def serveur(port):
    '''Serveur TCP prenant le port entré en ligne de commande en paramètre'''
    try:
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', port))
        serverSocket.listen(5)
        print(f'Server ready on port {port}')

        while True:
            # Accepter la connexion
            connectionSocket, addr = serverSocket.accept()
            
            #Pour pouvoir avoir plusieurs clients en même temps
            client = threading.Thread(target=handle_client, args=(connectionSocket, addr))
            client.start()
    
    except OSError as e:
        print(f"Erreur réseau: {e}")
    
    except gaierror:
        print("Erreur liée à l'adresse")
    
    except timeout:
        print("Délai d'attente expiré")

    finally: #Fermer la connexion
        serverSocket.close()

if __name__ == "__main__":
    #Gestion du pb d'arguments
    if len(sys.argv) != 2:
        print("Il faut entrer le numero du port")
        sys.exit(1)
    
    port = int(sys.argv[1])
    serveur(port)