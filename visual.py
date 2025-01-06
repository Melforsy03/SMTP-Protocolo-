from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.floatlayout import FloatLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import ScrollView


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
                                theme_text_color="Custom",
                                text_color=(1, 1, 1, 1),
                                font_style="H3",
                                size_hint=(1, 0.2)))

        # Botones para Cliente y Servidor
        self.client_button = MDRaisedButton(text="Envio de correos",
                                            size_hint=(None, None),
                                            size=("200dp", "50dp"),
                                            pos_hint={"center_x": 0.5},
                                            on_press=self.app.show_client_interface)
        self.add_widget(self.client_button)

        self.server_button = MDRaisedButton(text="Correos recibidos",
                                            size_hint=(None, None),
                                            size=("200dp", "50dp"),
                                            pos_hint={"center_x": 0.5},
                                            on_press=self.app.show_server_interface)
        self.add_widget(self.server_button)


# Ventana del Cliente para enviar mensaje
class ClientWindow(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 30
        self.app = app

        # Título
        self.add_widget(MDLabel(text="Enviar Correo",
                                halign="center",
                                theme_text_color="Custom",
                                text_color=(1, 1, 1, 1),
                                font_style="H4",
                                size_hint=(1, 0.1)))

        # Remitente
        self.add_widget(MDLabel(text="Remitente:", halign="left"))
        self.sender_input = MDTextField(hint_text="Introduce el remitente")
        self.add_widget(self.sender_input)

        # Destinatario
        self.add_widget(MDLabel(text="Destinatario:", halign="left"))
        self.recipient_input = MDTextField(hint_text="Introduce el destinatario")
        self.add_widget(self.recipient_input)

        # Asunto
        self.add_widget(MDLabel(text="Asunto:", halign="left"))
        self.subject_input = MDTextField(hint_text="Introduce el asunto")
        self.add_widget(self.subject_input)

        # Mensaje
        self.add_widget(MDLabel(text="Mensaje:", halign="left"))
        self.message_input = MDTextField(hint_text="Introduce tu mensaje", multiline=True, size_hint_y=None, height="100dp")
        self.add_widget(self.message_input)

        # Botones
        self.send_button = MDRaisedButton(text="Enviar",
                                          size_hint=(None, None),
                                          size=("200dp", "50dp"),
                                          pos_hint={"center_x": 0.5},
                                          on_press=self.send_message)
        self.add_widget(self.send_button)

        self.back_button = MDRaisedButton(text="Volver",
                                          size_hint=(None, None),
                                          size=("200dp", "50dp"),
                                          pos_hint={"center_x": 0.5},
                                          on_press=self.app.show_main_interface)
        self.add_widget(self.back_button)

    def send_message(self, instance):
        sender = self.sender_input.text
        recipient = self.recipient_input.text
        subject = self.subject_input.text
        message = self.message_input.text

        if sender and recipient and subject and message:
            print(f"Mensaje enviado: {sender} -> {recipient}: {subject}")
        else:
            print("Todos los campos deben estar completos.")


# Ventana del Servidor para ver los mensajes
class ServerWindow(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20  # Menor espacio entre elementos
        self.padding = (30, 20, 30, 0)  # Ajustar el margen para subir los elementos
        self.app = app

        # Título
        self.add_widget(MDLabel(text="Bandeja de Correos",
                                halign="center",
                                theme_text_color="Custom",
                                text_color=(1, 1, 1, 1),
                                font_style="H4",
                                size_hint=(1 , 0.5)))

        # Scroll para mensajes
        self.messages_list = ScrollView(size_hint=(1, 1), height=300)
        self.messages_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        self.messages_box.bind(minimum_height=self.messages_box.setter('height'))

        # Mensajes simulados
        for i in range(5):
            message = MDCard(size_hint=(1, None), height="100dp", padding=10)
            message.add_widget(MDLabel(
                text=f"Asunto: Test {i + 1}\nRemitente: user\nFecha: 01/01/202566",
                halign="left",
                theme_text_color="Secondary",
            ))
            self.messages_box.add_widget(message)
            
        for i in range(5):
            message = MDCard(size_hint=(None, None), size=("700dp", "100dp"), padding=10,
                             pos_hint={"center_x": 0.4})  # Tamaño reducido al 50% del ancho
            message.add_widget(MDLabel(
                text=f"Asunto: Test {i + 1}\nRemitente: user\nFecha: 01/01/2025",
                halign="left",
                theme_text_color="Secondary",
            ))
            self.messages_box.add_widget(message)

        self.messages_list.add_widget(self.messages_box)
        self.add_widget(self.messages_list)

        # Botón Volver
        self.back_button = MDRaisedButton(text="Volver",
                                          size_hint=(None, None),
                                          size=("200dp", "50dp"),
                                          pos_hint={"center_x": 0.5},
                                          on_press=self.app.show_main_interface)
        self.add_widget(self.back_button)



# Clase principal de la aplicación
class SMTPApp(MDApp):
    def build(self):
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

    def on_start(self):
        self.theme_cls.primary_palette = "Purple"  # Color primario
        self.theme_cls.theme_style = "Dark"  # Estilo oscuro


if __name__ == "__main__":
    SMTPApp().run()
