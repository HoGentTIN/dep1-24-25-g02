import os
from config import BASE_URL, OUTPUT_DIR, SUPPLIERS
from utils import get_product_links
from downloader import download_tariff_cards


def download_all_required_tariffs():
    """Download alle vereiste tariefkaarten voor het project."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    total_downloaded = 0

    for supplier in SUPPLIERS:
        print(f"\nVerwerken van leverancier: {supplier['name']}...")

        # Haal alle product links op
        product_links = get_product_links(BASE_URL, supplier['path'])

        for product in supplier['products']:
            product_name = product['name']
            from_date = product['from_date']

            print(f"  Zoeken naar tariefkaarten voor {product_name} vanaf {from_date}...")

            # Gebruik specifieke URL indien opgegeven
            if "specific_url" in product:
                product_url = product["specific_url"]
                print(f"  Gebruik specifieke URL: {product_url}")
            else:
                # Zoek de juiste product URL
                product_url = None
                for link in product_links:
                    if product_name.lower().replace(' ', '-') in link.lower() or product_name.lower().replace(' & ',
                                                                                                              '-') in link.lower():
                        product_url = link
                        break

            if product_url:
                count = download_tariff_cards(BASE_URL, product_url, supplier['name'], product_name, from_date,
                                              OUTPUT_DIR)
                total_downloaded += count
                print(f"  {count} tariefkaarten gedownload voor {supplier['name']} {product_name}")
            else:
                print(f"  Geen product URL gevonden voor {supplier['name']} {product_name}")

    print(f"\nTotaal aantal gedownloade tariefkaarten: {total_downloaded}")


if __name__ == "__main__":
    download_all_required_tariffs()
