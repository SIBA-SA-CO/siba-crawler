import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class Mlb(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def process_data(self, data,default_synopsis):

        processed_data = []

        for item in data['shows']:

            content = default_synopsis

            date_raw = item.get("startdate")
            date_obj = datetime.strptime(date_raw, '%m/%d/%Y')
            date = date_obj.strftime('%Y-%m-%d')
            
            time_raw= item.get("starttime")
            time = datetime.strptime(time_raw, "%I:%M %p").strftime("%H:%M")

            title = item.get("umbrellatitle") or item.get("seriestitle") 

            if not title:
                continue

            episode_title = item.get("episodetitle")
            synopsis = item.get("synopsis")

            if episode_title and synopsis:
                content = f"{episode_title} - {synopsis}"
            elif episode_title:
                content = episode_title
            elif synopsis:
                content = synopsis

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
        data = self.fetch_data(url)
        if data:
            self.data = self.process_data(data,default_synopsis)
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)