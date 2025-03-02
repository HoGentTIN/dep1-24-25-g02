import re
from utils import extract_text_from_pdf, extract_date_from_filename, get_end_date, logging


def extract_energiebe_data(pdf_path):
    """Extraheert tariefgegevens uit Energie-BE tariefkaarten."""
    logging.info(f"Verwerken van Energie-BE tariefkaart: {pdf_path}")

    # Extract text and date
    text = extract_text_from_pdf(pdf_path)
    filename = pdf_path.split("/")[-1]
    date = extract_date_from_filename(filename)

    if not date:
        logging.error(f"Kon geen datum extraheren uit {filename}")
        return None

    # Bepaal product type en contract type
    product = "VARIABEL" if "variabel" in filename.lower() else "VAST"
    contract_type = "variabel" if "variabel" in filename.lower() else "vast"

    logging.info(f"Gedetecteerd product: {product}, contract type: {contract_type}")

    # Initialize data dictionary
    data = {
        "leverancier": "ENERGIE-BE",
        "product": product,
        "contract_type": contract_type,
        "vanaf_datum": date,
        "tot_datum": get_end_date(date),
        "vaste_vergoeding_euro_jaar": "",
        "vaste_prijs_afname_eurocent_kwh": "",
        "meterfactor_afname": "",
        "balanceringskost_afname": "",
        "index_type_afname": "",
        "vaste_prijs_injectie_eurocent_kwh": "",
        "meterfactor_injectie": "",
        "balanceringskost_injectie": "",
        "index_type_injectie": ""
    }

    # Extract vaste vergoeding (abonnementskost)
    abonnement_match = re.search(r'Abonnements-\s*kost\s*[€\s]*(\d+)', text)
    if abonnement_match:
        data["vaste_vergoeding_euro_jaar"] = abonnement_match.group(1)
        logging.info(f"Vaste vergoeding gevonden: {data['vaste_vergoeding_euro_jaar']}")
    else:
        logging.warning("Kon geen vaste vergoeding vinden")

    if contract_type == "vast":
        # Voor vast contract - zoek vaste prijs voor afname
        energieprijs_match = re.search(r'Energieprijs\s*\(\s*c€\s*/\s*kWh\s*\)\s*(\d+[,.]\d+)', text)
        if energieprijs_match:
            data["vaste_prijs_afname_eurocent_kwh"] = energieprijs_match.group(1).replace(',', '.')
            logging.info(f"Vaste prijs afname gevonden: {data['vaste_prijs_afname_eurocent_kwh']}")
        else:
            logging.warning("Kon geen vaste prijs afname vinden")

    else:  # variabel contract
        # Zoek meterfactor en balanceringskost voor afname
        # Energie-BE formule: 1,058 x Belpex_RLP + €12/MWh
        meterfactor_match = re.search(r'(\d+[,.]\d+)\s*x\s*Belpex_RLP', text)
        if meterfactor_match:
            data["meterfactor_afname"] = meterfactor_match.group(1).replace(',', '.')
            data["index_type_afname"] = "Belpex_RLP"
            logging.info(f"Meterfactor afname gevonden: {data['meterfactor_afname']}")
        else:
            logging.warning("Kon geen meterfactor afname vinden")

        balanceringskost_match = re.search(r'\+\s*€(\d+)/MWh', text)
        if balanceringskost_match:
            # Converteer van €/MWh naar c€/kWh
            balanceringskost_mwh = float(balanceringskost_match.group(1))
            balanceringskost_kwh = balanceringskost_mwh / 10  # €/MWh naar c€/kWh
            data["balanceringskost_afname"] = str(balanceringskost_kwh)
            logging.info(f"Balanceringskost afname gevonden: {data['balanceringskost_afname']}")
        else:
            logging.warning("Kon geen balanceringskost afname vinden")

        # Zoek terugleveringsvergoeding (injectie)
        # Energie-BE formule: 0,80 × Belpex_SPP - €5/MWh
        injectie_meterfactor_match = re.search(r'(\d+[,.]\d+)\s*[×x\*]\s*Belpex_SPP', text)
        if injectie_meterfactor_match:
            data["meterfactor_injectie"] = injectie_meterfactor_match.group(1).replace(',', '.')
            data["index_type_injectie"] = "Belpex_SPP"
            logging.info(f"Meterfactor injectie gevonden: {data['meterfactor_injectie']}")
        else:
            logging.warning("Kon geen meterfactor injectie vinden")

        injectie_balanceringskost_match = re.search(r'-\s*€(\d+)/MWh', text)
        if injectie_balanceringskost_match:
            # Converteer van €/MWh naar c€/kWh en zet negatief
            balanceringskost_mwh = float(injectie_balanceringskost_match.group(1))
            balanceringskost_kwh = balanceringskost_mwh / 10  # €/MWh naar c€/kWh
            data["balanceringskost_injectie"] = "-" + str(balanceringskost_kwh)
            logging.info(f"Balanceringskost injectie gevonden: {data['balanceringskost_injectie']}")
        else:
            logging.warning("Kon geen balanceringskost injectie vinden")

        # Voor variabel contract, zoek ook naar de vaste injectieprijs indien aanwezig
        injectie_prijs_match = re.search(r'Zonnestroom\s*\(\s*c€\s*/\s*kWh\s*\)\s*(\d+[,.]\d+)', text)
        if injectie_prijs_match:
            data["vaste_prijs_injectie_eurocent_kwh"] = injectie_prijs_match.group(1).replace(',', '.')
            logging.info(f"Vaste prijs injectie gevonden: {data['vaste_prijs_injectie_eurocent_kwh']}")

    logging.info(f"Verwerking voltooid voor {pdf_path}")
    return data
