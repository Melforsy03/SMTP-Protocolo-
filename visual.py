from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
import asyncio
import re
from cliente import send_email
from Servidor import load_emails

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Layout de la ventana principal
class MainWindow(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20
        self.app = app

        # Título
        self.add_widget(MDLabel(text="Bienvenido a SMTP",
                                halign="center",
                                font_style="H3",
                                size_hint=(1, 0.2)))

        # Botones para Cliente y Servidor
        self.add_widget(MDRaisedButton(text="Envío de correos",
                                        size_hint=(None, None),
                                        size=("200dp", "50dp"),
                                        pos_hint={"center_x": 0.5},
                                        on_press=self.app.show_client_interface))

        self.add_widget(MDRaisedButton(text="Correos recibidos",
                                        size_hint=(None, None),
                                        size=("200dp", "50dp"),
                                        pos_hint={"center_x": 0.5},
                                        on_press=self.app.show_server_interface))

# Ventana del Cliente para enviar mensaje
import asyncio

class ClientWindow(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 30
        self.app = app
        self.spinner = None  # Agregar una referencia al spinner

        # Título
        self.add_widget(MDLabel(text="Enviar Correo",
                                halign="center",
                                font_style="H4",
                                size_hint=(1, 0.1)))

        # Remitente
        self.sender_input = MDTextField(hint_text="Introduce el remitente", size_hint=(1, None), height="40dp")
        self.add_widget(self._build_labeled_field("Remitente:", self.sender_input))

        # Destinatario
        self.recipient_input = MDTextField(hint_text="Introduce el destinatario", size_hint=(1, None), height="40dp")
        self.add_widget(self._build_labeled_field("Destinatario:", self.recipient_input))

        # Asunto
        self.subject_input = MDTextField(hint_text="Introduce el asunto", size_hint=(1, None), height="40dp")
        self.add_widget(self._build_labeled_field("Asunto:", self.subject_input))

        # Mensaje
        self.message_input = MDTextField(hint_text="Introduce tu mensaje", multiline=True, size_hint=(1, None), height="200dp")
        self.add_widget(self._build_labeled_field("Mensaje:", self.message_input))

        # Botón Enviar
        self.send_button = MDRaisedButton(text="Enviar",
                                          size_hint=(None, None),
                                          size=("200dp", "50dp"),
                                          pos_hint={"center_x": 0.5},
                                          on_press=self.send_message)
        self.add_widget(self.send_button)

        # Botón Volver
        self.add_widget(MDRaisedButton(text="Volver",
                                       size_hint=(None, None),
                                       size=("200dp", "50dp"),
                                       pos_hint={"center_x": 0.5},
                                       on_press=self.app.show_main_interface))

    def _build_labeled_field(self, label_text, input_field):
        layout = BoxLayout(orientation="vertical", size_hint=(1, None), height="100dp")
        layout.add_widget(MDLabel(text=label_text, halign="left"))
        layout.add_widget(input_field)
        return layout

    async def send_message_async(self, sender, recipient, subject, message):
        try:
            await send_email(sender, recipient, subject, message)
            toast("Correo enviado correctamente.")  # Usamos el toast aquí
            self.app.show_main_interface()
        except Exception as e:
            toast(f"Error: {str(e)}")  # Usamos el toast aquí
        finally:
            # Eliminar el spinner después de que termine el proceso
            if self.spinner:
                self.remove_widget(self.spinner)
                self.spinner = None

    def send_message(self, instance):
        sender = self.sender_input.text
        recipient = self.recipient_input.text
        subject = self.subject_input.text
        message = self.message_input.text

        # Validaciones
        if not all([sender, recipient, subject, message]):
            toast("Todos los campos deben estar completos.")  # Usamos el toast aquí
            return

        if not re.match(EMAIL_REGEX, sender):
            toast("El remitente no tiene un formato válido.")  # Usamos el toast aquí
            return

        if not re.match(EMAIL_REGEX, recipient):
            toast("El destinatario no tiene un formato válido.")  # Usamos el toast aquí
            return

        # Spinner de carga (solo uno)
        if not self.spinner:
            self.spinner = MDSpinner(size_hint=(None, None), size=("48dp", "48dp"), pos_hint={"center_x": 0.5, "center_y": 0.5})
            self.add_widget(self.spinner)

        # Ejecutar la tarea asincrónica correctamente
        asyncio.run(self.send_message_async(sender, recipient, subject, message))

# Ventana del Servidor para ver los mensajes
class ServerWindow(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = (30, 20, 30, 0)
        self.app = app

        # Título
        self.add_widget(MDLabel(text="Bandeja de Correos",
                                halign="center",
                                font_style="H4",
                                size_hint=(1, 0.1)))

        # Tabla de correos
        self.add_widget(self._build_emails_table())

        # Botón Volver
        self.add_widget(MDRaisedButton(text="Volver",
                                       size_hint=(None, None),
                                       size=("200dp", "50dp"),
                                       pos_hint={"center_x": 0.5},
                                       on_press=self.app.show_main_interface))

    def _build_emails_table(self):
        emails = load_emails()
        rows = [(email['from'], email['subject'], email['date']) for email in emails]

        # Aumentamos el tamaño de la tabla
        data_table = MDDataTable(
            size_hint=(1, 1),
            column_data=[("Remitente", dp(40)), ("Asunto", dp(50)), ("Fecha", dp(30))],
            row_data=rows,
            elevation=2  # Sombra para la tabla
        )

        # Evento de clic en una fila para mostrar el cuerpo del correo
        def show_body(instance, row):
            dialog = MDDialog(
                title="Cuerpo del Mensaje",
                text=row[3],
                size_hint=(0.8, 0.6),
                buttons=[
                    MDRaisedButton(
                        text="Cerrar", 
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()

        # Asignar la función a cada fila
        def row_on_release(instance, row):
            show_body(instance, row)

        data_table.bind(on_row_release=row_on_release)

        return data_table

# Clase principal de la aplicación
class SMTPApp(MDApp):
    def build(self):
        # Configurar el tema con fondo oscuro y color morado
        self.theme_cls.primary_palette = "Purple"  
        self.theme_cls.primary_hue = "500" 
        self.theme_cls.theme_style = "Dark" 
        self.theme_cls.accent_palette = "Purple"  
        self.theme_cls.accent_hue = "500" 

        self.main_window = MainWindow(self)
        return self.main_window

    def show_main_interface(self, *args):
        self.root.clear_widgets()
        self.root.add_widget(MainWindow(self))

    def show_client_interface(self, *args):
        self.root.clear_widgets()
        self.root.add_widget(ClientWindow(self))

    def show_server_interface(self, *args):
        self.root.clear_widgets()
        self.root.add_widget(ServerWindow(self))

if __name__ == "__main__":
    SMTPApp().run()
