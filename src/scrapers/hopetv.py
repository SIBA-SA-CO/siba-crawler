import logging
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
from .base_scraper import BaseScraper
from datetime import datetime,timedelta

class HopeTv(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def fetch_data_proccess_data(self, url, default_synopsis):

        processed_data = []

        with sync_playwright() as playwright:
            # Inicializa el navegador
            browser = playwright.chromium.launch(headless=True, slow_mo=500)
            page = browser.new_page()

            # Almacén para las respuestas relevantes
            schedule_responses = []

            # Intercepta las respuestas de red
            def handle_response(response):
                if "schedule" in response.url:  # Ajusta según la URL que contenga el schedule
                    try:
                        # Intenta convertir la respuesta en JSON
                        json_data = response.json()
                        if "items" in json_data:
                            schedule_responses.extend(json_data["items"])
                    except Exception as e:
                        return processed_data

            # Configura el evento para capturar respuestas de red
            page.on("response", handle_response)

            # Navega al sitio web
            page.goto(url)

            # Espera a que el contenido relevante esté cargado
            page.wait_for_load_state("networkidle") 
            # Cierra el navegador
            browser.close()

        # Procesa los datos capturados
        for event in schedule_responses:
            # Extraer los datos necesarios del evento
            starts_at = event.get("startsAt", "")
            title = event.get("showTitle", "").strip()  # Elimina espacios innecesarios
            subtitle = event.get("episodeTitle", "")
            description = event.get("description", "")  # Ajusta el campo si es necesario
            content = default_synopsis

            # Si no hay título, omitir el evento
            if not title:

                try:
                    title = event.get("episode", {}).get("show",{}).get("title")
                    subtitle = event.get("episode", {}).get("title")
                except:
                    continue

            # Sobrescribir content si hay subtítulo y/o descripción
            if subtitle and description:
                content = f"{subtitle} - {description}"
            elif subtitle:
                content = subtitle
            elif description:
                content = description


            dt = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))  # Convertir a objeto datetime
            dt_minus_5 = dt - timedelta(hours=5)
            date = dt_minus_5.strftime("%Y-%m-%d")  # Formato AAAA-MM-DD
            time = dt_minus_5.strftime("%H:%M")    # Formato HH:MM


            # Agregar los datos procesados
            processed_data.append({
                "date": date,
                "hour": time,
                "title": title,
                "content": content,
            })

        return processed_data

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        urls = self.get_date_urls(initial_date, days_range,"hopetv")
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data_proccess_data(url,default_synopsis)
            if data:
                date_key = url.split("day=")[-1].split("T")[0]
                self.data[date_key] = data
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)