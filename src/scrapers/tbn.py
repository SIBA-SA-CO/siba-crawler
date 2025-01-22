import logging
import re
import requests
import html
from datetime import datetime
from .base_scraper import BaseScraper
from datetime import datetime,timedelta
from bs4 import BeautifulSoup

class Tbn(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def fetch_data_proccess_data(self, url, default_synopsis):

        processed_data = []
        response = requests.get(url)
        target_date = url.split('=')[-1][0:10]
        html_str = response.text
        soup = BeautifulSoup(html_str, 'html.parser')

        # Encuentra todos los elementos del programa en la página
        episode_rows  = soup.find_all('tr', class_='episode-row')

        for row in episode_rows:

            content = default_synopsis

            date_str = row.get('data-timestamp')
            date_time = datetime.fromisoformat(str(date_str))
            date_time_adjusted  = date_time + timedelta(hours=-5)
            date = date_time_adjusted.date()
            
            if str(date) != target_date:
                continue

            time = date_time_adjusted.time().strftime("%H:%M")

            # Título del programa
            title_element = row.find('td', class_='title-column')
            title = title_element.text.strip()

            # Descripción
            description_element = description = row.get('data-synopsis')
            if(description_element):
                if description_element.strip().startswith('<'):
                    pass
                else:
                    soup = BeautifulSoup(description_element, 'html.parser')
                    content = soup.get_text(strip=True)
                    content = re.sub(r'\s+', ' ', content).strip()

            processed_data.append({
                "date": date,
                "hour": time,
                "title": title,
                "content": content,
            })

        return processed_data


    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        urls = self.get_date_urls(initial_date, days_range)
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data_proccess_data(url,default_synopsis)
            if data:
                date_key = url.split('=')[-1][0:10]
                self.data[date_key] = data
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)