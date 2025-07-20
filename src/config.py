"""Конфигурация проекта TelegramRag."""

import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

# Токен бота
TELEGRAM_TOKEN: Final[str] = os.getenv("tg_token")

# Пути
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"

# OpenAI API настройки
OPENAI_BASE_URL: Final[str] = os.getenv("APP_GENERATION_BASE_URL")
OPENAI_API_KEY: Final[str] = os.getenv("APP_GENERATION_API_TOKEN")
MODEL_NAME: Final[str] = "qwen/qwen3-32b:free"

# RAG настройки
EMBEDDING_MODEL: Final[str] = "intfloat/multilingual-e5-large"
CHUNK_SIZE: Final[int] = 800
CHUNK_OVERLAP: Final[int] = 80
SIMILARITY_K: Final[int] = 3 