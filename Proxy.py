import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI

# Инициализация OpenAI
client = OpenAI(
    api_key="sk-C85aZs33Lcl3PjjoW3ZpD50SHQvDMT6l",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Функция для отправки сообщения и получения ответа
def send_message():
    user_input = user_entry.get("1.0", tk.END).strip()
    if not user_input:
        return

    # Отображение сообщения пользователя
    chat_window.configure(state=tk.NORMAL)
    chat_window.insert(tk.END, f"\nВы: {user_input}\n", "user")
    chat_window.configure(state=tk.DISABLED)
    user_entry.delete("1.0", tk.END)

    # Отправка запроса к OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Вы - поэтический помощник, умеющий объяснять сложные программные концепции с творческим размахом."},
                {"role": "user", "content": user_input},
            ],
        )

        response = completion.choices[0].message.content
        chat_window.configure(state=tk.NORMAL)
        chat_window.insert(tk.END, f"GPT: {response}\n\n", "gpt")
        chat_window.configure(state=tk.DISABLED)
        chat_window.yview(tk.END)

    except Exception as e:
        chat_window.configure(state=tk.NORMAL)
        chat_window.insert(tk.END, f"Ошибка: {e}\n\n", "error")
        chat_window.configure(state=tk.DISABLED)

# Создание окна приложения
root = tk.Tk()
root.title("Чат с GPT")
root.geometry("600x700")
root.configure(bg="#2b2b2b")

# Окно для отображения сообщений
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=30, width=80, state=tk.DISABLED, bg="#1e1e1e", fg="#dcdcdc", font=("Arial", 12))
chat_window.tag_configure("user", foreground="#a8c023")
chat_window.tag_configure("gpt", foreground="#6a8759")
chat_window.tag_configure("error", foreground="#ff6b68")
chat_window.pack(padx=10, pady=(10, 0), fill=tk.BOTH, expand=True)

# Поле для ввода текста
user_entry = tk.Text(root, height=4, bg="#3c3f41", fg="#dcdcdc", font=("Arial", 12), insertbackground="white")
user_entry.pack(padx=10, pady=(10, 5), fill=tk.X)

# Кнопка для отправки сообщения
send_button = tk.Button(root, text="Отправить", command=send_message, bg="#5e5e5e", fg="#ffffff", font=("Arial", 12), activebackground="#6a8759", activeforeground="#ffffff")
send_button.pack(padx=10, pady=(0, 10))

# Запуск приложения
root.mainloop()
