
import logging
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class My9(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def process_data(self, data,default_synopsis,date_key):

        processed_data = []

        for show in data['Json']['Channels'][0]["Days"][0]["Shows"]:

            program_start = show.get("StartTime")

            # Manejo seguro de títulos
            main_title = (
                show.get("Title", [{}])[0].get("Text")
                if show.get("Title") and len(show.get("Title")) > 0
                else "n/a"
            )
            
            episode_title = (
                show.get("EpisodeTitle", [{}])[0].get("Text")
                if show.get("EpisodeTitle") and len(show.get("EpisodeTitle")) > 0
                else "n/a"
            )
            
            # Manejo seguro de descripciones
            synopsis = (
                show.get("Description", [{}])[0].get("Text")
                if show.get("Description") and len(show.get("Description")) > 0
                else default_synopsis
            )

            if(main_title == "No Programming Available"):
                continue
    
            if synopsis != "n/a" and episode_title != "n/a" :
                content = f"{episode_title} - {synopsis}"
            elif synopsis != "n/a":
                content = synopsis
            elif episode_title != "n/a":
                content = episode_title
            else:
                content = default_synopsis
        
            if program_start:
                date = program_start.split("T")[0]  # Extrae la fecha
                time = program_start.split("T")[1][:5] if len(program_start.split("T")) > 1 else ''  # Solo HH:MM
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
        urls = self.get_date_urls(initial_date, days_range,"titantv")
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data(url)
            if data:
                date_key = url.split("/")[-4][0:8]
                date_key = datetime.strptime(date_key, "%Y%m%d").strftime("%Y-%m-%d")
                programacion = self.process_data(data,default_synopsis,date_key)
                if date_key in self.data:
                    self.data[date_key].extend(programacion)
                else:
                    self.data[date_key] = programacion

        #Borrar los duplicados
        self.remove_duplicates()

        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)