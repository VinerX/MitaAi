import socket
import chat_model
def generate_text(input_text):
    return ChatModel.generate_response()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 12345))
server.listen(5)

print("Ожидаем соединение...")
while True:
    client_socket, addr = server.accept()
    print(f"Подключен {addr}")

    # Получаем сообщение от клиента
    message = client_socket.recv(1024).decode('utf-8')
    print(f"Получено сообщение: {message}")

    # Генерируем ответ
    response = generate_text(message)

    # Отправляем ответ обратно клиенту
    client_socket.send(response.encode('utf-8'))
    client_socket.close()
