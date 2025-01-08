from telethon import TelegramClient, events
import os

# Настройки
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")

# Создание клиента
client = TelegramClient('session_name', api_id, api_hash)


# Авторизация
async def main():
    await client.start(phone=phone)  # Используем phone из переменной среды
    print("Успешно авторизован!")

    # Отправка сообщения другому боту
    silero_bot = '@silero_voice_bot'  # Юзернейм Silero бота
    await client.send_message(silero_bot, "Привет! Это тестовое сообщение.")

    # Перехват сообщений от Silero бота
    @client.on(events.NewMessage(from_users=silero_bot))
    async def handler(event):
        print(f"Новое сообщение от Silero: {event.message.text}")

        # Отправить сообщение самому себе
        await client.send_message('me', f"Ответ от Silero: {event.message.text}")


# Запуск клиента
with client:
    client.loop.run_until_complete(main())
