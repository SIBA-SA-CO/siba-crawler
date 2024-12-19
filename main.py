from datetime import datetime
import argparse
from src.scrapers.bvn_tv import BvnTv
from src.scrapers.npo_client import NpoClient
from src.scrapers.me_tv_toons import MeTvToons
from src.scrapers.bet import Bet
from src.scrapers.my9 import My9

def main():

    
    replacements = {
        '&':'en',
        "'": "’",
        "“":'"',
        " \r\n":" ",
        "---": "-"
    }

    # Configuración del parser de argumentos
    parser = argparse.ArgumentParser(description="Scraper de programas de TV")
    parser.add_argument("--initial_date", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="Fecha inicial en formato YYYY-MM-DD")
    parser.add_argument("--days_range", type=int, default=15, help="Número de días antes y después de la fecha inicial a considerar")
    parser.add_argument("--channel", type=str, choices=["bvn","npo","metv","bet","my9"], required=True, help="El canal a scrapear: bvn, npo, metv, bet o my9")
    args = parser.parse_args()

    # Crear la instancia del scraper según el canal
    if args.channel == "bvn":
        scraper = BvnTv(base_url="https://www.bvn.tv/json/guide/")
    elif args.channel == "npo":
        scraper = NpoClient(base_url="https://npo.nl/start/api/domain/guide-channel?date=")
    elif args.channel == "metv":
        scraper = MeTvToons(base_url="https://metvtoons.com/schedule/")
    elif args.channel == "bet":
        scraper = Bet(base_url="https://www.bet.com/api/more/tvschedule/")
    elif args.channel == "my9":
        scraper = My9 (base_url="https://www.titantvguide.com/data/eventspage/52676/cb5977cf-30e2-4fe0-8052-023ba0063beb/")

    # Ejecutar el scraping, pasando el diccionario de reemplazos
    scraper.scrape_program_guide(args.initial_date, args.days_range, replacements)

if __name__ == "__main__":
    main()