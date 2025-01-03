import asyncio
import base64
from cryptography.fernet import Fernet

# Datos de configuración SMTP
SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 2525
USERNAME = "user"
PASSWORD = "password"

# Leer la clave de cifrado desde el archivo
def load_key():
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
    return key

cipher_suite = Fernet(load_key())

# Función para enviar el correo por SMTP
async def send_email(sender, recipient, subject, message):
    try:
        # Cifrar el mensaje
        encrypted_message = cipher_suite.encrypt(f"From: {sender}\r\nTo: {recipient}\r\nSubject: {subject}\r\n\r\n{message}".encode())

        reader, writer = await asyncio.open_connection(SMTP_SERVER, SMTP_PORT)
        data = await reader.read(100)
        print(f"Servidor: {data.decode()}")
        
        # Enviar HELO
        writer.write(b"HELO localhost\r\n")
        await writer.drain()

        # Autenticación
        writer.write(b"AUTH LOGIN\r\n")
        await writer.drain()
        writer.write(base64.b64encode(USERNAME.encode()) + b"\r\n")
        await writer.drain()
        writer.write(base64.b64encode(PASSWORD.encode()) + b"\r\n")
        await writer.drain()

        # Enviar MAIL FROM y RCPT TO
        writer.write(f"MAIL FROM:<{sender}>\r\n".encode())
        await writer.drain()
        writer.write(f"RCPT TO:<{recipient}>\r\n".encode())
        await writer.drain()
        
        # Iniciar la transferencia de datos
        writer.write(b"DATA\r\n")
        await writer.drain()

        # Enviar el mensaje cifrado
        writer.write(encrypted_message + b"\r\n.\r\n")
        await writer.drain()

        # Cerrar la conexión
        writer.write(b"QUIT\r\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

        print("Correo enviado correctamente.")

    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
