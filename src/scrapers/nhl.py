import logging
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class Nhl(BaseScraper):
    def __init__(self,channel_config):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def process_data(self, data,default_synopsis,date_key):

        processed_data = []
        for item in data['broadcasts']:

            content = default_synopsis
            date_raw = item.get("startTime")
            date, time = date_raw.split("T")
            time = time[:5]

            title = item.get("title") or title
            description = item.get("description") or description

            if description:
                content = description
            
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
            data = self.fetch_data(url)
            if data:
                date_key = url.split("/")[-2]
                self.data[date_key] = self.process_data(data,default_synopsis,date_key)
                
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)