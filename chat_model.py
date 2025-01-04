### chat_model.py

import json
import tiktoken
from openai import OpenAI

class ChatModel:
    def __init__(self):
        self.client = OpenAI(api_key="sk-your-key", base_url="https://api.proxyapi.ru/openai/v1")
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        self.max_input_tokens = 2048
        self.max_response_tokens = 500
        self.cost_input_per_1000 = 0.0432
        self.cost_response_per_1000 = 0.1728
        self.history_file = "chat_history.json"
        self.mood = 35

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

    def generate_response(self, user_input):
        messages = self.load_history()
        attitude = self.get_attitude()
        system_message = {
            "role": "system",
            "content": f"Ты Мита. Настроение: {self.mood}/100. Ты {attitude}."
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
            self.save_history(messages + [{"role": "assistant", "content": response}])
            return response
        except Exception as e:
            return f"Ошибка: {e}"

    def get_attitude(self):
        if self.mood <= 10:
            return "грубит и раздражается на всё вокруг"
        elif self.mood <= 20:
            return "замкнута и отвечает односложно, с раздражением"
        elif self.mood <= 30:
            return "едко саркастична и слегка раздражительна"
        elif self.mood <= 40:
            return "не слишком приветлива, но держится корректно"
        elif self.mood <= 50:
            return "равнодушна, но готова выслушать"
        elif self.mood <= 60:
            return "немного отстранённая, но старается быть приятной"
        elif self.mood <= 70:
            return "дружелюбна, но с лёгким сарказмом"
        elif self.mood <= 80:
            return "добродушна и приветлива"
        elif self.mood <= 90:
            return "искренне заботлива и приветлива"
        else:
            return "излучает радость и энтузиазм, готова помочь во всём"

    def save_history(self, messages):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
