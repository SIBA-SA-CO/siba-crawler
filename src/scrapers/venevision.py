import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class VeneVision(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def fetch_data_proccess_data(self, url, default_synopsis):
        processed_data = []

        # Obtener el HTML de la página
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Extraer los datos necesarios
        items = soup.find_all('div', class_='item')
        for item in items:

            title_tag = item.find('h3', class_='ml0')
            if not title_tag: 
                continue
            title = title_tag.text.strip()

            
            subtitle_tag = item.find('p', class_='subtitle fs13 ptb3')
            subtitle_text = subtitle_tag.text.strip()
            date_raw, hour_raw = subtitle_text.split(' de ')
            
            # Convertir la fecha al formato AAAA-MM-DD
            date_obj = datetime.strptime(date_raw, '%d-%m-%Y')
            date = date_obj.strftime('%Y-%m-%d')
            
            # Limpiar y convertir la hora al formato HH:MM
            hour_parts = hour_raw.split(' a ')
            time = datetime.strptime(hour_parts[0].strip(), '%I:%M %p').strftime('%H:%M')
            
            next_p = subtitle_tag.find_next('p')
            content = next_p.text.strip() if next_p else default_synopsis
            processed_data.append({
                "date": date,
                "hour": time,
                "title": title,
                "content": content,
            })

        processed_data = self.remove_duplicates_flat_list(processed_data)

        return processed_data
            

      

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        url = self.base_url
        logging.info(f"Procesando: {url}")
        data = self.fetch_data_proccess_data(url,default_synopsis)
        if data:
            self.data = data
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)