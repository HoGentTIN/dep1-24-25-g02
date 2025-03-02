# Configuratie voor het downloaden van tariefkaarten

# Basis URL voor de website
BASE_URL = "https://www.durfbesparen.be"

# Map voor het opslaan van tariefkaarten
OUTPUT_DIR = "tariefkaarten"

# Lijst van leveranciers en hun producten
SUPPLIERS = [
    {
        "name": "BOLT",
        "path": "/energie/tariefkaarten/1-bolt",
        "products": [
            {"name": "ELEKTRICITEIT", "from_date": "2023-01-01"},
            {"name": "VAST", "from_date": "2024-01-01"}
        ]
    },
    {
        "name": "DATS24",
        "path": "/energie/tariefkaarten/1-dats-24",
        "products": [
            {"name": "ELEKTRICITEIT", "from_date": "2023-01-01"}
        ]
    },
    {
        "name": "ENECO",
        "path": "/energie/tariefkaarten/1-eneco",
        "products": [
            {"name": "ZON & WIND FLEX", "from_date": "2023-01-01"}
        ]
    },
    {
        "name": "ENERGIE-BE",
        "path": "/energie/tariefkaarten/1-energie-be",
        "products": [
            {"name": "VARIABEL", "from_date": "2023-01-01", "specific_url": "/energie/tariefkaarten/1-energie-be/1-4452-variabel"},
            {"name": "VAST", "from_date": "2024-01-01"}
        ]
    },
    {
        "name": "LUMINUS",
        "path": "/energie/tariefkaarten/1-luminus",
        "products": [
            {"name": "DYNAMIC", "from_date": "2024-04-01"}
        ]
    },
    {
        "name": "OCTA+",
        "path": "/energie/tariefkaarten/1-octa",
        "products": [
            {"name": "DYNAMIC", "from_date": "2023-05-01"},
            {"name": "ECO CLEAR", "from_date": "2023-01-01", "specific_url": "/energie/tariefkaarten/1-octa/1-7062-eco-clear"},
            {"name": "FIXED", "from_date": "2023-08-01", "specific_url": "/energie/tariefkaarten/1-octa/1-7601-fixed"},
            {"name": "SMART VARIABEL", "from_date": "2023-01-01", "specific_url": "/energie/tariefkaarten/1-octa/1-3126-smart-variabel"}
        ]
    },
    {
        "name": "TOTALENERGIES",
        "path": "/energie/tariefkaarten/1-totalenergies",
        "products": [
            {"name": "PIXEL", "from_date": "2023-01-01", "specific_url": "/energie/tariefkaarten/1-totalenergies/1-6838-pixel"},
            {"name": "PIXEL NEXT VAST", "from_date": "2023-08-01", "specific_url": "/energie/tariefkaarten/1-totalenergies/1-6840-pixel-next"},
            {"name": "PIXEL EDRIVE", "from_date": "2023-01-01", "specific_url": "/energie/tariefkaarten/1-totalenergies/1-6004-pixel-edrive"},
            {"name": "PIXIE", "from_date": "2024-06-01", "specific_url": "/energie/tariefkaarten/1-totalenergies/1-8302-pixie"},
        ]
    }
]
