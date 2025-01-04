import tkinter as tk
from openai import OpenAI

# Инициализация OpenAI
client = OpenAI(
    api_key="sk-C85aZs33Lcl3PjjoW3ZpD50SHQvDMT6l",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Функция для отправки сообщения и получения ответа
def send_message():
    user_input = user_entry.get()
    if not user_input.strip():
        return

    # Отображение сообщения пользователя
    chat_window.insert(tk.END, f"Вы: {user_input}\n")
    user_entry.delete(0, tk.END)

    # Отправка запроса к OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Вы - поэтический помощник, умеющий объяснять сложные программные концепции с творческим размахом."},
                {"role": "user", "content": user_input},
            ],
        )
        print(completion.choices[0].message.content)
        #print(completion.choices[0].message["Content"])

        response = completion.choices[0].message.content
        chat_window.insert(tk.END, f"GPT: {response}\n\n")

    except Exception as e:
        chat_window.insert(tk.END, f"Ошибка: {e}\n\n")

# Создание окна приложения
root = tk.Tk()
root.title("Чат с GPT")

# Окно для отображения сообщений
chat_window = tk.Text(root, height=20, width=50, state=tk.NORMAL)
chat_window.pack(padx=10, pady=10)

# Поле для ввода текста
user_entry = tk.Entry(root, width=40)
user_entry.pack(side=tk.LEFT, padx=10, pady=10)

# Кнопка для отправки сообщения
send_button = tk.Button(root, text="Отправить", command=send_message)
send_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Запуск приложения
root.mainloop()
