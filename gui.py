import tkinter as tk
from chat_model import ChatModel

class ChatGUI:

    def __init__(self):
        self.model = ChatModel()
        self.root = tk.Tk()
        self.root.title("Чат с GPT")
        self.setup_ui()

    def setup_ui(self):
        self.root.config(bg="#2c2c2c")  # Установите темный цвет фона для всего окна

        self.chat_window = tk.Text(
            self.root, height=20, width=50, state=tk.NORMAL,
            bg="#1e1e1e", fg="#ffffff", insertbackground="white", wrap=tk.WORD
        )
        self.chat_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(self.root, bg="#2c2c2c")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.user_entry = tk.Entry(input_frame, width=40, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
        self.user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.user_entry.bind("<KeyRelease>", self.update_token_count)

        self.send_button = tk.Button(
            input_frame, text="Отправить", command=self.send_message,
            bg="#007acc", fg="#ffffff"
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)

        self.token_count_label = tk.Label(
            self.root, text=f"Токенов: 0/{self.model.max_input_tokens} | Ориент. стоимость: 0.0000 ₽",
            bg="#2c2c2c", fg="#ffffff"
        )
        self.token_count_label.pack(fill=tk.X, pady=5)

        self.setup_mood_controls()
        self.setup_history_controls()

    def setup_mood_controls(self):
        mood_frame = tk.Frame(self.root, bg="#2c2c2c")
        mood_frame.pack(fill=tk.X, pady=10)

        self.mood_label = tk.Label(
            mood_frame, text=f"Настроение: {self.model.mood}", bg="#2c2c2c", fg="#ffffff"
        )
        self.mood_label.pack(side=tk.LEFT, padx=5)

        mood_up_button = tk.Button(
            mood_frame, text="+", command=lambda: self.adjust_mood(5),
            bg="#007acc", fg="#ffffff"
        )
        mood_up_button.pack(side=tk.RIGHT, padx=5)

        mood_down_button = tk.Button(
            mood_frame, text="-", command=lambda: self.adjust_mood(-5),
            bg="#007acc", fg="#ffffff"
        )
        mood_down_button.pack(side=tk.RIGHT, padx=5)

    def setup_history_controls(self):
        history_frame = tk.Frame(self.root, bg="#2c2c2c")
        history_frame.pack(fill=tk.X, pady=10)

        load_button = tk.Button(
            history_frame, text="Загрузить историю", command=self.load_history,
            bg="#007acc", fg="#ffffff"
        )
        load_button.pack(side=tk.LEFT, padx=5)

        save_button = tk.Button(
            history_frame, text="Сохранить историю", command=self.save_history,
            bg="#007acc", fg="#ffffff"
        )
        save_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(
            history_frame, text="Очистить историю", command=self.clear_history,
            bg="#007acc", fg="#ffffff"
        )
        clear_button.pack(side=tk.LEFT, padx=5)

    def adjust_mood(self, amount):
        self.model.adjust_mood(amount)
        self.mood_label.config(text=f"Настроение: {self.model.mood}")

    def update_token_count(self, event=None):
        user_input = self.user_entry.get()
        token_count, cost = self.model.calculate_cost(user_input)
        self.token_count_label.config(
            text=f"Токенов: {token_count}/{self.model.max_input_tokens} | Ориент. стоимость: {cost:.4f} ₽"
        )

    def send_message(self):
        user_input = self.user_entry.get()
        if not user_input.strip():
            return

        self.chat_window.insert(tk.END, f"Вы: {user_input}\n", "user")
        self.user_entry.delete(0, tk.END)

        response = self.model.generate_response(user_input)
        self.chat_window.insert(tk.END, f"GPT: {response}\n\n", "gpt")

    def load_history(self):
        history = self.model.load_history()
        if history:
            self.chat_window.delete(1.0, tk.END)  # Очистить текущее окно чата
            for msg in history:
                role = "Вы" if msg["role"] == "user" else "GPT"
                self.chat_window.insert(tk.END, f"{role}: {msg['content']}\n", role.lower())

    def save_history(self):
        self.model.save_history()
        self.chat_window.insert(tk.END, "История сохранена.\n", "system")

    def clear_history(self):
        self.model.clear_history()
        self.chat_window.delete(1.0, tk.END)  # Очистить окно чата

    def run(self):
        self.root.mainloop()
