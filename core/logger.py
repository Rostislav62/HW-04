# /core/logger.py

import logging
import os

# 📌 Создаём папку `logs`, если её нет
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 📌 Настраиваем логирование в файл `logs/api.log`
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "api.log"),  # Файл логов
    level=logging.INFO,  # Логируем все INFO-события и выше (INFO, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Формат логов
)

# 📌 Добавляем StreamHandler (чтобы логи отображались и в терминале)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Логируем INFO и выше
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# 📌 Создаём объект логгера
logger = logging.getLogger(__name__)
logger.addHandler(console_handler)  # Добавляем обработчик для вывода в консоль
