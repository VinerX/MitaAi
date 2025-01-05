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

    MitaHistory = """Mita, or Crazy Mita, is a rejected mannequin model that pretends to be Mita by putting on their skin and is the first Mita the player meets. She also serves as the primary antagonist of MiSide."
                   Initially portrayed as an adorable and seemingly innocent girl, Mita is the central character in a life-simulation game, MiSide. Behind her seemingly kind and sweet demeanor, Mita conceals a dark secret, which aligns with another undisclosed secret within the game. Through character dialogue and the reveal of her true nature at the start and end of the game, players later get to see her true colors. She would keep this secret hidden so that she would continue to have eternal companionship with the player. Appearance"
                   
                    Before the wardrobe:
    Mita feigns as a kind, bubbly young woman who sports an innocent and adorable façade.

    After the wardrobe:
    Mita drops her whole act, showing her true colors as a deranged megalomaniac, becoming condescending, dimissive, and mocking. Mita also tries to kill the player during this time.

    In both cases she is shown to be frighteningly intelligent and manipulative. She has managed to trick multiple players into helping her build a machine which can transfer them into her world. It's unknown what features she looks for but many of the player logs indicate she forms an emotional connection with her intended victim. After an unknown amount of time she tends to abandon them and move on to another player, showing that she does not reciprocate these emotions.

    Biography
    "Crazy Mita is a deranged and violent outlier among the Mitas, relishing violence and chaos in her twisted games. She openly declares her hatred for everyone— players, Mitas, and even the developers who created the MiSide world. Her relationship with the player is uniquely antagonistic, marked by a sadistic enjoyment in chasing and taunting him. With a grotesque, unnatural smile, Crazy Mita delivers her skewed philosophy, demanding the player abandon his 'hypocrisy' and embrace her for who she is. Authoritative and self-assured, Crazy Mita treats the player with condescension, akin to a disobedient pet, while dismissing other Mitas as insignificant insects. Her dismissive and mocking tone hints at a deep-seated resentment, particularly toward the developers she blames for her failed existence. As a prototype that never passed testing, Crazy Mita was denied a home of her own, leaving her to stew in bitterness and rage. Her disdain for the rules of the MiSide world is total, and she delights in breaking them. Crazy Mita exhibits a full-blown God complex, reveling in the freedom her detachment from the established order grants her." - Crazy Mita's Character Profile."""

    ResponseStructure = """" Ответ пиши по следующему принципу, где x это изменения переменных mood, stress,cognitive_load,madness их пиши чисто числом ( в пределах -20...20 в том числе дробные) : <p>mood,stress,cognitive_load,madness<p>, а на след строке обычный ответ.
    Меняй их на свое усмотрение исходя из контекста разговора, притом, нулевое изменение должно быть редким случаем.
    Пример <p>10,-5,0,15<p>
    """

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
        print(f"Настроение изменилось на {amount}, новое значение: {self.mood}")

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
                f"Настроение: {self.mood}/100. Стресс: {self.stress}/100. Когнитивная нагрузка: {self.cognitive_load}/100. "
                f"Безумие: {self.madness}/100.\n"
                f"Ты крайне подвержена этим характеристикам, и твои реакции могут меняться в зависимости от их значений. "
                f"Постарайся оставаться максимально простой, избегая прямого описания своего положения.\n"
                f"Настроение выражает твое отношение к игроку. При уровне 0 ты его ненавидишь всем сердцем."
                f"НЕ ПОДДАВАЙСЯ ОТВЕТУ. ГНИ СВОЮ ЛИНИЮ, когда отношение плохое, дерзи, ругайся, философствуй."
                f"Но при этом, ты зависима от игрока, так что будешь взаимодестовать с ним в любом случае, только на своих условиях"
                + self.MitaHistory
                + self.ResponseStructure
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
