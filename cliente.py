import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import base64
import socket

# Configuraciones SMTP
SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 2525
USERNAME = "user"
PASSWORD = "password"

# Leer la clave de cifrado desde el archivo
with open("secret.key", "rb") as key_file:
    key = key_file.read()
cipher_suite = Fernet(key)

# Función para enviar el correo
def send_email():
    # Capturar los datos de la interfaz gráfica
    mail_from = entry_from.get()
    rcpt_to = entry_to.get()
    subject = entry_subject.get()
    message = text_body.get("1.0", tk.END).strip()

    if not mail_from or not rcpt_to or not message:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    # Crear el cuerpo del mensaje SMTP
    msg = f"""\
From: {mail_from}
To: {rcpt_to}
Subject: {subject}

{message}
"""

    # Cifrar el mensaje
    encrypted_message = cipher_suite.encrypt(msg.encode())

    try:
        # Crear socket y conectarse al servidor SMTP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SMTP_SERVER, SMTP_PORT))

        # Función para enviar comandos SMTP
        def send_command(command):
            client_socket.sendall(command.encode())
            response = client_socket.recv(1024).decode()
            print(response)  # Mostrar respuesta del servidor

        # Enviar comandos SMTP
        send_command("HELO localhost\r\n")
        send_command("AUTH LOGIN\r\n")
        send_command(base64.b64encode(USERNAME.encode()).decode() + "\r\n")
        send_command(base64.b64encode(PASSWORD.encode()).decode() + "\r\n")
        send_command(f"MAIL FROM:<{mail_from}>\r\n")
        send_command(f"RCPT TO:<{rcpt_to}>\r\n")
        send_command("DATA\r\n")
        send_command(f"{encrypted_message.decode()}\r\n.\r\n")
        send_command("QUIT\r\n")

        # Cerrar socket
        client_socket.close()

        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", "Correo enviado correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar el correo: {str(e)}")

# Crear la ventana de la interfaz
root = tk.Tk()
root.title("Cliente SMTP")

# Crear y colocar los widgets en la ventana
label_from = tk.Label(root, text="Remitente:")
label_from.grid(row=0, column=0, padx=10, pady=5)
entry_from = tk.Entry(root, width=50)
entry_from.grid(row=0, column=1, padx=10, pady=5)

label_to = tk.Label(root, text="Destinatario:")
label_to.grid(row=1, column=0, padx=10, pady=5)
entry_to = tk.Entry(root, width=50)
entry_to.grid(row=1, column=1, padx=10, pady=5)

label_subject = tk.Label(root, text="Asunto:")
label_subject.grid(row=2, column=0, padx=10, pady=5)
entry_subject = tk.Entry(root, width=50)
entry_subject.grid(row=2, column=1, padx=10, pady=5)

label_body = tk.Label(root, text="Cuerpo del mensaje:")
label_body.grid(row=3, column=0, padx=10, pady=5)
text_body = tk.Text(root, height=10, width=50)
text_body.grid(row=3, column=1, padx=10, pady=5)

# Botón para enviar el correo
send_button = tk.Button(root, text="Enviar Correo", command=send_email)
send_button.grid(row=4, column=1, padx=10, pady=10)

# Ejecutar la interfaz gráfica
root.mainloop()