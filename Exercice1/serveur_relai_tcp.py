# serveur_normal.py
import socket
from threading import Thread
HOST = '127.0.0.1'   # Adresse locale
PORT = 2025          # Même port que dans le relai

def handle_client(conn, addr):
    print(f"Client connecté : {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{addr}] Message reçu :", data.decode('utf-8'))
            response = f"Serveur a reçu: {data.decode('utf-8')}".encode('utf-8')
            conn.sendall(response)
    print(f"Connexion fermée avec {addr}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Serveur en écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        Thread(target=handle_client, args=(conn, addr)).start()
