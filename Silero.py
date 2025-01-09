from telethon import TelegramClient, events
import os

import time
import random

from telethon.tl.types import MessageMediaDocument

import pygame
import asyncio

# Настройки
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")
silero_bot = '@silero_voice_bot'  # Юзернейм Silero бота

# Создание клиента
client = TelegramClient('session_name', api_id, api_hash)

# Ограничения
MESSAGE_LIMIT_PER_MINUTE = 3
message_count = 0
start_time = time.time()


def reset_message_count():
    global message_count, start_time
    if time.time() - start_time > 60:
        message_count = 0
        start_time = time.time()

async def play_mp3(file_path):
    """Проигрывает MP3 файл."""
    def play():
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Ожидаем завершения воспроизведения
            pygame.time.Clock().tick(10)

    # Выполняем блокирующую функцию в отдельном потоке
    await asyncio.to_thread(play)

async def handle_voice_file(file_path):
    """Проигрывает звуковой файл."""
    try:
        print(f"Проигрываю файл: {file_path}")
        await play_mp3(file_path)
    except Exception as e:
        print(f"Ошибка при воспроизведении файла: {e}")


async def send_and_receive():
    bot_entity = await client.get_entity(silero_bot)  # Получаем объект бота
    bot_id = bot_entity.id  # ID бота
    """Отправляет сообщение боту и обрабатывает ответ."""
    global message_count

    while True:
        reset_message_count()

        if message_count >= MESSAGE_LIMIT_PER_MINUTE:
            print("Превышен лимит сообщений. Ожидаем...")
            await asyncio.sleep(random.uniform(10, 15))
            continue

        user_input = input("Введите сообщение для бота (или 'exit' для выхода): ")
        if user_input.lower() == 'exit':
            print("Завершение работы.")
            break

        # Отправка сообщения боту
        await client.send_message(silero_bot, user_input)
        message_count += 1

        # Ожидание ответа от бота
        print("Ожидание ответа от бота...")
        response = None
        attempts = 0
        await asyncio.sleep(0.5)
        while attempts < 3:  # Попытки получения ответа
            await asyncio.sleep(1)  # Немного подождем
            async for message in client.iter_messages(silero_bot, limit=5):
                if message.media and isinstance(message.media, MessageMediaDocument):
                    # Проверяем тип файла и его атрибуты
                    if 'audio/mpeg' in message.media.document.mime_type:
                        response = message
                        break
            if response:  # Если ответ найден, выходим из цикла
                break
            print(f"Попытка {attempts + 1}/3. Ответ от бота не найден.")
            attempts += 1

        if not response:
            print("Ответ от бота не получен после 3 попыток.")
            continue

        # Обработка полученного сообщения
        if response.media and isinstance(response.media, MessageMediaDocument):
            if 'audio/mpeg' in response.media.document.mime_type:  # Проверка MP3 файла
                file_path = await client.download_media(response.media)
                print(f"Файл загружен: {file_path}")
                await handle_voice_file(file_path)
        elif response.text:  # Если сообщение текстовое
            print(f"Ответ от бота: {response.text}")



async def main():
    await client.start(phone=phone)

    print("Успешно авторизован!")
    await send_and_receive()


# Запуск клиента
with client:
    client.loop.run_until_complete(main())
