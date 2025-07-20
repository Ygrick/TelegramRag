"""Парсер для страниц программ ИТМО."""

import json
from typing import Optional

import requests
from bs4 import BeautifulSoup


def parse_itmo_program(url: str) -> Optional[dict]:
    """
    Парсим страницу магистерской программы ИТМО.
    
    Извлекаем JSON данные из скрипта __NEXT_DATA__ для получения
    структурированной информации о программе.
    
    Args:
        url: URL страницы программы.
        
    Returns:
        Словарь с данными программы или None при ошибке.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем скрипт с JSON данными
        next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
        if not next_data_script:
            return None
            
        return json.loads(next_data_script.string)
        
    except (requests.RequestException, json.JSONDecodeError, AttributeError):
        return None