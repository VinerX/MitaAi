import socket
import datetime

class ChatServer:
    def __init__(self, gui,chat_model, host='127.0.0.1', port=12345, passive_port=12346):
        self.host = host
        self.port = port
        self.gui = gui
        self.passive_port = passive_port
        self.server_socket = None
        self.client_socket = None
        self.passive_client_socket = None
        self.passive_server_socket = None
        self.chat_model = chat_model
        self.MessagesToSay = list()
    def start(self):
        """Инициализирует и запускает сервер."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.passive_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passive_server_socket.bind((self.host, self.passive_port))
        self.passive_server_socket.listen(5)
        print(f"Сервер запущен на {self.host}:{self.passive_port}")

    def handle_connection(self):
        """Обрабатывает одно подключение."""
        if not self.server_socket:
            raise RuntimeError("Сервер не запущен. Вызовите start() перед handle_connection().")
        try:
            # Ожидание подключения
            self.client_socket, addr = self.server_socket.accept()
            #print(f"Подключен {addr}")

            # Получение сообщения от клиента
            received_text = self.client_socket.recv(1024).decode('utf-8')

            # Разделяем текст и ссылку по "|||"
            message, self.chat_model.distance = received_text.split("|||")

            response = ""
            if message == "":
                ...
            elif message == "waiting":
                if len(self.MessagesToSay)>0:
                    response = self.MessagesToSay.pop(0)
            elif message == "boring":
                date_now = datetime.datetime.now()
                response = self.generate_response("",f"Время{date_now}, Игрок долго молчит( Ты можешь что-то сказать или предпринять")
                self.gui.insertDialog("",response)
                print("Отправлено Мите на озвучку: " + response)
            else:
                # Если игрок отправил внутри игры, message его
                response = self.generate_response(message,"")
                #self.gui.insertDialog(message,response)
                print("Отправлено Мите на озвучку: " + response)


            # Отправка ответа обратно клиенту
            # Формируем сообщение через f-string с разделителем |||
            #print(f"Попытка отправить путь к файлу{self.gui.patch_to_sound_file}")
            message = f"{response}|||{self.gui.patch_to_sound_file}"
            self.gui.patch_to_sound_file = ""

            # Отправляем сообщение через сокет
            self.client_socket.send(message.encode('utf-8'))

            return True
        except Exception as e:
            print(f"Ошибка обработки подключения: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
            return False

    def generate_response(self, input_text,system_input_text):
        """Генерирует текст с помощью модели."""
        try:
            response = self.chat_model.generate_response(input_text,system_input_text)
            if input_text!="":
                self.gui.insertDialog(input_text,response)
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            response = "Произошла ошибка при обработке вашего сообщения."
        return response

    def send_message_to_server(self, message):
        self.MessagesToSay.append(message)

    def stop(self):
        """Закрывает сервер."""
        if self.server_socket:
            self.server_socket.close()
            print("Сервер остановлен.")
