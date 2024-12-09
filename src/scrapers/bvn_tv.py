
import logging
from .base_scraper import BaseScraper

class BvnTv(BaseScraper):
    def __init__(self, base_url ):
        super().__init__(base_url)
        self.data = {}

    def process_data(self, data,default_synopsis):
        processed_data = []
        for item in data:
            program_start = item.get("start")
            main_title = item.get("title", "")
            synopsis = item.get("content", "") or default_synopsis

            if not main_title:
                continue 
                
            if program_start:
                date = program_start.split(" ")[0]  # Extrae la fecha
                time = program_start.split(" ")[1][:5] if len(program_start.split(" ")) > 1 else ''  # Solo HH:MM
                processed_data.append({
                    "date": date,
                    "hour": time,
                    "title": main_title,
                    "content": synopsis,
                })
        return processed_data

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        """
        Obtiene la guía de programas de BVN TV para los días antes y después de la fecha inicial.
        """
        urls = self.get_date_urls(initial_date, days_range)
        file_path = './data/bvn'
        default_synopsis = "Programma BVN"
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data(url)
            if data:
                date_key = url.split("/")[-2]
                self.data[date_key] = self.process_data(data,default_synopsis)
                
        self.save_data_to_txt("BvnTv", self.data, char_replacements,file_path)