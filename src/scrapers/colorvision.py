import logging
import requests
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class ColorVision(BaseScraper):
    def __init__(self, channel_config ):
        super().__init__(channel_config["url"])
        self.channel_config = channel_config
        self.data = {}
        

    def get_days_range(self,days_list):

        days_of_week = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
        # Convertir los días a índices
        day_indices = [days_of_week.index(day.lower()) for day in days_list]
        
        # Ordenar los índices
        day_indices.sort()
        
        # Generar todos los días entre el primer y último índice
        all_days = days_of_week[day_indices[0]:day_indices[-1] + 1]
        
        return all_days

    def fetch_data_proccess_data(self, url, default_synopsis, initial_date, days_range):
        schedule_by_day_type = {
            'lunes-a-viernes-tab': [],
            'sbado-tab': [],
            'domingo-tab': []
        }
        processed_data = []
        

        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        initial_date = datetime.strptime(initial_date, "%Y-%m-%d")
        date_range  = [initial_date + timedelta(days=i) for i in range(-days_range, days_range + 1)]

        day_name_to_weekday = {
            'lunes': 0,
            'martes': 1,
            'miércoles': 2,
            'jueves': 3,
            'viernes': 4,
            'sábado': 5,
            'domingo': 6
        }

        for day_tab_id in schedule_by_day_type.keys():
            day_section = soup.find('div', id=day_tab_id) 
            if not day_section:
                continue

            previous_hour = None
            is_am = True 
            
            elements = day_section.find_all('div', class_='elementor-cta__content')
            for index,element in enumerate(elements):
                title = element.find('h2', class_='elementor-cta__title').get_text(strip=True)
                description = element.find('div', class_='elementor-cta__description').get_text(strip=True)
                time_match = re.search(r'(\d{1,2}:\d{2})', description)
                hour_str = time_match.group(1) 
                
                # Convertir la hora al formato datetime (para facilitar el manejo)
                current_hour = datetime.strptime(hour_str, "%I:%M")  # Interpreta en base a 12 horas
                # Manejo especial para las 12:00 (mediodía y medianoche)
                if current_hour.hour == 12 and is_am:
                    current_hour = current_hour.replace(hour=0)  # Medianoche -> 00:00
                elif current_hour.hour != 12 and not is_am:
                    current_hour += timedelta(hours=12)  # Añadir 12 horas si es PM y no es mediodía

                if index == 1:
                    if previous_hour.time() > current_hour.time():
                        is_am = is_am
                # Si hay una hora anterior, ajustar AM/PM según la cronología
                elif previous_hour and current_hour.time() < previous_hour.time():
                    is_am = not is_am  # Cambiar entre AM y PM si la hora es inconsistente
                    
                    # Recalcular la hora con el nuevo AM/PM
                    if is_am and current_hour.hour == 12:
                        current_hour = current_hour.replace(hour=0)  # Medianoche -> 00:00
                    elif not is_am and current_hour.hour != 12:
                        current_hour += timedelta(hours=12)  # Añadir 12 horas si es PM y no es mediodía

                # Formatear la hora en HH:MM
                hour_24 = current_hour.strftime("%H:%M")
                schedule_by_day_type[day_tab_id].append({
                    'hour': hour_24,
                    'title': title,
                    'content': description
                })
                
                # Actualizar la hora anterior
                previous_hour = current_hour

        for date in date_range :
            if date.weekday() < 5:
                day_type = 'lunes-a-viernes-tab'
            elif date.weekday() == 5:
                day_type = 'sbado-tab'
            elif date.weekday() == 6:
                day_type = 'domingo-tab'

            for item in schedule_by_day_type[day_type]:
                event_date = date.strftime("%Y-%m-%d")
                day_name = date.strftime("%A").lower()
                day_translation = {
                    'monday': 'lunes',
                    'tuesday': 'martes',
                    'wednesday': 'miércoles',
                    'thursday': 'jueves',
                    'friday': 'viernes',
                    'saturday': 'sábado',
                    'sunday': 'domingo'
                }
                event_day_name = day_translation.get(day_name, day_name)
                days_in_content = re.findall(r'\b(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b', item['content'], re.IGNORECASE)
                days_in_content = [day.lower() for day in days_in_content]

                if days_in_content:
                    if len(days_in_content) > 1:
                        all_days_in_range = self.get_days_range(days_in_content)
                        evento = item
                    else:
                        all_days_in_range = days_in_content
                        evento = item
                    
                    if event_day_name in all_days_in_range:
                        matching_events = [e for e in schedule_by_day_type[day_type] if e['hour'] == item['hour']]
                        processed_data.append({
                            'date': event_date,
                            'hour': item['hour'],
                            'title': item['title'],
                            'content': default_synopsis,
                        })
                else:
                    processed_data.append({
                        'date': event_date,
                        'hour': item['hour'],
                        'title': item['title'],
                        'content': default_synopsis,
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