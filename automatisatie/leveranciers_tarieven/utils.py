import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

def download_pdf(url, output_path):
    """Download een PDF-bestand van de gegeven URL en sla het op op het gegeven pad."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Gedownload: {output_path}")
        return True
    except Exception as e:
        print(f"Fout bij het downloaden van {url}: {e}")
        return False

def extract_date_from_title(title):
    """Extraheer de datum uit de titel van een tariefkaart."""
    months = {
        'januari': '01', 'februari': '02', 'maart': '03', 'april': '04', 'mei': '05', 'juni': '06',
        'juli': '07', 'augustus': '08', 'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
    }

    # Zoek naar patronen zoals "Januari 2023" of "januari-2023"
    pattern = r'(?i)(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)[- ](\d{4})'
    match = re.search(pattern, title)

    if match:
        month_name = match.group(1).lower()
        year = match.group(2)
        month = months.get(month_name)
        if month and year:
            return f"{year}-{month}-01"

    return None

def get_product_links(base_url, supplier_path):
    """Haal alle product links op voor een specifieke leverancier."""
    url = f"{base_url}{supplier_path}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_links = []
    for a_tag in soup.find_all('a', href=True):
        if supplier_path in a_tag['href'] and a_tag['href'] != supplier_path:
            product_links.append(a_tag['href'])

    return list(set(product_links))
