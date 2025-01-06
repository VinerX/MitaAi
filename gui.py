import tkinter as tk
from chat_model import ChatModel

class ChatGUI:

    def __init__(self):
        self.model = ChatModel()
        self.root = tk.Tk()
        self.root.title("Чат с GPT")
        self.api_key = ""
        self.api_url = ""
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

        # Добавление обработчика для вставки текста
        self.user_entry.bind("<Control-v>", self.paste_from_clipboard)

        self.setup_mood_controls()
        self.setup_stress_controls()
        self.setup_cognitive_load_controls()
        self.setup_madness_controls()
        self.setup_secret_controls()
        self.setup_history_controls()
        self.setup_debug_controls()
        self.setup_api_controls()

    def setup_mood_controls(self):
        mood_frame = tk.Frame(self.root, bg="#2c2c2c")
        mood_frame.pack(fill=tk.X, pady=5)

        self.mood_label = tk.Label(
            mood_frame, text=f"Настроение: {self.model.mood}", bg="#2c2c2c", fg="#ffffff"
        )
        self.mood_label.pack(side=tk.LEFT, padx=5)

        mood_up_button = tk.Button(
            mood_frame, text="+", command=lambda: self.adjust_mood(15),
            bg="#007acc", fg="#ffffff"
        )
        mood_up_button.pack(side=tk.RIGHT, padx=5)

        mood_down_button = tk.Button(
            mood_frame, text="-", command=lambda: self.adjust_mood(-15),
            bg="#007acc", fg="#ffffff"
        )
        mood_down_button.pack(side=tk.RIGHT, padx=5)

    def setup_stress_controls(self):
        stress_frame = tk.Frame(self.root, bg="#2c2c2c")
        stress_frame.pack(fill=tk.X, pady=5)

        self.stress_label = tk.Label(
            stress_frame, text=f"Стресс: {self.model.stress}", bg="#2c2c2c", fg="#ffffff"
        )
        self.stress_label.pack(side=tk.LEFT, padx=5)

        stress_up_button = tk.Button(
            stress_frame, text="+", command=lambda: self.adjust_stress(15),
            bg="#007acc", fg="#ffffff"
        )
        stress_up_button.pack(side=tk.RIGHT, padx=5)

        stress_down_button = tk.Button(
            stress_frame, text="-", command=lambda: self.adjust_stress(-15),
            bg="#007acc", fg="#ffffff"
        )
        stress_down_button.pack(side=tk.RIGHT, padx=5)

    def setup_cognitive_load_controls(self):
        cognitive_frame = tk.Frame(self.root, bg="#2c2c2c")
        cognitive_frame.pack(fill=tk.X, pady=5)

        self.cognitive_label = tk.Label(
            cognitive_frame, text=f"Когнитивная нагрузка: {self.model.cognitive_load}", bg="#2c2c2c", fg="#ffffff"
        )
        self.cognitive_label.pack(side=tk.LEFT, padx=5)

        cognitive_up_button = tk.Button(
            cognitive_frame, text="+", command=lambda: self.adjust_cognitive_load(15),
            bg="#007acc", fg="#ffffff"
        )
        cognitive_up_button.pack(side=tk.RIGHT, padx=5)

        cognitive_down_button = tk.Button(
            cognitive_frame, text="-", command=lambda: self.adjust_cognitive_load(-15),
            bg="#007acc", fg="#ffffff"
        )
        cognitive_down_button.pack(side=tk.RIGHT, padx=5)

    def setup_madness_controls(self):
        madness_frame = tk.Frame(self.root, bg="#2c2c2c")
        madness_frame.pack(fill=tk.X, pady=5)

        self.madness_label = tk.Label(
            madness_frame, text=f"Безумие: {self.model.madness}", bg="#2c2c2c", fg="#ffffff"
        )
        self.madness_label.pack(side=tk.LEFT, padx=5)

        madness_up_button = tk.Button(
            madness_frame, text="+", command=lambda: self.adjust_madness(15),
            bg="#007acc", fg="#ffffff"
        )
        madness_up_button.pack(side=tk.RIGHT, padx=5)

        madness_down_button = tk.Button(
            madness_frame, text="-", command=lambda: self.adjust_madness(-15),
            bg="#007acc", fg="#ffffff"
        )
        madness_down_button.pack(side=tk.RIGHT, padx=5)

    def setup_secret_controls(self):
        secret_frame = tk.Frame(self.root, bg="#2c2c2c")
        secret_frame.pack(fill=tk.X, pady=5)

        self.secret_var = tk.BooleanVar(value=self.model.secretExposed)

        secret_checkbox = tk.Checkbutton(
            secret_frame, text="Секрет раскрыт", variable=self.secret_var,
            bg="#2c2c2c", fg="#ffffff", command=self.adjust_secret
        )
        secret_checkbox.pack(side=tk.LEFT, padx=5)

    def setup_history_controls(self):
        history_frame = tk.Frame(self.root, bg="#2c2c2c")
        history_frame.pack(fill=tk.X, pady=5)

        clear_button = tk.Button(
            history_frame, text="Очистить историю", command=self.clear_history,
            bg="#007acc", fg="#ffffff"
        )
        clear_button.pack(side=tk.LEFT, padx=5)

    def setup_debug_controls(self):
        debug_frame = tk.Frame(self.root, bg="#2c2c2c")
        debug_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.debug_window = tk.Text(
            debug_frame, height=5, width=50, bg="#1e1e1e", fg="#ffffff",
            state=tk.NORMAL, wrap=tk.WORD, insertbackground="white"
        )
        self.debug_window.pack(fill=tk.BOTH, expand=True)

        self.update_debug_info()  # Отобразить изначальное состояние переменных

    def setup_api_controls(self):
        api_frame = tk.Frame(self.root, bg="#2c2c2c")
        api_frame.pack(fill=tk.X, pady=10)

        self.show_api_var = tk.BooleanVar(value=False)

        api_toggle = tk.Checkbutton(
            api_frame, text="Показать настройки API", variable=self.show_api_var,
            command=self.toggle_api_settings, bg="#2c2c2c", fg="#ffffff"
        )
        api_toggle.pack(side=tk.LEFT, padx=5)

        self.api_settings_frame = tk.Frame(self.root, bg="#2c2c2c")

        tk.Label(
            self.api_settings_frame, text="API-ключ:", bg="#2c2c2c", fg="#ffffff"
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.api_key_entry = tk.Entry(self.api_settings_frame, width=50, bg="#1e1e1e", fg="#ffffff",
                                      insertbackground="white")
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(
            self.api_settings_frame, text="Ссылка:", bg="#2c2c2c", fg="#ffffff"
        ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.api_url_entry = tk.Entry(self.api_settings_frame, width=50, bg="#1e1e1e", fg="#ffffff",
                                      insertbackground="white")
        self.api_url_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        save_button = tk.Button(
            self.api_settings_frame, text="Сохранить", command=self.save_api_settings,
            bg="#007acc", fg="#ffffff"
        )
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def paste_from_clipboard(self, event=None):
        try:
            clipboard_content = self.root.clipboard_get()
            self.user_entry.insert(tk.INSERT, clipboard_content)
        except tk.TclError:
            pass  # Если буфер обмена пуст, ничего не делаем
    def save_api_settings(self):
        self.api_key = self.api_key_entry.get()
        self.api_url = self.api_url_entry.get()
        self.model.set_api_key(self.api_key)
        self.model.set_api_url(self.api_url)
        print(f"API-ключ сохранён: {self.api_key}")
        print(f"Ссылка API сохранена: {self.api_url}")

    def toggle_api_settings(self):
        if self.show_api_var.get():
            self.api_settings_frame.pack(fill=tk.X, padx=10, pady=10)
        else:
            self.api_settings_frame.pack_forget()
    def update_debug_info(self):
        """Обновить окно отладки с отображением актуальных данных."""
        self.debug_window.delete(1.0, tk.END)  # Очистить старые данные
        debug_info = (
            f"Отношение к игроку: {self.model.mood}\n"
            f"Стресс: {self.model.stress}\n"
            f"Когнитивная нагрузка: {self.model.cognitive_load}\n"
            f"Безумие: {self.model.madness}\n"
            f"Секрет: {self.model.secretExposed}\n"
        )
        self.debug_window.insert(tk.END, debug_info)

    def adjust_mood(self, amount):
        self.model.adjust_mood(amount)
        self.mood_label.config(text=f"Настроение: {self.model.mood}")
        self.update_debug_info()

    def adjust_stress(self, amount):
        self.model.adjust_stress(amount)
        self.stress_label.config(text=f"Стресс: {self.model.stress}")
        self.update_debug_info()

    def adjust_cognitive_load(self, amount):
        self.model.adjust_cognitive_load(amount)
        self.cognitive_label.config(text=f"Когнитивная нагрузка: {self.model.cognitive_load}")
        self.update_debug_info()

    def adjust_madness(self, amount):
        self.model.adjust_madness(amount)
        self.madness_label.config(text=f"Безумие: {self.model.madness}")
        self.update_debug_info()

    def adjust_secret(self):
        self.model.secretExposed = not self.model.secretExposed
        self.update_debug_info()

    def update_token_count(self, event=None):
        user_input = self.user_entry.get()
        token_count, cost = self.model.calculate_cost(user_input)
        self.token_count_label.config(
            text=f"Токенов: {token_count}/{self.model.max_input_tokens} | Ориент. стоимость: {cost:.4f} ₽"
        )
        self.update_debug_info()

    def send_message(self):
        user_input = self.user_entry.get()
        if not user_input.strip():
            return

        self.chat_window.insert(tk.END, f"Вы: {user_input}\n", "user")
        self.user_entry.delete(0, tk.END)

        response = self.model.generate_response(user_input)
        self.chat_window.insert(tk.END, f"Мита: {response}\n\n", "gpt")
        self.update_debug_info()

    def clear_history(self):
        self.model.clear_history()
        self.chat_window.delete(1.0, tk.END)
        self.update_debug_info()

    def run(self):
        self.root.mainloop()
