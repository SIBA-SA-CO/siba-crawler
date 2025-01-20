import os
import logging
import requests
from time import sleep
from datetime import datetime, timedelta

class BaseScraper:
    def __init__(self, base_url, retries=3, log_file_path="./logs/app.log", data_dir="./data"):
        """
        Inicializa la clase base con la URL base y las opciones del navegador.
        """
        self.base_url = base_url
        self.retries = retries
        self.data = {}

        # Asegurarse de que las carpetas de log y datos existan
        log_dir = os.path.dirname(log_file_path)
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        # Configuración de logging
        logging.basicConfig(filename=log_file_path, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

    def fetch_data(self, url):
        """
        Obtiene los datos JSON desde la URL especificada con reintentos.
        """
        attempt = 0
        while attempt < self.retries:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Verifica errores HTTP
                logging.info(f"Éxito al obtener datos de {url}")
                return response.json()  # Retorna el contenido como JSON
            except requests.RequestException as e:
                attempt += 1
                logging.error(f"Error al obtener datos de {url} (Intento {attempt}/{self.retries}): {e}")
                sleep(2)  # Espera antes de reintentar
                if attempt == self.retries:
                    logging.critical(f"Fallo al obtener datos de {url} después de {self.retries} intentos.")
        return None

    def apply_replacements(self, text, replacements):
        """
        Aplica los reemplazos de caracteres a un texto dado.
        """
        if replacements:
            for old_char, new_char in replacements.items():
                text = text.replace(old_char, new_char)
        return text

    def get_date_urls(self, initial_date_str, days_range=15,url_format=""):
        """
        Genera las URLs correspondientes a los días desde 15 días antes hasta 15 días después de la fecha inicial.
        """
        initial_date = datetime.strptime(initial_date_str, "%Y-%m-%d")
        dates = [
            initial_date + timedelta(days=i)
            for i in range(-days_range, days_range + 1)
        ]

        if url_format == "npo":
            # NPO URL format (using %d-%m-%Y for the date)
            return [
                f"{self.base_url}{date.strftime('%d-%m-%Y')}&guid="
                for date in dates
            ]
        elif url_format == "titantv":
            # my9 format: Replace the date and add hourly intervals (e.g., 0000, 0100, ... 2300)
            urls = []
            for date in dates:
                date_str = date.strftime('%Y%m%d')  # Format date as YYYYMMDD
                for hour in range(0, 24):
                    hour_str = f"{hour:02}00"  # Format hour as HHMM
                    url = f"{self.base_url}{date_str}{hour_str}/240/292/7"
                    urls.append(url)
            return urls
        elif url_format == "hopetv":
            urls = []
            for date in dates:
                date_str = date.strftime('%Y-%m-%d')
                url = f"{self.base_url}{date_str}T00%3A00%3A00-05%3A00"
                urls.append(url)
            return urls
        else:
            # Default URL format (using %Y-%m-%d for the date)
            return [
                f"{self.base_url}{date.strftime('%Y-%m-%d')}/"
                for date in dates
            ]
        
        

    def write_program_data(self,f, program, current_date, char_replacements=None):
        """
        Escribe los datos de un programa en el archivo de texto.

        :param f: Objeto de archivo abierto.
        :param program: Diccionario con los datos del programa.
        :param current_date: Fecha actual escrita en el archivo.
        :param char_replacements: Diccionario con reemplazos de caracteres opcionales.
        :return: La fecha actualizada si cambió.
        """
        date = program.get('date', '')
        hour = program.get('hour', '')
        title = program.get('title', '').strip()
        content = program.get('content', '').strip()

        # Aplicar reemplazos de caracteres si es necesario
        if char_replacements:
            title = self.apply_replacements(title, char_replacements)
            content = self.apply_replacements(content, char_replacements)

        # Escribir la fecha solo si cambia
        if date != current_date:
            current_date = date
            f.write(f"{current_date}\n")

        # Escribir los datos del programa
        f.write(
            f"{hour}---{title}---{content}---USA|TV-PG---SIBA_TIPO|UNICO--- --- --- --- --- ---SIN_CTI|{content}--- --- --- ---\n"
        )

        return current_date


    def save_data_to_txt(self, channel_name, program_data, char_replacements=None, file_path='./data'):
        """
        Guarda los datos del canal en un archivo de texto con fecha, hora, título y sinopsis.
        El nombre del archivo será '{channel_name}_program_guide_{fecha_actual}.txt'.

        :param channel_name: Nombre del canal.
        :param program_data: Datos del programa (puede ser una lista o un diccionario).
        :param char_replacements: Reemplazos de caracteres opcionales.
        :param file_path: Ruta base para guardar el archivo.
        """
        
        file_name = f"{channel_name}.txt"
        full_file_path = os.path.join(file_path, file_name)

        try:
            with open(full_file_path, 'w', encoding='utf-8') as f:
                current_date = None

                # Si program_data es un diccionario (agrupado por fecha)
                if isinstance(program_data, dict):
                    for date, programs in program_data.items():
                        for program in programs:
                            current_date = self.write_program_data(f,program, current_date, char_replacements)

                # Si program_data es una lista (programas individuales)
                elif isinstance(program_data, list):
                    for program in program_data:
                        current_date = self.write_program_data(f,program, current_date, char_replacements)

                else:
                    logging.error("El formato de program_data no es válido. Debe ser un diccionario o una lista.")
                    return

            logging.info(f"Archivo generado para {channel_name}: {full_file_path}")

        except Exception as e:
            logging.error(f"Error al guardar los datos en el archivo {full_file_path}: {e}")


    def get_text_if_exists(self, locator, selector, timeout=500):
        """
        Verifica si un elemento existe y devuelve su texto. Si no existe, devuelve "No disponible".
        """
        try:
            # Localiza el elemento dentro del timeout
            element = locator.locator(selector).first
            if element.count() > 0:
                return element.text_content(timeout=timeout).strip()
            else:
                return "n/a"
        except TimeoutError:
            return "No disponible"

    def remove_duplicates(self):
        for key_name, program_data in self.data.items():
            # Utilizamos un conjunto para evitar duplicados - Elimina duplicados de una lista o diccionario jerárquico.
            seen = set()
            unique_data = []
            for program in program_data:
                # Convertimos el diccionario en una tupla de pares clave-valor para que sea "hasheable"
                program_tuple = tuple(program.items())
                if program_tuple not in seen:
                    seen.add(program_tuple)
                    unique_data.append(program)
            # Actualizamos la lista del canal con solo los datos únicos
            self.data[key_name] = unique_data

    def remove_duplicates_flat_list(self, data):
        # Elimina duplicados de una lista plana.
        seen = set()
        unique_data = []
        for item in data:
            unique_key = (item['date'], item['hour'], item['title'],item['content'])
            if unique_key not in seen:
                seen.add(unique_key)
                unique_data.append(item)
        return unique_data