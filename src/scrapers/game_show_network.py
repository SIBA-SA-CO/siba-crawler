import logging
import requests
import re
import json 
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class GameShowNetwork(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def fetch_data_proccess_data(self, url,default_synopsis):

        processed_data = []
        response = requests.get(url)
        html = response.text
        # Buscar el contenido de siteSettings.schedule
        pattern = r'<script[^>]*>\s*siteSettings\.schedule\s*=\s*(\[.*?\]);'
        match = re.search(pattern, html, re.DOTALL)

        if match:
            schedule = match.group(1)
            data = json.loads(schedule)
            for item in data:
                program_start = item.get('startTime')
                title = item.get('title')
                host = item.get('host')
                description = item.get('description')
                original_date = datetime.fromtimestamp(program_start)
                date = original_date.strftime("%Y-%m-%d")
                time = original_date.strftime("%H:%M")

                if description != "" and host != "":
                    content = f"{host} - {description}"
                elif description != "":
                    content = description
                elif host != "":
                    content = host
                else:
                    content = default_synopsis

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
        url = self.base_url
        logging.info(f"Procesando: {url}")
        data = self.fetch_data_proccess_data(url,default_synopsis)
        if data:
            self.data = data
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)