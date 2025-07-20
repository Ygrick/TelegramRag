"""Сервис для работы с данными."""

import json
import logging
from pathlib import Path

from utils.parser import parse_itmo_program, download_curriculum_pdf
from config import DATA_DIR

logger = logging.getLogger(__name__)


class DataService:
    """Сервис для инициализации и управления данными."""
    
    @staticmethod
    def ensure_data_exists() -> None:
        """
        Проверяем наличие данных и парсим при необходимости.
        
        Создаем директорию data, парсим программы ИТМО и скачиваем PDF планы.
        """
        DATA_DIR.mkdir(exist_ok=True)
        
        ai_json_path = DATA_DIR / 'ai.json'
        ai_product_json_path = DATA_DIR / 'ai_product.json'
        
        # Парсим и скачиваем для программы AI
        ai_data = parse_itmo_program('https://abit.itmo.ru/program/master/ai')
        if ai_data:
            with open(ai_json_path, 'w', encoding='utf-8') as f:
                json.dump(ai_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Сохранены данные: {ai_json_path}")
        
        # Скачиваем PDF для программы AI
        download_curriculum_pdf(
            'https://abit.itmo.ru/program/master/ai',
            DATA_DIR,
            'ai_itmo_plan.pdf'
        )
        
        # Парсим и скачиваем для программы AI Product

        ai_product_data = parse_itmo_program('https://abit.itmo.ru/program/master/ai_product')
        if ai_product_data:
            with open(ai_product_json_path, 'w', encoding='utf-8') as f:
                json.dump(ai_product_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Сохранены данные: {ai_product_json_path}")
        
        # Скачиваем PDF для программы AI Product  
        download_curriculum_pdf(
            'https://abit.itmo.ru/program/master/ai_product',
            DATA_DIR,
            'ai_product_itmo_plan.pdf'
        )
            
        logger.info("Инициализация данных завершена")
    
    @staticmethod
    def get_data_files() -> list[str]:
        """
        Получаем список файлов данных для RAG.
        
        Returns:
            Список путей к файлам данных.
        """
        files = []
        
        # JSON файлы
        for json_file in DATA_DIR.glob('*.json'):
            files.append(str(json_file))
        
        # PDF файлы
        for pdf_file in DATA_DIR.glob('*.pdf'):
            files.append(str(pdf_file))
        
        return files 