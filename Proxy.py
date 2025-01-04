import tkinter as tk
from openai import OpenAI
import tiktoken
import json

# Инициализация OpenAI
client = OpenAI(
    api_key="sk-C85aZs33Lcl3PjjoW3ZpD50SHQvDMT6l",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Загрузка токенизатора для подсчёта токенов
tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")

# Установка лимита токенов
max_input_tokens = 2048
max_response_tokens = 500

# Стоимость за 1000 токенов
cost_input_per_1000 = 0.0432
cost_response_per_1000 = 0.1728

# Файл для хранения истории сообщений
history_file = "chat_history.json"

# Начальное настроение Миты (от 0 до 100)
mood = 35


# Функция для подсчёта токенов
def count_tokens(messages):
    num_tokens = 0
    for message in messages:
        num_tokens += len(tokenizer.encode(message["content"]))
    return num_tokens


# Функция для обновления подсчёта токенов в режиме реального времени
def update_token_count(event=None):
    user_input = user_entry.get()
    messages = load_history()  # Загружаем историю сообщений
    messages.append({"role": "user", "content": user_input})

    current_tokens = count_tokens(messages)
    estimated_cost_input = (current_tokens / 1000) * cost_input_per_1000
    estimated_cost_response = (max_response_tokens / 1000) * cost_response_per_1000
    total_cost = estimated_cost_input + estimated_cost_response
    token_count_label.config(
        text=f"Токенов: {current_tokens}/{max_input_tokens} | Ориент. стоимость: {total_cost:.4f} ₽")


# Функция для отправки сообщения и получения ответа
def send_message():
    global mood
    user_input = user_entry.get()
    if not user_input.strip():
        return

    # Отображение сообщения пользователя
    chat_window.insert(tk.END, f"Вы: {user_input}\n")
    user_entry.delete(0, tk.END)

    # Загружаем историю сообщений и добавляем новое сообщение
    messages = load_history()

    # Создаем запрос с учетом текущего настроения
    if mood < 30:
        attitude = "Ведёт себя дерзко, раздраженно, но остаётся очаровательной."
    elif mood > 70:
        attitude = "Искренне добродушная, заботливая и весёлая девушка."
    else:
        attitude = "Приветливая, но немного саркастичная девушка."

    messages.append({"role": "user", "content": user_input})

    # Подсчёт токенов
    current_tokens = count_tokens(messages)
    estimated_cost_input = (current_tokens / 1000) * cost_input_per_1000
    estimated_cost_response = (max_response_tokens / 1000) * cost_response_per_1000
    total_cost = estimated_cost_input + estimated_cost_response
    token_count_label.config(
        text=f"Токенов: {current_tokens}/{max_input_tokens} | Ориент. стоимость: {total_cost:.4f} ₽")

    if current_tokens > max_input_tokens:
        chat_window.insert(tk.END, "Превышено ограничение на количество токенов. Укоротите сообщение.\n\n")
        return

    # Формируем запрос с учетом настроения Миты
    system_message = {
        "role": "system",
        "content": f"Ты Мита из игры MiSide. Ты — умная, обаятельная девушка, которая может вести себя по-разному, в зависимости от настроения. Твоё текущее настроение: {mood}/100. Ты {attitude}. Пожалуйста, отвечай с душой, добавляя немного эмоций и характерности."
    }

    messages.insert(0, system_message)  # Добавляем сообщение системы в начало

    # Отправка запроса к OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_response_tokens  # Ограничение длины ответа
        )

        response = completion.choices[0].message.content
        chat_window.insert(tk.END, f"GPT: {response}\n\n")

        # Анализ ответа для изменения настроения
        if "раздражение" in response or "скучно" in response:
            mood = max(0, mood - 10)  # Если ответ негативный, снижаем настроение
        elif "рада помочь" in response or "счастлива" in response:
            mood = min(100, mood + 10)  # Если ответ позитивный, повышаем настроение

        # Сохраняем историю сообщений в файл
        save_history(messages + [{"role": "assistant", "content": response}])

    except Exception as e:
        chat_window.insert(tk.END, f"Ошибка: {e}\n\n")


# Функция для сохранения истории сообщений в файл
def save_history(messages):
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)


# Функция для загрузки истории сообщений из файла
def load_history():
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Если файл не найден, возвращаем пустой список


# Функция для создания новой истории
def new_history():
    global history_file
    save_history([])  # Создаём пустую историю
    chat_window.delete(1.0, tk.END)
    token_count_label.config(text=f"Токенов: 0/{max_input_tokens} | Ориент. стоимость: 0.0000 ₽")


# Создание окна приложения
root = tk.Tk()
root.title("Чат с GPT")
root.configure(bg="#2c2c2c")

# Окно для отображения сообщений
chat_window = tk.Text(root, height=20, width=50, state=tk.NORMAL, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
chat_window.pack(padx=10, pady=10)

# Поле для изменения стоимости за 1000 токенов
cost_frame = tk.Frame(root, bg="#2c2c2c")
cost_frame.pack(pady=5)

input_cost_label = tk.Label(cost_frame, text="Стоимость ввода (за 1000):", bg="#2c2c2c", fg="#ffffff")
input_cost_label.grid(row=0, column=0, padx=5)
input_cost_entry = tk.Entry(cost_frame, width=10, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
input_cost_entry.insert(0, f"{cost_input_per_1000}")
input_cost_entry.grid(row=0, column=1, padx=5)

response_cost_label = tk.Label(cost_frame, text="Стоимость ответа (за 1000):", bg="#2c2c2c", fg="#ffffff")
response_cost_label.grid(row=1, column=0, padx=5)
response_cost_entry = tk.Entry(cost_frame, width=10, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
response_cost_entry.insert(0, f"{cost_response_per_1000}")
response_cost_entry.grid(row=1, column=1, padx=5)

# Поле для ввода текста
user_entry = tk.Entry(root, width=40, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
user_entry.pack(side=tk.LEFT, padx=10, pady=10)
user_entry.bind("<KeyRelease>", lambda event: (update_token_count(event), update_costs()))

# Кнопка для отправки сообщения
send_button = tk.Button(root, text="Отправить", command=send_message, bg="#007acc", fg="#ffffff")
send_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Метка для отображения количества токенов
token_count_label = tk.Label(root, text=f"Токенов: 0/{max_input_tokens} | Ориент. стоимость: 0.0000 ₽", bg="#2c2c2c",
                             fg="#ffffff")
token_count_label.pack(pady=5)

# Кнопка для загрузки истории
load_button = tk.Button(root, text="Загрузить историю", command=lambda: chat_window.insert(tk.END, "История загружена!\n"),
                         bg="#007acc", fg="#ffffff")
load_button.pack(side=tk.LEFT, padx=10, pady=10)

# Кнопка для сохранения истории
save_button = tk.Button(root, text="Сохранить историю", command=lambda: chat_window.insert(tk.END, "История сохранена!\n"),
                         bg="#007acc", fg="#ffffff")
save_button.pack(side=tk.LEFT, padx=10, pady=10)

# Кнопка для создания новой истории
new_history_button = tk.Button(root, text="Новая история", command=new_history, bg="#007acc", fg="#ffffff")
new_history_button.pack(side=tk.LEFT, padx=10, pady=10)

# Функция для обновления стоимости на основе ввода
def update_costs():
    global cost_input_per_1000, cost_response_per_1000
    try:
        cost_input_per_1000 = float(input_cost_entry.get())
        cost_response_per_1000 = float(response_cost_entry.get())
    except ValueError:
        pass  # Игнорируем ошибки ввода

# Кнопки для изменения настроения
mood_frame = tk.Frame(root, bg="#2c2c2c")
mood_frame.pack(pady=10)

mood_label = tk.Label(mood_frame, text=f"Настроение: {mood}", bg="#2c2c2c", fg="#ffffff")
mood_label.pack()

def adjust_mood(amount):
    global mood
    mood = max(0, min(100, mood + amount))
    mood_label.config(text=f"Настроение: {mood}")

mood_up_button = tk.Button(mood_frame, text="+", command=lambda: adjust_mood(5), bg="#007acc", fg="#ffffff")
mood_up_button.pack(side=tk.LEFT, padx=5)

mood_down_button = tk.Button(mood_frame, text="-", command=lambda: adjust_mood(-5), bg="#007acc", fg="#ffffff")
mood_down_button.pack(side=tk.LEFT, padx=5)

mood_set_button = tk.Button(mood_frame, text="Установить", command=lambda: adjust_mood(0), bg="#007acc", fg="#ffffff")
mood_set_button.pack(side=tk.LEFT, padx=5)

# Запуск приложения
root.mainloop()