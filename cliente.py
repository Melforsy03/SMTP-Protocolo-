import socket

def smtp_client(server_address, server_port, sender, recipient, subject, message):
    try:
        # Conexión al servidor
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        
        # Leer saludo inicial
        response = client_socket.recv(1024).decode()
        print(f"Server: {response}")

        # HELO comando
        client_socket.sendall(b"HELO client.example.com\r\n")
        response = client_socket.recv(1024).decode()
        print(f"Server: {response}")

        # MAIL FROM comando
        client_socket.sendall(f"MAIL FROM:<{sender}>\r\n".encode())
        response = client_socket.recv(1024).decode()
        print(f"Server: {response}")

        # RCPT TO comando
        client_socket.sendall(f"RCPT TO:<{recipient}>\r\n".encode())
        response = client_socket.recv(1024).decode()
        print(f"Server: {response}")

        # DATA comando
        client_socket.sendall(b"DATA\r\n")
        response = client_socket.recv(1024).decode()
        print(f"Server: {response}")

        # Cuerpo del correo
        email_body = f"Subject: {subject}\r\n\r\n{message}\r\n.\r\n"
        client_socket.sendall(email_body.encode())
        response = client_socket.recv(1024).decode()
        print(f"Server: {response}")

        # QUIT comando
        client_socket.sendall(b"QUIT\r\n")
        response = client_socket.recv(1024).decode()
        print(f"Server: {response}")

        # Cerrar conexión
        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")

# Uso del cliente
# smtp_client("127.0.0.1", 25, "sender@example.com", "recipient@example.com", "Test Subject", "Hello, this is a test email!")
