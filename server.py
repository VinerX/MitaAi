import socket
import datetime


class ChatServer:
    def __init__(self, gui, chat_model, host='127.0.0.1', port=12345, passive_port=12346):
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
        self.gui.ConnectedToGame = True

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
            message, isMessageSystem, one_system_message, new_long_system_message, self.chat_model.updated_info = received_text.split(
                "|||")

            if one_system_message != "":
                self.chat_model.write_message_in_history(one_system_message)
            if new_long_system_message != "":
                self.chat_model.write_message_in_history(new_long_system_message)

            if isMessageSystem:
                response = self.generate_response("", message)
            else:
                response = self.generate_response(message, "")

            # Отправка ответа обратно клиенту
            answer = f"{response}|||{self.gui.patch_to_sound_file}"

            print(f"answer {answer}")

            self.gui.patch_to_sound_file = ""

            # Отправляем сообщение через сокет
            self.client_socket.send(answer.encode('utf-8'))
            self.gui.ConnectedToGame = True
            return True
        except Exception as e:
            print(f"Ошибка обработки подключения: {e}")
            self.gui.ConnectedToGame = False
        finally:
            if self.client_socket:
                self.client_socket.close()
            return False

    def generate_response(self, input_text, system_input_text):
        """Генерирует текст с помощью модели."""
        try:
            response = self.chat_model.generate_response(input_text, system_input_text)
            counter = 0
            #while self.chat_model.repeatResponse and counter<3:
            #   response += self.chat_model.generate_response("", "")
            # counter+=1

            if input_text != "":
                self.gui.insertDialog(input_text, response)
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
            self.gui.ConnectedToGame = False
