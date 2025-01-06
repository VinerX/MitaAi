import json

import requests
import tiktoken
from openai import OpenAI
import os
import sys
import datetime

from g4f.client import Client


class ChatModel:
    def __init__(self):

        self.api_key = "sk-Ct9J32W6P6yJpuoOLOYYp9nundsVbqJA"
        self.api_url = "https://api.proxyapi.ru/openai/v1"

        self.client = OpenAI(api_key="sk-Ct9J32W6P6yJpuoOLOYYp9nundsVbqJA",
                             base_url="https://api.proxyapi.ru/openai/v1")

        #self.client = Client()

        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
            self.hasTokenizer = True
        except:
            print("Тиктокен не сработал(")
            self.hasTokenizer = False

        self.max_input_tokens = 2048
        self.max_response_tokens = 3250
        self.cost_input_per_1000 = 0.0432
        self.cost_response_per_1000 = 0.1728
        self.history_file = "chat_history.json"
        self.chat_history = self.load_history().get('messages', [])
        self.memory_limit = 30  # Ограничение сообщения
        self.attitude = 60
        self.boredom = 0
        self.stress = 0

        self.secretExposed = False
        self.secretExposedFirst = False
        # Загрузка данных из файлов
        self.common = self.load_text_from_file("Promts/Main/common.txt")
        self.main = self.load_text_from_file("Promts/Main/main.txt")
        self.player = self.load_text_from_file("Promts/Main/player.txt")
        self.mainPlaying = self.load_text_from_file("Promts/Main/mainPlaing.txt")
        self.PlayingFirst = False
        self.mainCrazy = self.load_text_from_file("Promts/Main/mainCrazy.txt")

        self.examplesLong = self.load_text_from_file("Promts/Context/examplesLong.txt")
        self.examplesLongCrazy = self.load_text_from_file("Promts/Context/examplesLongCrazy.txt")

        self.world = self.load_text_from_file("Promts/Context/world.txt")
        self.mita_history = self.load_text_from_file("Promts/Context/mita_history.txt")

        self.variableEffects = self.load_text_from_file("Promts/Structural/VariablesEffects.txt")
        self.response_structure = self.load_text_from_file("Promts/Structural/response_structure.txt")

        self.SecretExposed = self.load_text_from_file("Promts/Events/SecretExposed.txt")

        self.MitaMainBehaviour = []
        self.MitaExamples = []
        self.systemMessages = []
        self.HideAiData = False
        #print_ip_and_country()

    @staticmethod
    def load_text_from_file(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def load_json_file(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Файл {filepath} не найден.")
            return {}

    def calculate_cost(self, user_input):
        # Загружаем историю
        history_data = self.load_history()

        # Получаем только сообщения
        messages = history_data.get('messages', [])

        # Добавляем новое сообщение от пользователя
        messages.append({"role": "user", "content": user_input})

        # Считаем токены
        token_count = self.count_tokens(messages)

        # Рассчитываем стоимость
        cost = (token_count / 1000) * self.cost_input_per_1000

        return token_count, cost

    def count_tokens(self, messages):
        return sum(len(self.tokenizer.encode(msg["content"])) for msg in messages if
                   isinstance(msg, dict) and "content" in msg)

    def adjust_attitude(self, amount):
        amount = clamp(amount, -20, 20)
        """Корректируем отношение."""
        self.attitude = clamp(self.attitude + amount, 0, 100)
        print(f"Отношение изменилось на {amount}, новое значение: {self.attitude}")

    def adjust_boredom(self, amount):
        amount = clamp(amount, -20, 20)
        """Корректируем уровень скуки."""
        self.boredom = clamp(self.boredom + amount, 0, 100)
        print(f"Стресс изменился на {amount}, новое значение: {self.boredom}")

    def adjust_stress(self, amount):
        amount = clamp(amount, -20, 20)
        """Корректируем уровень стресса."""
        self.stress = clamp(self.stress + amount, 0, 100)
        print(f"Стресс изменился на {amount}, новое значение: {self.stress}")

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.set_api_key_url()

    def set_api_url(self, api_url):
        self.api_url = api_url
        self.set_api_key_url()

    def set_api_key_url(self):
        if self.api_url != "":
            self.client = OpenAI(api_key=self.api_key,
                                 base_url=self.api_url)
        else:
            self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, user_input):
        # Загрузка истории из файла
        history_data = self.load_history()

        messages = history_data.get('messages', [])
        current_info = history_data.get('currentInfo', {})

        print(
            f"mood: {self.attitude}, secretExposed: {self.secretExposed}, secretExposedFirst: {self.secretExposedFirst}")
        # Первый раз - вводная
        if len(messages) == 0:
            self.MitaMainBehaviour = {
                "role": "system",
                "content": f"{self.main}\n"
            }
            self.MitaExamples = {
                "role": "system",
                "content": f"{self.examplesLong}\n"
            }
            self.systemMessages.insert(0, {"role": "system", "content": f"{self.player}\n"})
            self.systemMessages.insert(0, {"role": "system", "content": f"{self.response_structure}"})


        elif self.attitude < 50 and not (self.secretExposed or self.PlayingFirst):
            print("Играет с игроком в якобы невиновную")
            self.PlayingFirst = True

            self.MitaMainBehaviour = {
                "role": "system",
                "content": f"{self.mainPlaying}\n"
            }


        # Если секрет раскрыт
        elif (self.attitude <= 10 or self.secretExposed) and not self.secretExposedFirst:
            print("Перестала играть вообще")
            self.secretExposedFirst = True
            self.MitaMainBehaviour = {
                "role": "system",
                "content": f"{self.mainCrazy}\n"
                           f"{self.response_structure}"
            }
            self.MitaExamples = {
                "role": "system",
                "content": f"{self.examplesLongCrazy}\n"
            }
            system_message = {
                "role": "system",
                "content": f"{self.SecretExposed}"

            }
            messages.append(system_message)
            system_message = {
                "role": "system",
                "content": f"{self.mita_history}\n"
            }
            self.systemMessages.append(system_message)

        # Текущее настроение (обновление)
        timed_system_message = {
            "role": "system",
            "content": (f"Твои характеристики. {self.variableEffects}"
                        f"Отношение: {self.attitude}/100."
                        f"Стресс: {self.stress}/100."
                        f"Скука: {self.boredom}/100."
                        f"Состояние секрета: {self.secretExposed}"
                        f"{self.common}"
                        )
        }

        # Речь игрока
        date_now = datetime.datetime.now()
        messages.append({"role": "system", "content": f"Текущее время: {date_now}."})
        messages.append({"role": "user", "content": user_input})


        # Ограничение на сообщения
        messages = messages[-self.memory_limit:]

        # Обновляем текущую информацию
        current_info.update({
            'MitaMainBehaviour': self.MitaMainBehaviour,
            'MitaExamples': self.MitaExamples,
            'timed_system_message': timed_system_message
        })
        current_info['MitaSystemMessages'] = self.systemMessages

        combined_messages = []

        # Добавляем systemMessages, если они не пустые
        if self.systemMessages:
            combined_messages.extend(self.systemMessages)

        # Добавляем MitaExamples, если это словарь
        if isinstance(self.MitaExamples, dict):
            combined_messages.append(self.MitaExamples)

        # Добавляем MitaMainBehaviour, если это словарь
        if isinstance(self.MitaMainBehaviour, dict):
            combined_messages.append(self.MitaMainBehaviour)

        # Добавляем timed_system_message, если это словарь
        if isinstance(timed_system_message, dict):
            combined_messages.append(timed_system_message)

        # Добавляем messages, если они не пустые
        if messages:
            combined_messages.extend(messages)

        for idx, msg in enumerate(combined_messages):
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                print(f"Ошибка в формате сообщения {idx}: {msg}")

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=combined_messages,
                max_tokens=self.max_response_tokens,
                presence_penalty=1.5,
                temperature=0.6,
            )
            response = completion.choices[0].message.content

            # Добавляем ответ в правильном формате
            messages.append({"role": "assistant", "content": response})
            # Сохраняем историю в файл
            self.save_history({
                'messages': messages,
                'currentInfo': current_info
            })
            # Процессинг ответа: изменяем показатели и удаляем служебное сообщение
            response = self.process_response(user_input, response,messages)

            return response
        except Exception as e:
            print(f"Ошибка на фазе генерации: {e}")
            return f"Ошибка на фазе генерации: {e}"


    def process_response(self, user_input, response,messages):

        try:
            # Обрабатываем изменение состояния Секрета
            response = self.detect_secret_exposure(response)

            # Обрабатывает ответ, изменяет показатели на основе скрытой строки формата <p>x,x,x,x<p>.
            response = self.process_behavior_changes(response)

            #Выполняет команды
            response = self.process_commands(response,messages)

            # Возвращаем обработанный ответ для дальнейшей работы
            return response.strip()

        except Exception as e:
            print(f"Ошибка в обработке ответа: {e}")
            return response  # Возвращаем оригинальный ответ в случае ошибки

    def process_behavior_changes(self, response):
        """
        Обрабатывает изменения переменных на основе строки формата <p>x,x,x,x<p>.
        """
        start_tag = "<p>"
        end_tag = "</p>"

        if start_tag in response and end_tag in response:
            # Извлекаем изменения переменных
            start_index = response.index(start_tag) + len(start_tag)
            end_index = response.index(end_tag, start_index)
            changes_str = response[start_index:end_index]

            # Разделяем строку на отдельные значения
            changes = [float(x.strip()) for x in changes_str.split(",")]

            if len(changes) == 3:
                # Применяем изменения к переменным
                self.adjust_attitude(changes[0])
                self.adjust_boredom(changes[1])
                self.adjust_stress(changes[2])

            # Убираем строку с <p>...<p> из ответа
            if self.HideAiData:
                response = response[:response.index(start_tag)] + response[end_index + len(end_tag):]

        return response

    def detect_secret_exposure(self, response):
        """
        Проверяем, содержит ли ответ маркер <Secret!>, и удаляем его.
        """
        if "<Secret!>" in response and not self.secretExposedFirst:
            self.secretExposed = True
            print(f"Секрет раскрыт")
            self.attitude = 15
            self.boredom = 20
            if self.HideAiData:
                response = response.replace("<Secret!>", "")
            return response
        return response

    def process_commands(self, response,messages):
        """
        Обрабатывает команды типа <c>...</c> в ответе.
        Команды могут быть: "Достать бензопилу", "Выключить игрока" и другие.
        """

        start_tag = "<c>"
        end_tag = "</c>"

        while start_tag in response and end_tag in response:
            # Извлекаем команду
            start_index = response.index(start_tag) + len(start_tag)
            end_index = response.index(end_tag, start_index)
            command = response[start_index:end_index]

            # Обработка команды в зависимости от условий
            if command == "Достать бензопилу":
                self.add_temporary_system_message(messages,"Игрок был распилен, но скоро он вернется...")
                os._exit(0)  # Принудительное завершение

            elif command == "Выключить игрока":
                self.add_temporary_system_message(messages, "Игрок был выключен, но скоро он вернется...")
                os._exit(0)  # Принудительное завершение

            # Можете добавить другие команды с аналогичной логикой

        return response

    def add_temporary_system_message(self, messages, content):
        """
        Добавляет одноразовое системное сообщение в список сообщений.

        :param messages: Список сообщений, в который добавляется системное сообщение.
        :param content: Текст системного сообщения.
        """
        system_message = {
            "role": "system",
            "content": content
        }
        messages.append(system_message)
    def load_history(self):
        """Загружаем историю из файла, создаем пустую структуру, если файл пуст или не существует."""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Проверяем, что 'messages' и 'currentInfo' присутствуют, и 'messages' является списком
                if isinstance(data.get('messages'), list) and isinstance(data.get('currentInfo'), dict):
                    return data
                else:
                    return {'messages': [], 'currentInfo': {}, 'MitaSystemMessages': []}
        except (json.JSONDecodeError, FileNotFoundError):
            # Если файл пуст или не существует, возвращаем структуру по умолчанию
            return {'messages': [], 'currentInfo': {}, 'MitaSystemMessages': []}

    def save_history(self, data):
        """Сохраняем историю в файл с явной кодировкой utf-8."""
        # Убедимся, что структура данных включает 'messages', 'currentInfo' и 'MitaSystemMessages'
        history_data = {
            'messages': data.get('messages', []),
            'currentInfo': data.get('currentInfo', {}),
            'MitaSystemMessages': data.get('MitaSystemMessages', [])
        }

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)

    def clear_history(self):
        """Очищаем историю чатов."""
        # Сохраняем пустые значения для сообщений и текущей информации
        self.save_history({
            'messages': [],
            'currentInfo': {}  # Очистка информации о текущем состоянии игры
        })


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def print_ip_and_country():
    try:
        # Обращаемся к API для получения информации о текущем IP
        response = requests.get("https://ipinfo.io/json")
        data = response.json()

        ip = data.get("ip", "Не удалось определить IP")
        country = data.get("country", "Не удалось определить страну")

        # Выводим IP и страну в консоль
        print(f"Ваш IP: {ip}")
        print(f"Ваша страна: {country}")
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")


def get_resource_path(filename):
    """
    Функция для получения пути к файлу, учитывая работу как в исходной среде, так и в собранном виде.
    В случае, если приложение собрано в один файл, программа ищет папку Promts рядом с исполнимым файлом.
    """
    if getattr(sys, 'frozen', False):
        # Если программа запущена как исполнимый файл (например, PyInstaller)
        base_path = os.path.dirname(sys.executable)
    else:
        # Если программа запускается в обычной среде (например, в PyCharm)
        base_path = os.path.dirname(__file__)

    # Путь к папке Promts рядом с исполнимым файлом
    promts_path = os.path.join(base_path, 'Promts')

    # Если папка Promts существует, возвращаем путь к файлу в ней
    if os.path.isdir(promts_path):
        return os.path.join(promts_path, filename)

    # Если папка Promts не найдена, генерируем ошибку или другое поведение
    print(f"Ошибка: Папка 'Promts' не найдена рядом с исполнимым файлом.")
    return None


def load_text_from_file(filename):
    """
    Функция для чтения текста из файла.
    """
    try:
        with open(get_resource_path(filename), 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return ""
