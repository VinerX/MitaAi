import tkinter as tk
from chat_model import ChatModel
from server import ChatServer
import threading


class ChatGUI:

    def __init__(self):
        self.model = ChatModel(self)
        self.server = ChatServer(self,self.model)

        self.server_thread = None
        self.running = False
        self.start_server()

        self.root = tk.Tk()
        self.root.title("Чат с MitaAI")
        self.api_key = "sk-PkNRM8HNkAeVadcJEwKVW6c8OTtafs6f"
        self.api_url = "https://api.proxyapi.ru/openai/v1"
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

        # Привязка для вставки с использованием Control-Insert
        self.user_entry.bind("<Control-Insert>", self.paste_from_clipboard)
        # Привязка обработчика для Ctrl+C
        self.user_entry.bind("<Control-KeyPress-C>", self.copy_to_clipboard)
        # Устанавливаем обработчик закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_attitude_controls()
        self.setup_boredom_controls()
        self.setup_stress_controls()

        self.setup_secret_controls()

        self.setup_update_promts()
        self.setup_history_controls()
        self.setup_debug_controls()
        self.setup_api_controls()

        self.load_chat_history()  # Загрузить историю чата

        #self.send_message("Игрок только что зашел в игру")

    def setup_attitude_controls(self):
        attitude_frame = tk.Frame(self.root, bg="#2c2c2c")
        attitude_frame.pack(fill=tk.X, pady=5)

        self.mood_label = tk.Label(
            attitude_frame, text=f"Настроение: {self.model.attitude}", bg="#2c2c2c", fg="#ffffff"
        )
        self.mood_label.pack(side=tk.LEFT, padx=5)

        mood_up_button = tk.Button(
            attitude_frame, text="+", command=lambda: self.adjust_attitude(15),
            bg="#007acc", fg="#ffffff"
        )
        mood_up_button.pack(side=tk.RIGHT, padx=5)

        mood_down_button = tk.Button(
            attitude_frame, text="-", command=lambda: self.adjust_attitude(-15),
            bg="#007acc", fg="#ffffff"
        )
        mood_down_button.pack(side=tk.RIGHT, padx=5)

    def setup_boredom_controls(self):
        boredom_frame = tk.Frame(self.root, bg="#2c2c2c")
        boredom_frame.pack(fill=tk.X, pady=5)

        self.boredom_label = tk.Label(
            boredom_frame, text=f"Скука: {self.model.boredom}", bg="#2c2c2c", fg="#ffffff"
        )
        self.boredom_label.pack(side=tk.LEFT, padx=5)

        stress_up_button = tk.Button(
            boredom_frame, text="+", command=lambda: self.adjust_boredom(15),
            bg="#007acc", fg="#ffffff"
        )
        stress_up_button.pack(side=tk.RIGHT, padx=5)

        stress_down_button = tk.Button(
            boredom_frame, text="-", command=lambda: self.adjust_boredom(-15),
            bg="#007acc", fg="#ffffff"
        )
        stress_down_button.pack(side=tk.RIGHT, padx=5)

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

    def setup_secret_controls(self):
        secret_frame = tk.Frame(self.root, bg="#2c2c2c")
        secret_frame.pack(fill=tk.X, pady=5)

        self.secret_var = tk.BooleanVar(value=self.model.secretExposed)

        secret_checkbox = tk.Checkbutton(
            secret_frame, text="Секрет раскрыт", variable=self.secret_var,
            bg="#2c2c2c", fg="#ffffff", command=self.adjust_secret
        )
        secret_checkbox.pack(side=tk.LEFT, padx=5)

    def setup_update_promts(self):
        update_promts_frame = tk.Frame(self.root, bg="#2c2c2c")
        update_promts_frame.pack(fill=tk.X, pady=5)

        # Кнопка для обновления промтов
        update_button = tk.Button(
            update_promts_frame, text="Обновить промты раскрыт",
            bg="#2c2c2c", fg="#ffffff", command=self.model.load_prompts
        )
        update_button.pack(side=tk.LEFT, padx=5)

    def setup_history_controls(self):
        history_frame = tk.Frame(self.root, bg="#2c2c2c")
        history_frame.pack(fill=tk.X, pady=5)

        clear_button = tk.Button(
            history_frame, text="Очистить историю", command=self.clear_history,
            bg="#007acc", fg="#ffffff"
        )
        clear_button.pack(side=tk.LEFT, padx=5)

    def load_chat_history(self):
        self.model.load_history()
        """Загрузить историю из модели и отобразить в интерфейсе."""
        for entry in self.model.chat_history:
            role = entry["role"]
            content = entry["content"]
            if role == "user":
                self.chat_window.insert(tk.END, f"Вы: {content}\n", "user")
            elif role == "assistant":
                self.chat_window.insert(tk.END, f"Мита: {content}\n\n", "gpt")

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

    def copy_to_clipboard(self, event=None):
        try:
            # Получение выделенного текста из поля ввода
            selected_text = self.user_entry.selection_get()
            # Копирование текста в буфер обмена
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.root.update()  # Обновление буфера обмена
        except tk.TclError:
            # Если текст не выделен, ничего не делать
            pass

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
            f"Отношение к игроку: {self.model.attitude}\n"
            f"Скука: {self.model.boredom}\n"
            f"Стресс: {self.model.stress}\n"

            f"Секрет: {self.model.secretExposed}\n"
        )
        self.debug_window.insert(tk.END, debug_info)

    def adjust_attitude(self, amount):
        self.model.adjust_attitude(amount)
        self.mood_label.config(text=f"Отношение: {self.model.attitude}")
        self.update_debug_info()

    def adjust_boredom(self, amount):
        self.model.adjust_boredom(amount)
        self.boredom_label.config(text=f"Скука: {self.model.boredom}")
        self.update_debug_info()

    def adjust_stress(self, amount):
        self.model.adjust_stress(amount)
        self.stress_label.config(text=f"Стресс: {self.model.stress}")
        self.update_debug_info()

    def adjust_secret(self):
        self.model.secretExposed = not self.model.secretExposed
        self.update_debug_info()

    def update_token_count(self, event=None):
        if False and self.model.hasTokenizer:
            user_input = self.user_entry.get()
            token_count, cost = self.model.calculate_cost(user_input)
            self.token_count_label.config(
                text=f"ВЫКЛЮЧЕНО!! Токенов: {token_count}/{self.model.max_input_tokens} | Ориент. стоимость: {cost:.4f} ₽"
            )
            self.update_debug_info()

    def insertDialog(self,input_text="",response=""):
        if input_text != "":
            self.chat_window.insert(tk.END, f"Вы: {input_text}\n", "user")
        if response != "":
            self.chat_window.insert(tk.END, f"Мита: {response}\n", "Gpt")

    def send_message(self, system_input=""):
        user_input = self.user_entry.get()
        if not user_input.strip() and system_input == "":
            return

        if user_input != "":
            self.chat_window.insert(tk.END, f"Вы: {user_input}\n", "user")
            self.user_entry.delete(0, tk.END)

        response = self.model.generate_response(user_input, system_input)
        self.chat_window.insert(tk.END, f"Мита: {response}\n\n", "gpt")
        # Отправка сообщения на сервер
        if self.server:
            try:
                # Отправляем сообщение клиенту через сервер
                if self.server.client_socket:
                    self.server.send_message_to_server(response)
                    print("Сообщение отправлено на сервер.")
                else:
                    print("Нет активного подключения к клиенту.")
            except Exception as e:
                print(f"Ошибка при отправке сообщения на сервер: {e}")

        # Генерация ответа модели для локального отображения (опционально)


        self.update_debug_info()


    def clear_history(self):
        self.model.clear_history()
        self.chat_window.delete(1.0, tk.END)
        self.update_debug_info()

    def run(self):
        self.root.mainloop()

    def start_server(self):
        """Запускает сервер в отдельном потоке."""
        if not self.running:
            self.running = True
            self.server.start()  # Инициализация сокета
            self.server_thread = threading.Thread(target=self.run_server_loop, daemon=True)
            self.server_thread.start()
            print("Сервер запущен.")

    def stop_server(self):
        """Останавливает сервер."""
        if self.running:
            self.running = False
            self.server.stop()
            print("Сервер остановлен.")

    def run_server_loop(self):
        """Цикл обработки подключений сервера."""
        while self.running:
            needUpdate = self.server.handle_connection()
            if needUpdate:
                self.load_chat_history()

    def on_closing(self):
        self.stop_server()
        self.send_message("Игрок покинул игру")
        print("Закрываемся")
        self.root.destroy()
        #1

    def close_app(self):
        """Закрытие приложения корректным образом."""
        print("Завершение программы...")
        self.root.destroy()  # Закрывает GUI
