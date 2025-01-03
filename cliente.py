import tkinter as tk
from tkinter import messagebox
import socket
import base64
from cryptography.fernet import Fernet

# Datos de configuración SMTP
SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 2525
USERNAME = "user"
PASSWORD = "password"

# Generar una clave de cifrado si no existe
def generate_key():
    try:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    return key

# Leer la clave de cifrado
key = generate_key()
cipher_suite = Fernet(key)

# Función para enviar el correo por SMTP
def send_email():
    try:
        # Recoger los datos de los campos de entrada
        mail_from = sender_entry.get()
        rcpt_to = recipient_entry.get()
        subject = subject_entry.get()
        message = message_entry.get("1.0", "end-1c")

        if not message:
            messagebox.showerror("Error", "El mensaje no puede estar vacío.")
            return
        if not mail_from or not rcpt_to:
            messagebox.showerror("Error", "El remitente y el destinatario son obligatorios.")
            return

        # Formatear el mensaje con los campos 'From', 'To' y 'Subject'
        formatted_message = f"From: {mail_from}\r\nTo: {rcpt_to}\r\nSubject: {subject}\r\n\r\n{message}"

        # Cifrar el mensaje completo
        encrypted_message = cipher_suite.encrypt(formatted_message.encode())

        # Establecer la conexión con el servidor SMTP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SMTP_SERVER, SMTP_PORT))

        # Interacción con el servidor SMTP
        client_socket.recv(1024)  # Mensaje de bienvenida
        client_socket.sendall(b"HELO localhost\r\n")
        client_socket.recv(1024)

        # Autenticación
        client_socket.sendall(b"AUTH LOGIN\r\n")
        client_socket.sendall(base64.b64encode(b"user").decode().encode() + b"\r\n")
        client_socket.sendall(base64.b64encode(b"password").decode().encode() + b"\r\n")
        client_socket.recv(1024)

        # Enviar el correo
        client_socket.sendall(f"MAIL FROM:<{mail_from}>\r\n".encode())
        client_socket.recv(1024)
        client_socket.sendall(f"RCPT TO:<{rcpt_to}>\r\n".encode())
        client_socket.recv(1024)
        client_socket.sendall(b"DATA\r\n")
        client_socket.recv(1024)

        # Enviar el mensaje cifrado
        client_socket.sendall(f"{encrypted_message.decode()}\r\n.\r\n".encode())
        client_socket.recv(1024)

        # Terminar la sesión
        client_socket.sendall(b"QUIT\r\n")
        client_socket.close()

        # Mensaje de éxito
        messagebox.showinfo("Éxito", "El mensaje fue enviado correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# Pantalla de inicio
def show_main_screen():
    main_screen = tk.Tk()
    main_screen.title("Pantalla de Inicio")
    main_screen.geometry("600x400")
    main_screen.config(bg="#f3f3f3")  # Fondo suave

    # Título
    title_label = tk.Label(main_screen, text="Bienvenido al Enviador de SMS", font=("Helvetica", 24, "bold"), fg="#4CAF50", bg="#f3f3f3")
    title_label.pack(pady=50)

    # Botón para ir a la pantalla de enviar SMS
    go_button = tk.Button(main_screen, text="Enviar SMS", width=20, height=2, font=("Helvetica", 16), bg="#4CAF50", fg="white", command=lambda: show_send_sms_screen(main_screen))
    go_button.pack(pady=10)

    # Ejecutar la pantalla
    main_screen.mainloop()

# Pantalla de envío de SMS
def show_send_sms_screen(prev_screen=None):
    if prev_screen:
        prev_screen.destroy()

    send_sms_screen = tk.Tk()
    send_sms_screen.title("Enviar SMS")
    send_sms_screen.geometry("600x500")
    send_sms_screen.config(bg="#f3f3f3")  # Fondo suave

    # Título
    title_label = tk.Label(send_sms_screen, text="Enviar un Mensaje", font=("Helvetica", 24, "bold"), fg="#4CAF50", bg="#f3f3f3")
    title_label.pack(pady=30)

    # Campos para el asunto, remitente y destinatario
    subject_label = tk.Label(send_sms_screen, text="Asunto:", font=("Helvetica", 14), bg="#f3f3f3")
    subject_label.pack()

    subject_entry = tk.Entry(send_sms_screen, font=("Helvetica", 12), width=40)
    subject_entry.pack(pady=10)

    sender_label = tk.Label(send_sms_screen, text="Remitente:", font=("Helvetica", 14), bg="#f3f3f3")
    sender_label.pack()

    sender_entry = tk.Entry(send_sms_screen, font=("Helvetica", 12), width=40)
    sender_entry.pack(pady=10)

    recipient_label = tk.Label(send_sms_screen, text="Destinatario:", font=("Helvetica", 14), bg="#f3f3f3")
    recipient_label.pack()

    recipient_entry = tk.Entry(send_sms_screen, font=("Helvetica", 12), width=40)
    recipient_entry.pack(pady=10)

    # Entrada para el mensaje
    message_label = tk.Label(send_sms_screen, text="Mensaje:", font=("Helvetica", 14), bg="#f3f3f3")
    message_label.pack()

    message_entry = tk.Text(send_sms_screen, width=50, height=10, font=("Helvetica", 12), wrap="word", bd=2)
    message_entry.pack(pady=10)

    # Botón para enviar el SMS
    send_button = tk.Button(send_sms_screen, text="Enviar SMS", width=20, height=2, font=("Helvetica", 16), bg="#4CAF50", fg="white", command=lambda: send_email())
    send_button.pack(pady=20)

    # Botón para volver
    back_button = tk.Button(send_sms_screen, text="Volver", width=20, height=2, font=("Helvetica", 14), bg="#f44336", fg="white", command=lambda: show_main_screen())
    back_button.pack(pady=10)

    # Ejecutar la pantalla de envío de SMS
    send_sms_screen.mainloop()

if __name__ == "__main__":
    show_main_screen()
