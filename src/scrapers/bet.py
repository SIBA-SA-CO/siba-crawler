
import logging
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class Bet(BaseScraper):
    def __init__(self,channel_config):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def process_data(self, data,default_synopsis,date_key):

        processed_data = []
        for item in data['tvSchedules']:

            program_start = item.get("airTime")
            main_title = item.get("seriesTitle")
            episode_title = item.get("episodeTitle") or 'n/a'
            synopsis = item["meta"].get("description") or 'n/a'
            

            if synopsis != "n/a" and episode_title != "n/a" :
                content = f"{episode_title} - {synopsis}"
            elif synopsis != "n/a":
                content = synopsis
            elif episode_title != "n/a":
                content = episode_title
            else:
                content = default_synopsis
                
            if program_start:
                fecha_obj = datetime.fromisoformat(program_start)
                fecha_modificada = fecha_obj - timedelta(hours=5)
                date = fecha_modificada.strftime("%Y-%m-%d")
                time = fecha_modificada.strftime("%H:%M")

                # Filtrar solo los datos que coinciden con la fecha indicada en date_key
                if date == date_key:
                    processed_data.append({
                        "date": date,
                        "hour": time,
                        "title": main_title,
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