from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout

# Cambiar tamaño de la ventana
Window.size = (800, 600)
Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Fondo de color claro (puedes cambiar este color)

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.spacing = 15
        self.padding = 50
        self.add_widget(Label(text="SMTP Cliente / Servidor", font_size=30, color=(0, 0, 0, 1), bold=True))

        # Botón de Cliente
        self.client_button = Button(text="Soy Cliente", size_hint=(0.2, 0.1), background_color=(0.2, 0.6, 0.2, 1), font_size=18)
        self.client_button.bind(on_press=self.open_client_interface)
        self.client_button.pos_hint = {'right': 0.9, 'top': 0.9}  # Esquina superior derecha
        self.add_widget(self.client_button)

        # Botón de Servidor
        self.server_button = Button(text="Soy Servidor", size_hint=(0.2, 0.1), background_color=(0.6, 0.2, 0.2, 1), font_size=18)
        self.server_button.bind(on_press=self.open_server_interface)
        self.server_button.pos_hint = {'left': 0.1, 'top': 0.9}  # Esquina superior izquierda
        self.add_widget(self.server_button)

    def open_client_interface(self, instance):
        self.clear_widgets()
        self.add_widget(ClientWindow(main_app=self))

    def open_server_interface(self, instance):
        self.clear_widgets()
        self.add_widget(ServerWindow(main_app=self))

class ClientWindow(FloatLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.spacing = 10
        self.padding = 20

        self.add_widget(Label(text="Enviar Correo", font_size=24, color=(0, 0, 0, 1), pos_hint={'center_x': 0.5, 'top': 1}))

        self.add_widget(Label(text="Remitente:", size_hint=(None, None), pos_hint={'left': 0.1, 'top': 0.85}))
        self.sender_input = TextInput(font_size=18, size_hint=(0.8, None), height=40, pos_hint={'left': 0.1, 'top': 0.8})
        self.add_widget(self.sender_input)

        self.add_widget(Label(text="Destinatario:", size_hint=(None, None), pos_hint={'left': 0.1, 'top': 0.75}))
        self.recipient_input = TextInput(font_size=18, size_hint=(0.8, None), height=40, pos_hint={'left': 0.1, 'top': 0.7})
        self.add_widget(self.recipient_input)

        self.add_widget(Label(text="Asunto:", size_hint=(None, None), pos_hint={'left': 0.1, 'top': 0.65}))
        self.subject_input = TextInput(font_size=18, size_hint=(0.8, None), height=40, pos_hint={'left': 0.1, 'top': 0.6})
        self.add_widget(self.subject_input)

        self.add_widget(Label(text="Mensaje:", size_hint=(None, None), pos_hint={'left': 0.1, 'top': 0.5}))
        self.message_input = TextInput(multiline=True, font_size=18, size_hint=(0.8, None), height=200, pos_hint={'left': 0.1, 'top': 0.4})
        self.add_widget(self.message_input)

        # Botón Enviar
        self.send_button = Button(text="Enviar", size_hint=(None, None), size=(120, 50), background_color=(0.2, 0.6, 0.2, 1), font_size=18, pos_hint={'right': 0.9, 'top': 0.2})
        self.send_button.bind(on_press=self.send_sms)
        self.add_widget(self.send_button)

        # Botón Volver
        self.back_button = Button(text="Volver", size_hint=(None, None), size=(120, 50), background_color=(0.2, 0.2, 1, 1), font_size=18, pos_hint={'left': 0.1, 'top': 0.2})
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

    def send_sms(self, instance):
        sender = self.sender_input.text
        recipient = self.recipient_input.text
        subject = self.subject_input.text
        message = self.message_input.text

        if sender and recipient and subject and message:
            print(f"Mensaje enviado: {sender} -> {recipient}: {subject}")
        else:
            print("Todos los campos deben estar completos.")

    def go_back(self, instance):
        self.main_app.clear_widgets()
        self.main_app.add_widget(MainWindow())

class ServerWindow(BoxLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.main_app = main_app
        self.spacing = 10
        self.padding = 20

        self.add_widget(Label(text="Bandeja de Entrada", font_size=24, color=(0, 0, 0, 1)))

        # Mensajes de ejemplo
        self.messages_list = RecycleView(size_hint=(1, 0.7))
        self.messages_list.data = [
            {"text": "Asunto: Test - Remitente: user - Fecha: 01/01/2025"},
            {"text": "Asunto: Prueba - Remitente: admin - Fecha: 02/01/2025"}
        ]
        self.add_widget(self.messages_list)

        # Cuerpo del mensaje
        self.message_body = TextInput(text="Selecciona un mensaje para ver el contenido.", multiline=True, readonly=True, font_size=18, size_hint_y=None, height=200)
        self.add_widget(self.message_body)

        # Botón Volver
        self.back_button = Button(text="Volver", size_hint=(None, None), size=(120, 50), background_color=(0.2, 0.2, 1, 1), font_size=18, pos_hint={'center_x': 0.5, 'top': 0.2})
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)

    def go_back(self, instance):
        self.main_app.clear_widgets()
        self.main_app.add_widget(MainWindow())

class SMTPApp(App):
    def build(self):
        return MainWindow()

if __name__ == "__main__":
    SMTPApp().run()
