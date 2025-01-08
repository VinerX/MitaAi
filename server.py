import socket


class ChatServer:
    def __init__(self, gui,chat_model, host='127.0.0.1', port=12345, passive_port=12345):
        self.host = host
        self.port = port
        self.gui = gui
        self.passive_port = passive_port
        self.server_socket = None
        self.client_socket = None
        self.chat_model = chat_model

    def start(self):
        """Инициализирует и запускает сервер."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Сервер запущен на {self.host}:{self.port}")

    def handle_connection(self):
        """Обрабатывает одно подключение."""
        if not self.server_socket:
            raise RuntimeError("Сервер не запущен. Вызовите start() перед handle_connection().")
        try:
            # Ожидание подключения
            self.client_socket, addr = self.server_socket.accept()
            print(f"Подключен {addr}")

            # Получение сообщения от клиента
            message = self.client_socket.recv(1024).decode('utf-8')
            print(f"Получено сообщение: {message}")

            # Генерация ответа
            response = self.generate_response(message)

            # Отправка ответа обратно клиенту
            self.client_socket.send(response.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Ошибка обработки подключения: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
            return False

    def generate_response(self, input_text):
        """Генерирует текст с помощью модели."""
        try:
            response = self.chat_model.generate_response(input_text)
            self.gui.insertDialog(input_text,response)
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            response = "Произошла ошибка при обработке вашего сообщения."
        return response

    def send_message_to_server(self, message):
        """Отправляет сообщение на порт пассивный, чтобы пассивное подключение получило его."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.passive_port))
                client_socket.send(message.encode('utf-8'))
                print(f"Отправлено сообщение на порт {self.passive_port}: {message}")

                # Получение ответа от сервера
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Получен ответ: {response}")
                return response
        except Exception as e:
            print(f"Ошибка отправки сообщения на порт {self.passive_port}: {e}")
            return None

    def stop(self):
        """Закрывает сервер."""
        if self.server_socket:
            self.server_socket.close()
            print("Сервер остановлен.")
