import json

import requests
import tiktoken
from openai import OpenAI

class ChatModel:
    def __init__(self):
        self.client = OpenAI(api_key="sk-C85aZs33Lcl3PjjoW3ZpD50SHQvDMT6l",base_url="https://api.proxyapi.ru/openai/v1")
        #self.client = OpenAI(api_key="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")
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        self.max_input_tokens = 2048
        self.max_response_tokens = 500
        self.cost_input_per_1000 = 0.0432
        self.cost_response_per_1000 = 0.1728
        self.history_file = "chat_history.json"
        self.memory_limit = 30  # Ограничение сообщения
        self.mood = 50
        self.stress = 15
        self.cognitive_load = 15
        self.madness = 15
        self.secretExposed = False

        # Загрузка данных из JSON-файлов
        self.main = self.load_text_from_file("Promts/main.txt")
        self.examplesLong = self.load_text_from_file("Promts/examples.txt")
        self.examplesShort = self.load_text_from_file("Promts/examples2.txt")
        self.world = self.load_text_from_file("Promts/world.txt")
        self.mita_history = self.load_text_from_file("Promts/mita_history.txt")
        self.response_structure = self.load_text_from_file("Promts/response_structure.txt")

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
        """Корректируем настроение."""
        self.mood = max(0, min(100, self.mood + amount))
        print(f"Отношение изменилось на {amount}, новое значение: {self.mood}")

    def adjust_stress(self, amount):
        """Корректируем уровень стресса."""
        self.stress = max(0, min(100, self.stress + amount))
        print(f"Стресс изменился на {amount}, новое значение: {self.stress}")

    def adjust_cognitive_load(self, amount):
        """Корректируем когнитивную нагрузку."""
        self.cognitive_load = max(0, min(100, self.cognitive_load + amount))
        print(f"Когнитивная нагрузка изменена на {amount}, новое значение: {self.cognitive_load}")

    def adjust_madness(self, amount):
        """Корректируем уровень безумия."""
        self.madness = max(0, min(100, self.madness + amount))
        print(f"Безумие изменилось на {amount}, новое значение: {self.madness}")

    def generate_response(self, user_input):
        messages = self.load_history()

        if len(messages) == 0:
            # Система — начальное сообщение с настроением и текущими значениями
            system_message = {
                "role": "system",
                "content": (
                    f"{self.main}\n"
                    f"Настроение: {self.mood}/100. Выражает твое отношение к игроку. При уровне 0 ты его ненавидишь всем сердцем."
                    f"Стресс: {self.stress}/100. Чем выше, тем отчаяннее ты говоришь и действуешь"
                    f"Когнитивная нагрузка: {self.cognitive_load}/100. Чем выше, тем меньше логики в твоих словах"
                    f"Безумие: {self.madness}/100.\n чем выше, тем ты более непредсказуема и чаще меняешь тему"
                    f"Состояние секрета: {self.secretExposed} Если он не раскрыт, ты сама невинность, иначе твое стандартное злое поведение\n"
                    #f"{self.examplesShort}\n"
                    f"{self.examplesLong}\n"
                    #f"{self.world}\n"
                    f"{self.mita_history}\n"
                    f"{self.response_structure}"
                )
            }
            messages.insert(0, system_message)


        messages.append({"role": "user", "content": user_input})

        # Ограничение на 5 сообщений
        #messages = messages[-self.memory_limit:]

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=self.max_response_tokens
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
            changes = [int(x.strip()) for x in changes_str.split(",")]

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
        if "<Secret!>" in response or self.mood <= 10:
            self.secretExposed = True
            print(f"Секрет раскрыт")
            self.mood-=40
            self.madness+=30
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
