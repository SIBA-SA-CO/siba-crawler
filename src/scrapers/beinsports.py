import logging
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class BeinSports(BaseScraper):
    def __init__(self,channel_config):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def process_data(self, data,default_synopsis,date_key):

        processed_data = []
        for item in data['rows']:
            content = default_synopsis

            date_raw = item.get("startDate")
            date_obj = datetime.strptime(date_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
            adjusted_date = date_obj - timedelta(hours=5)
            date = adjusted_date.strftime("%Y-%m-%d").strip()
            time = adjusted_date.strftime("%H:%M").strip()

            title = item.get("title").strip()
            description = item.get("category").strip()

            if description:
                content = description

            if date == date_key:
                processed_data.append({
                    "date": date,
                    "hour": time,
                    "title": title,
                    "content": content,
                })

        return processed_data

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        urls = self.get_date_urls(initial_date, days_range,"beinsports")
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data(url,headers)
            if data:
                date_key = url.split("T")[1][-10:]
                self.data[date_key] = self.process_data(data,default_synopsis,date_key)

        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)