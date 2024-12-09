from datetime import datetime
import argparse
from src.scrapers.bvn_tv import BvnTv
from src.scrapers.npo_client import NpoClient

def main():

    
    replacements = {
        '&':'en',
        "'": "’"
    }

    # Configuración del parser de argumentos
    parser = argparse.ArgumentParser(description="Scraper de programas de TV")
    parser.add_argument("--initial_date", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="Fecha inicial en formato YYYY-MM-DD")
    parser.add_argument("--days_range", type=int, default=15, help="Número de días antes y después de la fecha inicial a considerar")
    parser.add_argument("--channel", type=str, choices=["bvn","npo"], required=True, help="El canal a scrapear: bvn o npo")
    args = parser.parse_args()

    # Crear la instancia del scraper según el canal
    if args.channel == "bvn":
        scraper = BvnTv(base_url="https://www.bvn.tv/json/guide/")
    else:
        scraper = NpoClient(base_url="https://npo.nl/start/api/domain/guide-channel?date=")

    # Ejecutar el scraping, pasando el diccionario de reemplazos
    scraper.scrape_program_guide(args.initial_date, args.days_range, replacements)

if __name__ == "__main__":
    main()