import logging
import requests
from .base_scraper import BaseScraper
from datetime import datetime, timedelta

class NpoClient(BaseScraper):
    def __init__(self, channel_config):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}


    def process_data(self, data,default_synopsis):
        processed_data = []
        for item in data:
            program_start = item.get("programStart")
            main_title = item.get("mainTitle", "")
            synopsis = item.get("synopsis","") or default_synopsis

            if not main_title:
                continue 

            if program_start:
                program_start = program_start // 1000 if program_start > 10**10 else program_start
                original_date = datetime.fromtimestamp(program_start)

                fecha_modificada = original_date + timedelta(hours=6)

                date = fecha_modificada.strftime("%Y-%m-%d")
                time = fecha_modificada.strftime("%H:%M")

                processed_data.append({
                    "date": date,
                    "hour": time,
                    "title": main_title,
                    "content": synopsis,
                })

        return processed_data

    def scrape_program_guide(self, initial_date_str, days_range, char_replacements=None):
        file_path = self.channel_config['output_path']
        urls = self.get_date_urls(initial_date_str, days_range,"npo")
        for url in urls:
            for channel  in self.channel_config['sub_channels']:
                channel_name = channel.get("file_name")
                client_id =  channel.get("id")
                default_synopsis = channel.get("default_description")
                client_url = f"{url}{client_id}"
                data = self.fetch_data(client_url)
                if data:
                    programacion = self.process_data(data, default_synopsis)
                    if channel_name in self.data:
                        self.data[channel_name].extend(programacion)
                    else:
                        self.data[channel_name] = programacion


        # #Borrar los duplicados
        self.remove_duplicates()

        for channel_name, program_data in self.data.items():
            self.save_data_to_txt(channel_name, program_data, char_replacements,file_path)