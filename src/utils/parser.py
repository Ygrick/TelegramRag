"""Парсер для страниц программ ИТМО."""

import json
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

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


def download_curriculum_pdf(url: str, save_dir: Path, filename: str) -> Optional[str]:
    """
    Скачиваем PDF учебного плана с страницы программы ИТМО.
    
    Ищем ссылку на учебный план и скачиваем PDF файл в указанную директорию.
    
    Args:
        url: URL страницы программы.
        save_dir: Путь к директории для сохранения.
        filename: Имя файла для сохранения.
        
    Returns:
        Путь к скачанному файлу или None при ошибке.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # Получаем страницу
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем ссылку на учебный план
        curriculum_link_tag = soup.find('a', string=lambda t: t and 'Учебный план' in t)
        if not curriculum_link_tag or not curriculum_link_tag.has_attr('href'):
            print("[!] Не удалось найти ссылку на учебный план.")
            return None
            
        # Формируем абсолютный URL
        pdf_absolute_url = urljoin(url, curriculum_link_tag['href'])
        print(f"[*] Найдена ссылка на учебный план: {pdf_absolute_url}")
        
        # Скачиваем PDF
        print("[*] Скачиваю PDF файл...")
        pdf_response = requests.get(pdf_absolute_url, headers=headers)
        pdf_response.raise_for_status()
        
        # Создаем директорию если её нет
        save_dir.mkdir(exist_ok=True)
        
        # Сохраняем файл
        file_path = save_dir / filename
        with open(file_path, 'wb') as f:
            f.write(pdf_response.content)
            
        print(f"[+] PDF сохранен: {file_path}")
        return str(file_path)
        
    except requests.RequestException as e:
        print(f"[!] Ошибка при скачивании: {e}")
        return None