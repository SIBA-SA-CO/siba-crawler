import logging
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
from .base_scraper import BaseScraper
from datetime import datetime

class MeTvToons(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def format_time(self,time_text):
        """
        Convierte una hora en formato '6:00am ET' a '06:00'.
        """

        # Usa regex para extraer la hora y el período (am/pm)
        match = re.match(r"(\d{1,2}:\d{2})(am|pm)", time_text.lower())
        if match:
            time_str, period = match.groups()
            # Convierte la hora a formato 24 horas
            time_obj = datetime.strptime(time_str + period, "%I:%M%p")
            return time_obj.strftime("%H:%M")
        return "Hora no válida"

    def fetch_data_proccess_data(self, url,default_synopsis):

        events_data = []

        with sync_playwright() as playwright:
            # Inicializa el navegador
            browser = playwright.chromium.launch(headless=True, slow_mo=500)
            page = browser.new_page()

            # Navega al sitio web
            page.goto(url)
            date = url.split('/')[-2]

            try:
                # Espera a que el contenedor esté visible
                container_xpath = '//*[@id="schedule_container"]'
                page.wait_for_selector(f'xpath={container_xpath}', timeout=5000)

                # Localiza el contenedor
                container = page.locator(f'xpath={container_xpath}')

                # Buscar el evento en section.current-show-wrapper
                current_show_wrapper = container.locator('section.current-show-wrapper')
                current_show_exists = current_show_wrapper.count() >= 1 

                # Si existe un evento en current-show-wrapper, extraer datos
                if current_show_exists:
                    current_event = current_show_wrapper.first  # Tomar el primer (y único) evento en esta sección
                    # Extrae los textos de los elementos especificados
                    show_time_raw = self.get_text_if_exists(current_event, '.sched-show-title')
                    show_time_raw = show_time_raw[-10:].strip()
                    show_time = self.format_time(show_time_raw)
                    show_name = self.get_text_if_exists(current_event, '.current-show-title')
                    episode_title = self.get_text_if_exists(current_event, '.current-episode-title')
                    description = self.get_text_if_exists(current_event, 'p')
                    
                    if description != "n/a" and episode_title != "n/a":
                        content = f"{episode_title} - {description}"
                    elif description != "n/a":
                        content = description
                    elif episode_title != "n/a":
                        content = episode_title
                    else:
                        content = default_synopsis

                    events_data.append({
                        "date": date,  # Se asume que 'date' ya está definido
                        "hour": show_time,
                        "title": show_name,
                        "content": content,
                    })

                # Busca y cuenta los eventos dentro del contenedor
                events = container.locator('div.sched-item')
                current_count = events.count()

                # Verifica si current_count es mayor o igual a 1
                if current_count >= 1:
                    # Extrae datos de cada evento
                    for i in range(current_count):
                        event = events.nth(i)

                        # Extrae los textos de los elementos especificados
                        show_time_raw  = self.get_text_if_exists(event, '.sched-show-time')
                        show_time = self.format_time(show_time_raw)
                        show_name = self.get_text_if_exists(event, '.sched-show-name')
                        episode_title = self.get_text_if_exists(event, '.sched-episode-title')
                        description = self.get_text_if_exists(event, 'p')

                        if description != "n/a" and episode_title != "n/a" :
                            content = f"{episode_title} - {description}"
                        elif description != "n/a":
                            content = description
                        elif episode_title != "n/a":
                            content = episode_title
                        else:
                            content = default_synopsis

                        events_data.append({
                        "date": date,  # Aquí se asume que 'date' ya está definido
                        "hour": show_time,
                        "title": show_name,
                        "content": content,
                    })

                    
            except TimeoutError:
                print("No se pudo cargar el contenedor o los eventos dentro del tiempo esperado.")

            # Ordena los eventos por hora (de menor a mayor)
            events_data_sorted = sorted(events_data, key=lambda x: x["hour"] if x["hour"] else datetime.min)
            # Cierra el navegador
            browser.close()

            return events_data_sorted

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        urls = self.get_date_urls(initial_date, days_range)
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data_proccess_data(url,default_synopsis)
            if data:
                date_key = url.split("/")[-2]
                self.data[date_key] = data
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)