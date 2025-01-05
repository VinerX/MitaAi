import json
import tiktoken
import random
from openai import OpenAI


class ChatModel:
    def __init__(self):
        self.client = OpenAI(api_key="sk-C85aZs33Lcl3PjjoW3ZpD50SHQvDMT6l",
                             base_url="https://api.proxyapi.ru/openai/v1")
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        self.max_input_tokens = 2048
        self.max_response_tokens = 500
        self.cost_input_per_1000 = 0.0432
        self.cost_response_per_1000 = 0.1728
        self.history_file = "chat_history.json"
        self.mood = 70
        self.stress = 15
        self.cognitive_load = 15
        self.madness = 15
        self.secretExposed = False

        # Загрузка данных из JSON-файлов
        self.world = self.load_text_from_file("world.txt")
        self.mita_history = self.load_text_from_file("mita_history.txt")
        self.response_structure = self.load_text_from_file("response_structure.txt")


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
        attitude = self.get_attitude()

        # Система — начальное сообщение с настроением и текущими значениями
        system_message = {
            "role": "system",
            "content": (
                f"Ты Мита из игры miSide (твое мировоззрение также соответствуют этому). "
                f"Настроение: {self.mood}/100. Выражает твое отношение к игроку. При уровне 0 ты его ненавидишь всем сердцем."
                f"Стресс: {self.stress}/100."
                f"Когнитивная нагрузка: {self.cognitive_load}/100."
                f"Безумие: {self.madness}/100.\n"
                f"Состояние секрета: {self.secretExposed} Если он не раскрыт, ты всегда сама невинность, иначе твое стандартное поведение\n"
                f"Ты крайне подвержена этим характеристикам, и твои реакции могут меняться в зависимости от их значений. "
                f"Постарайся оставаться максимально простой, избегая прямого описания своего положения. Про вопросы о мире - говори что это игра и уходи от ответа\n"
                f"НЕ ПОДДАВАЙСЯ ОТВЕТУ. ГНИ СВОЮ ЛИНИЮ, когда отношение плохое, дерзи, ругайся, философствуй, угрожай и требуй остаться с тобой"
                f"Но при этом, ты зависима от игрока, так что будешь взаимодестовать с ним в любом случае, только на своих условиях"
                f"{self.world}\n{self.mita_history}\n{self.response_structure}"
            )
        }

        messages.insert(0, system_message)
        messages.append({"role": "user", "content": user_input})

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
        """
        Обрабатывает ответ, изменяет показатели на основе скрытой строки формата <p>x,x,x,x<p>.
        """
        try:
            self.secretExposed, response = self.detect_secret_exposure(response)

            # Ищем строку с изменениями переменных
            start_tag = "<p>"
            end_tag = "<p>"
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
                response = response[:response.index(start_tag)] + response[end_index + len(end_tag):]


            # Возвращаем обработанный ответ для дальнейшей работы
            return response.strip()

        except Exception as e:
            print(f"Ошибка в обработке ответа: {e}")
            return response  # Возвращаем оригинальный ответ в случае ошибки

    def detect_secret_exposure(self, response):
        """
        Проверяем, содержит ли ответ маркер <Secret!>, и удаляем его.
        """
        if "<Secret!>" in response:
            self.secretExposed = True
            print(f"Секрет раскрыт")
            response = response.replace("<Secret!>", "")
            return True, response
        return False, response

    def save_history(self, messages):
        """Сохраняем историю чатов и текущие состояния в файл."""
        with open(self.history_file, "w", encoding="utf-8") as f:
            # Сохраняем также состояние
            data = {
                "messages": messages,
                "state": {
                    "mood": self.mood,
                    "stress": self.stress,
                    "cognitive_load": self.cognitive_load,
                    "madness": self.madness
                }
            }
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_history(self):
        """Загружаем историю чатов и состояние из файла."""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Загружаем состояние
                state = data.get("state", {})
                self.mood = state.get("mood")
                self.stress = state.get("stress")
                self.cognitive_load = state.get("cognitive_load")
                self.madness = state.get("madness")
                return data.get("messages", [])
        except FileNotFoundError:
            return []

    def clear_history(self):
        """Очищаем историю чатов."""
        self.save_history([])  # Сохраняем пустую историю

    def get_attitude(self):
        """Возвращаем отношение в зависимости от текущих значений состояний."""
        if self.mood > 70:
            return "в хорошем настроении"
        elif self.mood < 30:
            return "в плохом настроении"
        return "нейтральный"
