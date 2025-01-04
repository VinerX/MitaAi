import tkinter as tk
from openai import OpenAI
import tiktoken

# Инициализация OpenAI
client = OpenAI(
    api_key="sk-C85aZs33Lcl3PjjoW3ZpD50SHQvDMT6l",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Загрузка токенизатора для подсчёта токенов
tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")

# Функция для подсчёта токенов

def count_tokens(messages):
    num_tokens = 0
    for message in messages:
        num_tokens += len(tokenizer.encode(message["content"]))
    return num_tokens

# Установка лимита токенов
max_input_tokens = 2048

# Функция для обновления подсчёта токенов в режиме реального времени

def update_token_count(event=None):
    user_input = user_entry.get()
    messages = [
        {"role": "system", "content": "Вы - поэтический помощник, умеющий объяснять сложные программные концепции с творческим размахом."},
        {"role": "user", "content": user_input},
    ]
    current_tokens = count_tokens(messages)
    cost = (current_tokens / 1000) * 0.0432
    token_count_label.config(text=f"Токенов: {current_tokens}/{max_input_tokens} | Стоимость: {cost:.4f} USD")

# Функция для отправки сообщения и получения ответа

def send_message():
    user_input = user_entry.get()
    if not user_input.strip():
        return

    # Отображение сообщения пользователя
    chat_window.insert(tk.END, f"Вы: {user_input}\n")
    user_entry.delete(0, tk.END)

    # Формируем список сообщений для подсчёта токенов
    messages = [
        {"role": "system", "content": "Вы - поэтический помощник, умеющий объяснять сложные программные концепции с творческим размахом."},
        {"role": "user", "content": user_input},
    ]

    # Подсчёт токенов
    current_tokens = count_tokens(messages)
    cost = (current_tokens / 1000) * 0.0432
    token_count_label.config(text=f"Токенов: {current_tokens}/{max_input_tokens} | Стоимость: {cost:.4f} Рублей")

    if current_tokens > max_input_tokens:
        chat_window.insert(tk.END, "Превышено ограничение на количество токенов. Укоротите сообщение.\n\n")
        return

    # Отправка запроса к OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=100  # Ограничение длины ответа
        )

        response = completion.choices[0].message.content
        chat_window.insert(tk.END, f"GPT: {response}\n\n")

    except Exception as e:
        chat_window.insert(tk.END, f"Ошибка: {e}\n\n")

# Создание окна приложения
root = tk.Tk()
root.title("Чат с GPT")
root.configure(bg="#2c2c2c")

# Окно для отображения сообщений
chat_window = tk.Text(root, height=20, width=50, state=tk.NORMAL, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
chat_window.pack(padx=10, pady=10)

# Поле для ввода текста
user_entry = tk.Entry(root, width=40, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
user_entry.pack(side=tk.LEFT, padx=10, pady=10)
user_entry.bind("<KeyRelease>", update_token_count)

# Кнопка для отправки сообщения
send_button = tk.Button(root, text="Отправить", command=send_message, bg="#007acc", fg="#ffffff")
send_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Метка для отображения количества токенов
token_count_label = tk.Label(root, text=f"Токенов: 0/{max_input_tokens} | Стоимость: 0.0000 USD", bg="#2c2c2c", fg="#ffffff")
token_count_label.pack(pady=5)

# Запуск приложения
root.mainloop()
