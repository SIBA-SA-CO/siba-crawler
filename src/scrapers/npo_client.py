import logging
import requests
from .base_scraper import BaseScraper
from datetime import datetime, timedelta

class NpoClient(BaseScraper):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.clients = [
            ("2042e1ee-0e79-4766-aea2-5b300d6839b2", "NPO3"),
            ("316951f5-ce06-41d2-ae24-44eb25368a61", "NPO2"),
            ("83dc1f25-a065-496c-9418-bd5c60dfb36d", "NPO1")
        ]
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
        file_path = './data/npo'
        urls = self.get_date_urls(initial_date_str, days_range,"npo")
        default_synopsis = "Programma "
        for url in urls:
            for client_id, channel_name in self.clients:
                client_url = f"{url}{client_id}"
                data = self.fetch_data(client_url)
                if data:
                    programacion = self.process_data(data, default_synopsis + channel_name)
                    if channel_name in self.data:
                        self.data[channel_name].extend(programacion)
                    else:
                        self.data[channel_name] = programacion


        #Borrar los duplicados
        self.remove_duplicates()

        for channel_name, program_data in self.data.items():
            self.save_data_to_txt(channel_name, program_data, char_replacements,file_path)