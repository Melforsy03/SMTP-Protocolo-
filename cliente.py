import socket
from cryptography.fernet import Fernet
import base64

SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 2525
MAIL_FROM = "sender@example.com"
RCPT_TO = "recipient@example.com"
USERNAME = "user"
PASSWORD = "password"
MESSAGE = """\
From: sender@example.com
To: recipient@example.com
Subject: Test Email with STARTTLS

Hello, this email was sent securely with STARTTLS.
"""

# Leer la clave de cifrado desde el archivo
with open("secret.key", "rb") as key_file:
    key = key_file.read()
cipher_suite = Fernet(key)

def send_command(sock, command):
    """Envía un comando al servidor y espera una respuesta."""
    sock.sendall(command.encode())
    response = sock.recv(1024).decode()
    print(response)  # Mostrar la respuesta del servidor
    return response

def main():
    # Crear socket y conectarse al servidor SMTP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SMTP_SERVER, SMTP_PORT))

    # Recibir saludo de bienvenida
    response = client_socket.recv(1024).decode()
    print(f"Server: {response}")

    # Enviar HELO para iniciar la comunicación SMTP
    send_command(client_socket, "HELO localhost\r\n")

    # Autenticación LOGIN
    send_command(client_socket, "AUTH LOGIN\r\n")
    send_command(client_socket, base64.b64encode(USERNAME.encode()).decode() + "\r\n")
    send_command(client_socket, base64.b64encode(PASSWORD.encode()).decode() + "\r\n")

    # Especificar el remitente
    send_command(client_socket, f"MAIL FROM:<{MAIL_FROM}>\r\n")

    # Especificar el destinatario
    send_command(client_socket, f"RCPT TO:<{RCPT_TO}>\r\n")

    # Iniciar envío de datos
    send_command(client_socket, "DATA\r\n")

    # Cifrar el mensaje antes de enviarlo
    encrypted_message = cipher_suite.encrypt(MESSAGE.encode())

    # Enviar el mensaje cifrado
    send_command(client_socket, f"{encrypted_message.decode()}\r\n.\r\n")

    # Finalizar la conexión SMTP
    send_command(client_socket, "QUIT\r\n")

    # Cerrar socket
    client_socket.close()

if __name__ == "__main__":
    main()




