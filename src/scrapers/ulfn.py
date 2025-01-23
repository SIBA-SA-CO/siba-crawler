import logging
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class Ulfn(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}

    def convert_to_24_hour(self, time_str):

        time_str = time_str.replace("ET", "").strip()

        if "NOON" in time_str:
            return "12:00"
        if "MIDNIGHT" in time_str:
            return "00:00"

        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
        except ValueError:
            time_obj = datetime.strptime(time_str, "%I %p")

        return time_obj.strftime("%H:%M")

    def fetch_data_proccess_data(self, url, default_synopsis, initial_date, days_range):
        schedule_by_day_type = {
            'Weekdays(Eastern Time)': [],
            'Saturday (Eastern Time)': [],
            'Sunday (Eastern Time)': []
        }
        processed_data = []

        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        schedule_sections = soup.find_all('div', class_='wp-block-column')
        initial_date = datetime.strptime(initial_date, "%Y-%m-%d")
        date_range  = [initial_date + timedelta(days=i) for i in range(-days_range, days_range + 1)]

        for section in schedule_sections:
            day_type = section.find('h2').get_text(strip=True)
            schedule_items = section.find_all('p')
            for item in schedule_items:
                text = item.get_text(strip=True)
                if "–" in text:
                    time, program = text.split("–", 1)
                    time_24hr = self.convert_to_24_hour(time.strip())
                    schedule_by_day_type[day_type].append({
                        'hour': time_24hr,
                        'title': program.strip(),
                        'content': default_synopsis
                    })

        for date in date_range :
            if date.weekday() < 5:
                day_type = 'Weekdays(Eastern Time)'
            elif date.weekday() == 5:
                day_type = 'Saturday (Eastern Time)'
            elif date.weekday() == 6:
                day_type = 'Sunday (Eastern Time)'

            for item in schedule_by_day_type[day_type]:
                processed_data.append({
                    'date': date.strftime("%Y-%m-%d"),
                    'hour': item['hour'],
                    'title': item['title'],
                    'content': item['content'],
                })

        processed_data = sorted(
            processed_data,
            key=lambda x: (x['date'], x['hour'])
        )
        
        return processed_data

      

    def scrape_program_guide(self, initial_date, days_range, char_replacements=None):
        file_path = self.channel_config['output_path']
        default_synopsis = self.channel_config['default_description']
        file_name = self.channel_config['file_name']
        url = self.base_url
        logging.info(f"Procesando: {url}")
        data = self.fetch_data_proccess_data(url, default_synopsis, initial_date, days_range)
        if data:
            self.data = data
        self.save_data_to_txt(file_name, self.data, char_replacements,file_path)