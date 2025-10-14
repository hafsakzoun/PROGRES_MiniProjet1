from socket import *
import sys

def client(relay_addr, relay_port):
    '''Client TCP qui se connecte au relai avec l'addresse ip et port entré en ligne de commande en paramètre'''
    try:
        # Créer le socket TCP
        clientSocket = socket(AF_INET, SOCK_STREAM)
        
        # Se connecter au relai
        clientSocket.connect((relay_addr, relay_port))
        print(f"Connecté au relai sur {relay_addr}:{relay_port}")
        
        # Envoyer plusieurs messages
        while True:
            message = input('Message à envoyer (ou "quit" pour arrêter): ')
            
            if message.lower() == 'quit':
                break
            
            # Envoyer le message
            clientSocket.sendall(message.encode('utf-8'))
            
            # Recevoir la réponse
            response = clientSocket.recv(2048)

            if not response:  # Vérifier si la réponse n'est pas vide
                print("Serveur déconnecté")
                break

            print(f"Réponse reçue: {response.decode('utf-8')}")

    except OSError as e:
        print(f"Erreur réseau: {e}")

    except gaierror:
        print("Erreur liée à l'adresse")

    except timeout:
        print("Délai d'attente expiré")

    finally:
        # Fermer la connexion
        clientSocket.close()
        print("Connexion fermée")

if __name__ == "__main__":
    #Gestion du pb d'arguments
    if len(sys.argv) != 3:
        print("Il faut entrer l'adresse IP puis le port du relai")
        sys.exit(1)
    
    relai_adr = sys.argv[1]
    relai_port = int(sys.argv[2])
    client(relai_adr, relai_port)