# serveur_normal.py
import socket
from threading import Thread

HOST = '127.0.0.1'
PORT = 8080

def handle_client(conn, addr):
    print(f"Client connecté : {addr}")
    with conn:
        data = conn.recv(1024).decode('utf-8')
        if data.startswith("GET"):
            uri = data.split()[1]
            if uri == "/":
                uri = "/index.html"
            try:
                with open(uri[1:], "rb") as f:
                    content = f.read()
                response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + content
            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found\r\n\r\nFichier non trouvé".encode('utf-8')
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
