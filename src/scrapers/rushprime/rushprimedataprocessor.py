import pytz
from datetime import datetime
from src.scrapers.core.interfaces.idataprocessor import IDataProcessor

class RushPrimeDataProcessor(IDataProcessor):
    """
    Procesador de datos para eventos de programación de Rush Prime.

    Esta clase toma datos crudos provenientes de un archivo (por ejemplo, un CSV),
    convierte las fechas y horas de los eventos desde una zona horaria fuente hacia la zona horaria
    objetivo ("America/Bogota") y estructura los eventos para su posterior almacenamiento o uso.

    Atributos:
        sourceTimezone (pytz.timezone): Zona horaria original de los datos recibidos.
        targetTimezone (pytz.timezone): Zona horaria destino para convertir las fechas (siempre 'America/Bogota').
    """

    def __init__(self, timezone: str):
        """
        Inicializa el procesador con la zona horaria fuente de los eventos.

        Args:
            timezone (str): Zona horaria fuente (ej. "UTC", "America/New_York", etc.).
        """
        self.sourceTimezone = pytz.timezone(timezone)
        self.targetTimezone = pytz.timezone("America/Bogota")

    def processData(self, rawData, defaultDescription: str, targetDate: str) -> list:
        """
        Procesa una tabla de datos crudos y extrae la información relevante de los eventos.

        Convierte fechas y horas desde la zona horaria fuente a la zona horaria objetivo,
        normaliza el contenido y estructura cada evento con formato uniforme.

        Args:
            rawData (pd.DataFrame): DataFrame con columnas esperadas: 
                'Program Start Date', 'Program Start Time', 'Program Title', 'Program Description'.
            defaultDescription (str): Descripción por defecto en caso de que el evento no tenga sinopsis.
            targetDate (str): (Actualmente ignorado) Fecha objetivo para filtrar eventos, formato 'YYYY-MM-DD'.

        Returns:
            list: Lista de eventos procesados. Cada elemento es un diccionario con:
                - 'date': Fecha del evento (str, formato 'YYYY-MM-DD').
                - 'hour': Hora de inicio del evento (str, formato 'HH:MM').
                - 'title': Título del programa (str).
                - 'content': Sinopsis del programa o descripción por defecto (str).
        """
        processedEvents = []

        for _, row in rawData.iterrows():
            try:
                rawDate = str(row.get("Program Start Date", "")).strip()
                rawHour = str(row.get("Program Start Time", "")).strip()
                eventTitle = str(row.get("Program Title", "")).strip()
                eventContent = str(row.get("Program Description", "")).strip() or defaultDescription

                if not rawDate or not rawHour or not eventTitle:
                    continue

                # Convertir a datetime (se espera formato mm/dd/yyyy HH:MM)
                eventStartDatetime = datetime.strptime(f"{rawDate} {rawHour}", "%m/%d/%Y %H:%M")
                
                # Aplicar zona horaria fuente
                localizedEventDatetime = self.sourceTimezone.localize(eventStartDatetime)
                
                # Convertir a zona horaria destino
                targetEventDatetime = localizedEventDatetime.astimezone(self.targetTimezone)

                # Formatear resultado
                eventDate = targetEventDatetime.strftime("%Y-%m-%d")
                eventTime = targetEventDatetime.strftime("%H:%M")

                processedEvents.append({
                    "date": eventDate,
                    "hour": eventTime,
                    "title": eventTitle,
                    "content": eventContent,
                })

            except Exception as e:
                print(f"[Error] Evento con error: {e}")
                continue

        return processedEvents
