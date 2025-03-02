import os
from datetime import datetime
import urllib.parse
from bs4 import BeautifulSoup
import requests
from utils import download_pdf, extract_date_from_title

def download_tariff_cards(base_url, product_url, supplier_name, product_name, from_date, output_dir):
    """Download alle tariefkaarten voor een specifiek product vanaf een bepaalde datum."""
    # Zorg ervoor dat de URL correct wordt opgebouwd
    if product_url.startswith('http'):
        url = product_url
    else:
        url = f"{base_url}{product_url}"

    print(f"Downloaden van URL: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Maak de output directory als deze nog niet bestaat
    supplier_dir = os.path.join(output_dir, supplier_name)
    if not os.path.exists(supplier_dir):
        os.makedirs(supplier_dir)

    product_dir = os.path.join(supplier_dir, product_name)
    if not os.path.exists(product_dir):
        os.makedirs(product_dir)

    # Converteer from_date naar datetime object
    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")

    # Zoek alle PDF links
    pdf_links = []
    for a_tag in soup.find_all('a', href=True):
        if a_tag['href'].endswith('.pdf'):
            title = a_tag.get('title', '') or os.path.basename(a_tag['href'])
            date_str = extract_date_from_title(title)

            # Speciale gevallen voor TotalEnergies producten
            is_target_product = False

            # Voor Pixel eDrive
            if product_name == "PIXEL EDRIVE" and (
                    'emobility' in a_tag['href'].lower() or 'edrive' in a_tag['href'].lower()):
                is_target_product = True

            # Voor Pixel Next Vast (check zowel 'next-vast' als 'blue-fixed')
            elif product_name == "PIXEL NEXT VAST" and (
                    'next-vast' in a_tag['href'].lower() or
                    'blue-fixed' in a_tag['href'].lower() or
                    'pixel-next' in a_tag['href'].lower() or
                    'pixel-blue' in a_tag['href'].lower()
            ):
                is_target_product = True

            # Voor andere producten
            elif product_name.lower().replace(' ', '-') in a_tag['href'].lower() or product_name.lower().replace(' & ', '-') in a_tag['href'].lower():
                is_target_product = True

            if is_target_product and date_str:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj >= from_date_obj:
                    pdf_links.append({
                        'url': a_tag['href'],
                        'date': date_str,
                        'title': title
                    })

    # Download de PDFs
    downloaded_count = 0
    for pdf in pdf_links:
        pdf_url = pdf['url']
        if not pdf_url.startswith('http'):
            pdf_url = urllib.parse.urljoin(base_url, pdf_url)

        date_parts = pdf['date'].split('-')
        year = date_parts[0]
        month = date_parts[1]

        # Bepaal de bestandsnaam
        filename = f"{supplier_name.lower()}-{product_name.lower().replace(' ', '-').replace('&', 'en')}-{year}-{month}.pdf"
        pdf_path = os.path.join(product_dir, filename)

        # Download het bestand
        if download_pdf(pdf_url, pdf_path):
            downloaded_count += 1

    return downloaded_count
