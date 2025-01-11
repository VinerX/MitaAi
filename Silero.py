from telethon import TelegramClient, events
import os
import time
import random
import pygame
import asyncio
from telethon.tl.types import MessageMediaDocument
from pydub import AudioSegment

import audioread
import soundfile as sf
import ffmpeg


# Пример использования:
class TelegramBotHandler:
    def __init__(self, gui, message_limit_per_minute=3):
        api_id = int(os.getenv("TELEGRAM_API_ID"))
        api_hash = os.getenv("TELEGRAM_API_HASH")
        phone = os.getenv("TELEGRAM_PHONE")
        silero_bot = '@silero_voice_bot'  # Юзернейм Silero бота

        self.gui = gui
        self.patch_to_sound_file = ""

        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.silero_bot = silero_bot
        self.message_limit_per_minute = message_limit_per_minute
        self.message_count = 0
        self.start_time = time.time()
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)

        # Сделаем метод экземплярным и добавим await

    async def convert_mp3_to_wav(self, input_path, output_path):
        """Конвертирует MP3 в WAV с использованием ffmpeg."""
        try:
            if not os.path.exists(input_path):
                print(f"Файл {input_path} не найден.")
                return

            # Указываем путь к ffmpeg
            ffmpeg_path = r"E:\Games\OpenAI_API_TEST\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"

            print(f"Начинаю конвертацию {input_path} в {output_path} с помощью {ffmpeg_path}")

            # Выполняем команду конвертации
            ffmpeg.input(input_path).output(output_path).run(cmd=ffmpeg_path)

            print(f"Конвертация завершена: {output_path}")
        except Exception as e:
            print(f"Ошибка при конвертации: {e}")

    def reset_message_count(self):
        """Сбрасывает счетчик сообщений каждую минуту."""
        if time.time() - self.start_time > 60:
            self.message_count = 0
            self.start_time = time.time()

    async def play_mp3(self, file_path):
        """Проигрывает MP3 файл."""

        def play():
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():  # Ожидаем завершения воспроизведения
                pygame.time.Clock().tick(10)

        # Выполняем блокирующую функцию в отдельном потоке
        await asyncio.to_thread(play)

    async def handle_voice_file(self, file_path):
        """Проигрывает звуковой файл."""
        try:
            print(f"Проигрываю файл: {file_path}")
            await self.play_mp3(file_path)
        except Exception as e:
            print(f"Ошибка при воспроизведении файла: {e}")

    async def send_and_receive(self, input_message):
        """Отправляет сообщение боту и обрабатывает ответ."""
        bot_entity = await self.client.get_entity(self.silero_bot)  # Получаем объект бота
        bot_id = bot_entity.id  # ID бота
        global message_count

        self.reset_message_count()

        if self.message_count >= self.message_limit_per_minute:
            print("Превышен лимит сообщений. Ожидаем...")
            await asyncio.sleep(random.uniform(10, 15))
            return

        # Отправка сообщения боту
        await self.client.send_message(self.silero_bot, input_message)
        self.message_count += 1

        # Ожидание ответа от бота
        print("Ожидание ответа от бота...")
        response = None
        attempts = 0
        await asyncio.sleep(0.7)
        while attempts < 3:  # Попытки получения ответа

            async for message in self.client.iter_messages(self.silero_bot, limit=1):
                if message.media and isinstance(message.media, MessageMediaDocument):
                    # Проверяем тип файла и его атрибуты
                    if 'audio/mpeg' in message.media.document.mime_type:
                        response = message
                        break
            if response:  # Если ответ найден, выходим из цикла
                break
            print(f"Попытка {attempts + 1}/3. Ответ от бота не найден.")
            attempts += 1
            await asyncio.sleep(1)  # Немного подождем

        if not response:
            print("Ответ от бота не получен после 3 попыток.")
            return

        # Обработка полученного сообщения
        if response.media and isinstance(response.media, MessageMediaDocument):
            if 'audio/mpeg' in response.media.document.mime_type:  # Проверка MP3 файла
                file_path = await self.client.download_media(response.media)

                print(f"Файл загружен: {file_path}")
                # Генерируем путь для WAV-файла на основе имени исходного MP3
                base_name = os.path.splitext(os.path.basename(file_path))[0]  # Получаем имя файла без расширения
                wav_path = os.path.join(os.path.dirname(file_path), f"{base_name}.wav")  # Создаем новый путь

                # Получаем абсолютный путь
                absolute_wav_path = os.path.abspath(wav_path)
                # Конвертируем MP3 в WAV
                await self.convert_mp3_to_wav(file_path, absolute_wav_path)
                self.gui.patch_to_sound_file = absolute_wav_path

                print(f"Файл wav загружен: {absolute_wav_path}")
                #await self.handle_voice_file(file_path)
        elif response.text:  # Если сообщение текстовое
            print(f"Ответ от бота: {response.text}")

    async def start(self):
        print("Запуск коннектора ТГ!")
        try:
            await self.client.start(phone=self.phone)

            print("Успешно авторизован!")
        except Exception as e:
            print(f"Ошибка авторизации: {e}")
