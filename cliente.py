import asyncio
import base64
from cryptography.fernet import Fernet
import ssl
import re

# Datos de configuración SMTP
SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 2525
USERNAME = "user"
PASSWORD = "password"

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Leer la clave de cifrado desde el archivo
def load_key():
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
    return key

cipher_suite = Fernet(load_key())

# Validar direcciones de correo electrónico
def validate_email(email):
    if not re.match(EMAIL_REGEX, email):
        raise ValueError(f"Dirección de correo no válida: {email}")

# Función para enviar el correo por SMTP
async def send_email(sender, recipient, subject, message):
    try:
        # Validar correos electrónicos
        validate_email(sender)
        validate_email(recipient)
        
        # Cifrar el mensaje
        nonce = Fernet.generate_key()[:8].decode()  # Nonce de 8 bytes
        full_message = f"Nonce: {nonce}\nFrom: {sender}\r\nTo: {recipient}\r\nSubject: {subject}\r\n\r\n{message}"
        encrypted_message = cipher_suite.encrypt(full_message.encode())

        # Crear contexto SSL
        ssl_context = ssl.create_default_context()

        # Establecer conexión con el servidor SMTP usando SSL
        reader, writer = await asyncio.open_connection(SMTP_SERVER, SMTP_PORT, ssl=ssl_context)
    
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
    
    except ValueError as ve:
        print(f"Error de validación: {ve}")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
