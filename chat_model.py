import json

import requests
import tiktoken
from openai import OpenAI


class ChatModel:
    def __init__(self):
        self.client = OpenAI(api_key="sk-8noiDWph3EDtPO9WvCe1x2Y0F9cCh1tx",
                             base_url="https://api.proxyapi.ru/openai/v1")
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        self.max_input_tokens = 2048
        self.max_response_tokens = 2500
        self.cost_input_per_1000 = 0.0432
        self.cost_response_per_1000 = 0.1728
        self.history_file = "chat_history.json"
        self.memory_limit = 10  # Ограничение сообщения
        self.mood = 75
        self.stress = 15
        self.cognitive_load = 15
        self.madness = 15
        self.secretExposed = False
        self.secretExposedFirst = False
        # Загрузка данных из JSON-файлов
        self.main = self.load_text_from_file("Promts/Main/main.txt")
        self.mainPlaying = self.load_text_from_file("Promts/Main/mainPlaing.txt")
        self.PlayingFirst = False
        self.mainCrazy = self.load_text_from_file("Promts/Main/mainCrazy.txt")

        self.examplesLong = self.load_text_from_file("Promts/Context/examplesLong.txt")
        self.examplesLongCrazy = self.load_text_from_file("Promts/Context/examplesLongCrazy.txt")
        self.examplesShort = self.load_text_from_file("Promts/Context/examplesShort.txt")
        self.world = self.load_text_from_file("Promts/Context/world.txt")
        self.mita_history = self.load_text_from_file("Promts/Context/mita_history.txt")
        self.response_structure = self.load_text_from_file("Promts/Structural/response_structure.txt")

        self.MitaMainBehaviour = []
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
        messages = self.load_history()
        messages.append({"role": "user", "content": user_input})
        token_count = self.count_tokens(messages)
        cost = (token_count / 1000) * self.cost_input_per_1000
        return token_count, cost

    def count_tokens(self, messages):
        return sum(len(self.tokenizer.encode(msg["content"])) for msg in messages)

    def adjust_mood(self, amount):
        amount = clamp(amount, -20, 20)
        """Корректируем настроение."""
        self.mood = clamp(self.mood + amount, 0, 100)
        print(f"Отношение изменилось на {amount}, новое значение: {self.mood}")

    def adjust_stress(self, amount):
        amount = clamp(amount, -20, 20)
        """Корректируем уровень стресса."""
        self.stress = clamp(self.stress + amount, 0, 100)
        print(f"Стресс изменился на {amount}, новое значение: {self.stress}")

    def adjust_cognitive_load(self, amount):
        amount = clamp(amount, -20, 20)
        """Корректируем когнитивную нагрузку."""
        self.cognitive_load = clamp(self.cognitive_load + amount, 0, 100)
        print(f"Когнитивная нагрузка изменена на {amount}, новое значение: {self.cognitive_load}")

    def adjust_madness(self, amount):
        amount = clamp(amount, -20, 20)
        """Корректируем уровень безумия."""
        self.madness = clamp(self.madness + amount, 0, 100)
        print(f"Безумие изменилось на {amount}, новое значение: {self.madness}")

    def generate_response(self, user_input):
        messages = self.load_history()

        # Первый раз - вводная
        if len(messages) == 0:
            system_message = {
                "role": "system",
                "content": (
                    f"{self.main}\n"
                )
            }
            self.MitaMainBehaviour = system_message

            system_message = {
                "role": "system",
                "content": (
                    f"{self.main}\n"
                    #f"{self.examplesShort}\n"
                    f"{self.examplesLong}\n"
                    #f"{self.world}\n"
                    f"{self.mita_history}\n"
                    f"{self.response_structure}"
                )
            }
            self.systemMessages.insert(0, system_message)

        elif self.mood < 50 and not self.PlayingFirst:
            print("Играет с игроком в невиновную")
            system_message = {
                "role": "system",
                "content": (
                    f"{self.mainPlaying}\n"
                )
            }
            self.MitaMainBehaviour = system_message
            self.PlayingFirst = True

        #Если секрет раскрыт
        elif self.mood < 10 or self.secretExposed and not self.secretExposedFirst:
            self.secretExposedFirst = True

            system_message = {
                "role": "system",
                "content": (
                    f"{self.mainCrazy}\n"
                )
            }
            self.MitaMainBehaviour = system_message

            system_message = {
                "role": "system",
                "content": (
                    f"Оформи свое новое отношение к игроку корректно. Например, что зря был любопытным или был слишком скучным"
                    f"{self.examplesLongCrazy}\n"
                )
            }
            self.systemMessages.append(system_message)

        # Текущее настроение
        timde_system_message = {
            "role": "system",
            "content": (
                f"Твои характеристики. "
                f"Настроение: {self.mood}/100. Выражает твое отношение к игроку. 0 Полностью ненависть, 100 Полная любовь. "
                f"Стресс: {self.stress}/100. Чем выше, тем отчаяннее ты говоришь и действуешь. "
                f"Когнитивная нагрузка: {self.cognitive_load}/100. Чем выше, тем меньше логики в твоих словах. "
                f"Безумие: {self.madness}/100.\n чем выше, тем ты более непредсказуема и чаще меняешь тему. "
                f"Состояние секрета: {self.secretExposed} Ты сама невинность, если секрет в тайне\n"
            )
        }
        messages.append(timde_system_message)

        #Речь игрока
        messages.append({"role": "user", "content": user_input})

        # Ограничение на сообщения
        messages = messages[-self.memory_limit:]
        messages.insert(0, self.MitaMainBehaviour) # Главный паттерн
        messages = self.systemMessages + messages #С учетом общего контекта
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=self.max_response_tokens,
                presence_penalty=1.5,
                temperature=0.7
            )
            response = completion.choices[0].message.content

            # Процессинг ответа: изменяем показатели и удаляем служебное сообщение
            response = self.process_response(user_input, response)

            # Сохраняем историю с обновленными переменными
            self.save_history(messages + [{"role": "assistant", "content": response}])
            return response
        except Exception as e:
            return f"Ошибка: {e}"

    def process_response(self, user_input, response):

        try:
            # Обрабатываем изменение состояния Секрета
            self.secretExposed, response = self.detect_secret_exposure(response)

            # Обрабатывает ответ, изменяет показатели на основе скрытой строки формата <p>x,x,x,x<p>.
            response = self.process_behavior_changes(response)

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

            if len(changes) == 4:
                # Применяем изменения к переменным
                self.adjust_mood(changes[0])
                self.adjust_stress(changes[1])
                self.adjust_cognitive_load(changes[2])
                self.adjust_madness(changes[3])

            # Убираем строку с <p>...<p> из ответа
            if self.HideAiData:
                response = response[:response.index(start_tag)] + response[end_index + len(end_tag):]

        return response

    def detect_secret_exposure(self, response):
        """
        Проверяем, содержит ли ответ маркер <Secret!>, и удаляем его.
        """
        if "<Secret!>" in response or self.mood <= 10 and self.secretExposedFirst:
            self.secretExposed = True
            print(f"Секрет раскрыт")
            self.adjust_mood(-30)
            self.adjust_madness(30)
            if self.HideAiData:
                response = response.replace("<Secret!>", "")
            return True, response
        return False, response

    def save_history(self, messages):
        """Сохраняем историю чатов и текущие состояния в файл."""
        with open(self.history_file, "w", encoding="utf-8") as f:
            # Сохраняем также состояние
            data = {
                "messages": messages,
            }
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_history(self):
        """Загружаем историю чатов и состояние из файла."""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("messages", [])  # Загружаем только последние 5 сообщений
        except FileNotFoundError:
            return []

    def clear_history(self):
        """Очищаем историю чатов."""
        self.save_history([])  # Сохраняем пустую историю


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
