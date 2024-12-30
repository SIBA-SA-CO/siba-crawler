# Configuración de canales
CHANNELS = {
    "gameshownetwork": {
        "file_name": "Game Show Network - US",
        "url": "https://www.gameshownetwork.com/schedule",
        "default_description": "Program Game Show Network",
        "output_path": "./data/gameshow/"
    },
    "my9": {
        "file_name": "MY9 TV - US",
        "url": "https://www.titantvguide.com/data/eventspage/52676/cb5977cf-30e2-4fe0-8052-023ba0063beb/",
        "default_description": "Programma My9",
        "output_path": "./data/my9/"
    },
    "bet": {
        "file_name": "BET - US",
        "url": "https://www.bet.com/api/more/tvschedule/",
        "default_description": "Programma Bet",
        "output_path": "./data/bet/"
    },
    "bvntv": {
        "file_name": "BVN TV - NL",
        "url": "https://www.bvn.tv/json/guide/",
        "default_description": "Programma BVN",
        "output_path": "./data/bvn/"
    },
    "metvtoons": {
        "file_name": "METV TOONS - US",
        "url": "https://metvtoons.com/schedule/",
        "default_description": "Program MeTvToons",
        "output_path": "./data/metvtoons/"
    },
    "npoclient": {
        "url": "https://npo.nl/start/api/domain/guide-channel?date=",
        "output_path": "./data/npo/",
        "sub_channels": [
            {
                "id": "2042e1ee-0e79-4766-aea2-5b300d6839b2",
                "file_name": "NPO3 - NL",
                "default_description": "Programma NPO3",

            },
            {
                "id": "316951f5-ce06-41d2-ae24-44eb25368a61",
                "file_name": "NPO2 - NL",
                "default_description": "Programma NPO2",

            },
            {
                "id": "83dc1f25-a065-496c-9418-bd5c60dfb36d",
                "file_name": "NPO1 - NL",
                "default_description": "Programma NPO1",
            }
        ]
    }
}
