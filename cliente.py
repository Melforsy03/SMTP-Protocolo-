import asyncio
import base64
from cryptography.fernet import Fernet
import ssl
from email.utils import formatdate


SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 2525
USERNAME = "user"
PASSWORD = "password"

def load_key():
    # Cargar la clave de cifrado
    with open("secret.key", "rb") as key_file:
        return key_file.read()

cipher_suite = Fernet(load_key())

def validate_email(email):
    # Descomenta la siguiente línea solo si deseas realizar validaciones estrictas
    #try:
    #    validate_email_lib(email)
    #except EmailNotValidError as e:
    #    raise ValueError(f"Dirección de correo no válida: {e}")
    pass  # Desactiva temporalmente la validación para pruebas

async def read_response(reader):
    # Leer la respuesta del servidor SMTP
    response = await reader.read(1024)
    response_decoded = response.decode()
    
    # Verifica que la respuesta empiece con un código válido
    if not (response_decoded.startswith("2") or response_decoded.startswith("3")):
        raise Exception(f"Error del servidor: {response_decoded}")
    
    return response_decoded

async def send_email(sender, recipient, subject, message):
    # Validar las direcciones de correo (temporalmente desactivada)
    validate_email(sender)
    validate_email(recipient)

    # Construir el mensaje
    headers = f"From: {sender}\nTo: {recipient}\nSubject: {subject}\nDate: {formatdate(localtime=True)}\n"
    full_message = headers + "\n" + message
    
    # Cifrar el mensaje
    encrypted_message = cipher_suite.encrypt(full_message.encode())

    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations("server.crt")
    
    reader, writer = None, None  # Inicializar writer y reader fuera del try

    try:
        # Abrir una conexión segura al servidor SMTP
        reader, writer = await asyncio.open_connection(SMTP_SERVER, SMTP_PORT, ssl=ssl_context)

        # Leer la respuesta del servidor (bienvenida)
        await read_response(reader)

        # Enviar comando HELO
        writer.write(b"HELO localhost\r\n")
        await writer.drain()
        await read_response(reader)

        # Autenticación LOGIN
        writer.write(b"AUTH LOGIN\r\n")
        await writer.drain()
        await read_response(reader)

        # Enviar el nombre de usuario codificado en base64
        writer.write(base64.b64encode(USERNAME.encode()) + b"\r\n")
        await writer.drain()
        await read_response(reader)

        # Enviar la contraseña codificada en base64
        writer.write(base64.b64encode(PASSWORD.encode()) + b"\r\n")
        await writer.drain()
        await read_response(reader)

        # Enviar MAIL FROM
        writer.write(f"MAIL FROM:<{sender}>\r\n".encode())
        await writer.drain()
        await read_response(reader)

        # Enviar RCPT TO
        writer.write(f"RCPT TO:<{recipient}>\r\n".encode())
        await writer.drain()
        await read_response(reader)

        # Enviar DATA
        writer.write(b"DATA\r\n")
        await writer.drain()
        await read_response(reader)

        # Enviar el mensaje cifrado
        writer.write(encrypted_message + b"\r\n.\r\n")
        await writer.drain()
        await read_response(reader)

        # Finalizar la conexión
        writer.write(b"QUIT\r\n")
        await writer.drain()
        await read_response(reader)

        print("Correo enviado correctamente.")

    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    
    finally:
        if writer:  # Solo cerrar writer si la conexión se estableció
            writer.close()
            await writer.wait_closed()

# Prueba el envío de correo
if __name__ == "__main__":
    # Cambia estos valores a correos reales para probar
    sender = "remitente@miempresa.com"
    recipient = "destinatario@miempresa.com"
    subject = "Asunto de prueba"
    message = "Este es un mensaje de prueba."

    # Ejecutar el cliente
    asyncio.run(send_email(sender, recipient, subject, message))