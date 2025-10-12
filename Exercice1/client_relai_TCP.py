# client_normal.py
import socket

SERVER_IP = '127.0.0.1'  # Adresse du relai, pas du serveur direct
SERVER_PORT = 5012       # Port du relai

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print(f"Connecté à {SERVER_IP}:{SERVER_PORT}")

    while True:
        message = input("Votre message (ou 'quit' pour sortir) : ")
        if message.lower() == 'quit':
            break

        client_socket.sendall(message.encode('utf-8'))

        data = client_socket.recv(1024)
        print("Réponse :", data.decode('utf-8'))
