# main.py
from datetime import datetime
import argparse
from src.config import CHANNELS
from src.scrapers import discover_scrapers

def main():
    replacements = {
        '&': 'en',
        "'": "’",
        "“": '"',
        " \r\n": " ",
        "---": "-",
        '\n': ' ',
        '': "’", 
        '': '-',  
        '': '"',  
        '': '"',
    }

    # Configuración del parser de argumentos
    parser = argparse.ArgumentParser(description="Scraper de programas de TV")
    parser.add_argument("--initial_date", type=str, default=datetime.now().strftime("%Y-%m-%d"),
                        help="Fecha inicial en formato YYYY-MM-DD")
    parser.add_argument("--days_range", type=int, default=15, help="Número de días antes y después de la fecha inicial a considerar")
    parser.add_argument("--channel", type=str, choices=CHANNELS.keys(), required=True,
                        help=f"El canal a scrapear: {', '.join(CHANNELS.keys())}")
    args = parser.parse_args()

    # Descubre los scrapers dinámicamente
    scrapers = discover_scrapers()

    # Busca el scraper correspondiente al canal
    scraper_class = scrapers.get(args.channel)
    if not scraper_class:
        raise ValueError(f"No se encontró un scraper para el canal: {args.channel}")

    # Inicializa el scraper
    scraper = scraper_class(CHANNELS[args.channel])

    # Ejecutar el scraping, pasando el diccionario de reemplazos
    scraper.scrape_program_guide(args.initial_date, args.days_range, replacements)

if __name__ == "__main__":
    main()
