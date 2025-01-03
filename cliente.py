import asyncio
import base64
import socket
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox

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

        messagebox.showinfo("Éxito", "Correo enviado correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar el correo: {str(e)}")

# Pantalla de inicio
def show_main_screen():
    main_screen = tk.Tk()
    main_screen.title("Pantalla de Inicio")
    main_screen.geometry("600x400")
    main_screen.config(bg="#f3f3f3")

    title_label = tk.Label(main_screen, text="Bienvenido al Enviador de SMS", font=("Helvetica", 24, "bold"), fg="#4CAF50", bg="#f3f3f3")
    title_label.pack(pady=50)

    go_button = tk.Button(main_screen, text="Enviar SMS", width=20, height=2, font=("Helvetica", 16), bg="#4CAF50", fg="white", command=lambda: show_send_sms_screen(main_screen))
    go_button.pack(pady=10)

    main_screen.mainloop()

# Pantalla para enviar SMS
def show_send_sms_screen(prev_screen=None):
    if prev_screen:
        prev_screen.destroy()

    send_sms_screen = tk.Tk()
    send_sms_screen.title("Enviar SMS")
    send_sms_screen.geometry("600x500")
    send_sms_screen.config(bg="#f3f3f3")

    title_label = tk.Label(send_sms_screen, text="Enviar un Mensaje", font=("Helvetica", 24, "bold"), fg="#4CAF50", bg="#f3f3f3")
    title_label.pack(pady=30)

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

    message_label = tk.Label(send_sms_screen, text="Mensaje:", font=("Helvetica", 14), bg="#f3f3f3")
    message_label.pack()
    message_entry = tk.Text(send_sms_screen, width=50, height=10, font=("Helvetica", 12), wrap="word", bd=2)
    message_entry.pack(pady=10)

    send_button = tk.Button(send_sms_screen, text="Enviar SMS", width=20, height=2, font=("Helvetica", 16), bg="#4CAF50", fg="white", command=lambda: asyncio.run(send_email(sender_entry.get(), recipient_entry.get(), subject_entry.get(), message_entry.get("1.0", "end-1c"))))
    send_button.pack(pady=20)

    back_button = tk.Button(send_sms_screen, text="Volver", width=20, height=2, font=("Helvetica", 14), bg="#f44336", fg="white", command=lambda: show_main_screen())
    back_button.pack(pady=10)

    send_sms_screen.mainloop()

if __name__ == "__main__":
    show_main_screen()
