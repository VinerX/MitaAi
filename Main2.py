import os
import logging
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Флаг для использования видеокарты (GPU)
ИспользоватьВидеокарту = True  # Установите False, если хотите использовать только CPU

# Проверка доступности GPU
device = torch.device("cuda" if torch.cuda.is_available() and ИспользоватьВидеокарту else "cpu")

# Указание директории для хранения модели
model_directory = './local_model'

# Проверка, существует ли уже модель в локальной папке
logger.info(f"Проверка наличия модели в директории: {model_directory}")
if not os.path.exists(model_directory):
    os.makedirs(model_directory)
    logger.info(f"Директория {model_directory} была создана.")

# Загрузка модели и токенизатора
logger.info("Загрузка модели и токенизатора...")
model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=model_directory)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=model_directory)

# Установка pad_token_id, если необходимо
tokenizer.pad_token = tokenizer.eos_token
logger.info("Модель и токенизатор загружены успешно.")

# Перемещение модели на нужное устройство (CPU или GPU)
model = model.to(device)
logger.info(f"Модель перемещена на устройство: {device}")

while True:
    # Ввод текста с консоли
    input_text = input("Введите текст для генерации (или '0' для выхода): ")

    # Проверка на выход
    if input_text == '0':
        logger.info("Выход из программы...")
        break

    logger.info(f"Текст для генерации: {input_text}")

    # Токенизация ввода
    logger.info("Токенизация текста...")
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    logger.info(f"Токенизация завершена. Входные данные: {inputs['input_ids']}")

    # Перемещение входных данных на нужное устройство (CPU или GPU)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    # Генерация текста с улучшенными параметрами для быстрого ответа
    logger.info("Начало генерации текста...")
    output = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=100,          # Ограничиваем длину текста для быстрого ответа
        temperature=0.95,         # Контролируем случайность
        top_k=40,                # Ограничиваем выбор токенов
        top_p=0.95,              # Ограничиваем вероятность выбора токенов
        do_sample=True,          # Включаем сэмплинг для улучшения разнообразия
        no_repeat_ngram_size=2,  # Убираем повторения фраз
        pad_token_id=tokenizer.pad_token_id
    )
    logger.info("Генерация завершена.")

    # Декодирование и вывод результата
    output_text = tokenizer.decode(output[0], skip_special_tokens=True)
    logger.info(f"Результат генерации: {output_text}")

    print(f"Сгенерированный текст: {output_text}")
