import logging
import requests
import re
from datetime import datetime, timedelta
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class MeTv(BaseScraper):
    def __init__(self,channel_config):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def fetch_data_proccess_data(self, url,default_synopsis):

        processed_data = []
        response = requests.get(url)
        date = url.split('/')[-2]
        html = response.text

        if response.history:
            return processed_data
        soup = BeautifulSoup(html, 'html.parser')
        # Buscar todos los bloques de programación
        schedule_items = soup.find_all('div', class_='schedule-item-wrap')
        # Verificar si se encontraron bloques
        if schedule_items:
            for item in schedule_items:

                time_raw = item.find('span', class_='schedule-on-now').get_text(strip=True) 

                if time_raw:
                    time_cleaned = time_raw.split('Now:', 1)[-1].strip()
                    original_time = datetime.strptime(time_cleaned, "%I:%M%p")
                    # updated_time = original_time + timedelta(hours=1)
                    # time = updated_time.strftime("%H:%M")
                    time = original_time.strftime("%H:%M")
                    

                main_title = item.find('div', class_='content-now-title-schedule').get_text(strip=True)
                episode_title = item.find('div', class_='schedule-entry-episode-title').get_text(strip=True) if item.find('div', class_='schedule-entry-episode-title') else "n/a"
                description = item.find('div', class_='schedule-entry-episode-desc').get_text(strip=True) if item.find('div', class_='schedule-entry-episode-desc') else "n/a"
                episode_title = episode_title.strip()
                description = description.strip()
                content = (
                    f"{episode_title} - {description}" if episode_title not in ["n/a", ""] and description not in ["n/a", ""] 
                    else episode_title if episode_title not in ["n/a", ""] 
                    else description if description not in ["n/a", ""] 
                    else " "
                )

                processed_data.append({
                    "date": date,
                    "hour": time,
                    "title": main_title,
                    "content": content,
                })

        events_data_sorted = sorted(processed_data, key=lambda x: x["hour"] if x["hour"] else datetime.min)

        return events_data_sorted

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        urls = self.get_date_urls(initial_date, days_range)
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data_proccess_data(url,default_synopsis)
            if data:
                date_key = url.split("/")[-2]
                self.data[date_key] = data
                
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)