import logging
import re
import requests
from datetime import datetime
from .base_scraper import BaseScraper
from datetime import datetime,timedelta
from bs4 import BeautifulSoup

class StartTv(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def fetch_data_proccess_data(self, url, default_synopsis):

        processed_data = []
        response = requests.get(url)
        date = url.split('/')[-2]
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        if response.history:
            return processed_data

        # Encuentra todos los elementos del programa en la página
        schedule_items = soup.find_all('div', class_='sched-item clearfix')

        for item in schedule_items:

            time_str = item.find('div', class_='sched-show-time').text.strip()
            time = datetime.strptime(time_str, "%I:%M%p").strftime("%H:%M")

            title = item.find('h1', class_='hp-section-header sched-inline').text.strip()

            episode = ""
            description = ""
            content = default_synopsis
            
            description_element = item.find('div', class_='sched-show-desc')

            if description_element:
                h2_element = description_element.find('h2')
                episode = h2_element.text.strip() if h2_element else ""
                description = (
                    h2_element.next_sibling.strip() if h2_element and h2_element.next_sibling else ""
                )

            
            if episode and description:
                content = f"{episode} - {description}"
            elif episode:
                content = episode
            elif description:
                content = description

            processed_data.append({
                "date": date,
                "hour": time,
                "title": title,
                "content": content,
            })

        processed_data = sorted(processed_data, key=lambda x: x["hour"] if x["hour"] else datetime.min)


        return processed_data


    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        urls = self.get_date_urls(initial_date, days_range)
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        for url in urls:
            logging.info(f"Procesando: {url}")
            data = self.fetch_data_proccess_data(url,default_synopsis)
            if data:
                date_key = url.split('/')[-2]
                self.data[date_key] = data
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)