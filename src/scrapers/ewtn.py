import logging
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class Ewtn(BaseScraper):
    def __init__(self, channel_config):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def fetch_data_proccess_data(self, url, default_synopsis):
        processed_data = []

        # Obtener el HTML de la página
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        target_date = url.split('/')[-2]
        # Extraer los datos necesarios
        entries = soup.find_all('div', class_='schedule__entry')

        if not entries:
            return processed_data
        
        for entry in entries:
            # Extraer título principal
            title_container = entry.find('div', class_='schedule__title')
            if not title_container:
                continue
            title = title_container.text.strip()
            title = re.sub(r'\s+', ' ', title.replace("\n", " "))
            

            # Extraer subtítulo
            subtitle_container = entry.find('h3', class_='schedule__sub-title')
            subtitle = subtitle_container.text.strip() if subtitle_container else 'n/a'
            subtitle = re.sub(r'\s+', ' ', subtitle.replace("\n", " "))

            # Extraer descripción
            description_container = entry.find('p', class_='schedule__description')
            description = description_container.text.strip() if description_container else 'n/a'
            description = re.sub(r'\s+', ' ', description.replace("\n", " "))

            content = default_synopsis

            # Sobrescribir content si hay subtítulo y/o descripción
            if subtitle and description:
                content = f"{subtitle} - {description}"
            elif subtitle:
                content = subtitle
            elif description:
                content = description
        

            # Extraer hora de inicio y fin
            time_container = entry.find('div', class_='schedule__time')
            start_time = time_container['data-datetime'] if time_container and 'data-datetime' in time_container.attrs else None
            start_time_obj = datetime.fromisoformat(start_time.replace("Z", "+00:00"))

            # Restar 5 horas
            adjusted_time_obj = start_time_obj - timedelta(hours=5)

            # Extraer la fecha en formato AAAA-MM-DD
            date = adjusted_time_obj.strftime('%Y-%m-%d')
            if date != target_date:
                continue

            # Extraer la hora en formato HH:MM
            time = adjusted_time_obj.strftime('%H:%M')

            processed_data.append({
                "date": date,
                "hour": time,
                "title": title,
                "content": content,
            })

        return processed_data

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        urls = self.get_date_urls(initial_date, days_range)
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data_proccess_data(url,default_synopsis)
            if data:
                date_key = url.split("/")[-2]
                self.data[date_key] = data

        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)