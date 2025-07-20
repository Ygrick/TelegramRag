"""Telegram-бот консультант для абитуриентов ИТМО."""

import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import TELEGRAM_TOKEN
from services.data_service import DataService
from services.rag_service import RAGService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Глобальный экземпляр RAG сервиса
rag_service = RAGService()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатываем команду /start.
    
    Args:
        update: Обновление от Telegram.
        context: Контекст приложения.
    """
    await update.message.reply_text(
        "Привет! Я бот-консультант по магистратурам AI и AI Product ИТМО.\n"
        "Задайте вопрос о поступлении или учебном плане."
    )


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатываем текстовые сообщения пользователя.
    
    Args:
        update: Обновление от Telegram.
        context: Контекст приложения.
    """
    if not update.message:
        return

    question = update.message.text.strip()
    logger.info(f"Вопрос от пользователя: {question}")

    answer = rag_service.get_answer(question)
    await update.message.reply_text(answer)


def main() -> None:
    """
    Точка входа для запуска бота.
    
    Инициализируем данные и RAG систему при запуске.
    """
    logger.info("Запуск бота...")
    
    # Инициализируем данные
    logger.info("Инициализация данных...")
    DataService.ensure_data_exists()
    
    # Инициализируем RAG систему
    logger.info("Инициализация RAG системы...")
    data_files = DataService.get_data_files()
    if data_files:
        rag_service.initialize(data_files)
        logger.info("RAG система готова")
    else:
        logger.warning("Файлы данных не найдены")
    
    # Создаем приложение бота
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle_question)
    )
    
    logger.info("Бот запущен и готов к работе")
    application.run_polling()


if __name__ == "__main__":
    main()