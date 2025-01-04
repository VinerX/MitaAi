import json
import tiktoken
import random
from openai import OpenAI



class ChatModel:
    def __init__(self):
        self.client = OpenAI(api_key="sk-C85aZs33Lcl3PjjoW3ZpD50SHQvDMT6l", base_url="https://api.proxyapi.ru/openai/v1")
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        self.max_input_tokens = 2048
        self.max_response_tokens = 500
        self.cost_input_per_1000 = 0.0432
        self.cost_response_per_1000 = 0.1728
        self.history_file = "chat_history.json"
        self.mood = 35
        self.stress = 25
        self.cognitive_load = 25
        self.madness = 5

    def calculate_cost(self, user_input):
        messages = self.load_history()
        messages.append({"role": "user", "content": user_input})
        token_count = self.count_tokens(messages)
        cost = (token_count / 1000) * self.cost_input_per_1000
        return token_count, cost

    def count_tokens(self, messages):
        return sum(len(self.tokenizer.encode(msg["content"])) for msg in messages)

    def adjust_mood(self, amount):
        self.mood = max(0, min(100, self.mood + amount))

    def adjust_stress(self, amount):
        self.stress = max(0, min(100, self.stress + amount))

    def adjust_cognitive_load(self, amount):
        self.cognitive_load = max(0, min(100, self.cognitive_load + amount))

    def adjust_madness(self, amount):
        self.madness = max(0, min(100, self.madness + amount))

    def generate_response(self, user_input):
        messages = self.load_history()
        attitude = self.get_attitude()
        system_message = {
            "role": "system",
            "content": f"Ты Мита. Настроение: {self.mood}/100. Стресс: {self.stress}/100. Безумие: {self.madness}/100. Ты {attitude}."
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
            self.process_response(user_input, response)
            self.save_history(messages + [{"role": "assistant", "content": response}])
            return response
        except Exception as e:
            return f"Ошибка: {e}"

    def process_response(self, user_input, response):
        # В зависимости от содержания сообщения, увеличиваем стресс или безумие
        if "сложно" in user_input or "трудно" in user_input:
            self.adjust_stress(10)
        if "сумасшедший" in response:
            self.adjust_madness(5)

    def get_attitude(self):
        if self.madness > 90:
            return "совсем безумна и непредсказуема"
        elif self.madness > 50:
            return "стала агрессивной и странной"
        elif self.stress > 50:
            return "грубит и раздражается на всё вокруг"
        elif self.cognitive_load > 50:
            return "с трудом отвечает, запутываясь в словах"
        else:
            return "нормально реагирует на происходящее"

    def save_history(self, messages):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def clear_history(self):
        self.save_history([])  # Сохраняем пустую историю