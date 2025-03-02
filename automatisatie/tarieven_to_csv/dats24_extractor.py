import re
from utils import extract_text_from_pdf, extract_date_from_filename, get_end_date, logging

def extract_dats24_data(pdf_path):
    """Extraheert tariefgegevens uit DATS24 tariefkaarten."""
    logging.info(f"Processing DATS24 tariff card: {pdf_path}")

    # Extract text and date
    text = extract_text_from_pdf(pdf_path)
    filename = pdf_path.split("/")[-1]
    date = extract_date_from_filename(filename)

    if not date:
        logging.error(f"Could not extract date from {filename}")
        return None

    # Initialize data dictionary
    data = {
        "leverancier": "DATS24",
        "product": "ELEKTRICITEIT",
        "contract_type": "variabel",  # DATS24 heeft variabele tarieven
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

    # Extract vaste vergoeding
    vaste_vergoeding_match = re.search(r'Vaste vergoeding[^\d]*(\d+[,.]\d+)', text, re.IGNORECASE)
    if vaste_vergoeding_match:
        data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
        logging.info(f"Found vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
    else:
        logging.warning("Could not find vaste vergoeding")

    # Voor variabel contract - zoek meterfactor en balanceringskost voor afname
    # DATS24 formule: (BE_spotRLP × 0,1084+0,697)+6% btw
    meterfactor_match = re.search(r'BE_spotRLP\s*[×x\*]\s*(\d+[,.]\d+)', text)
    if meterfactor_match:
        data["meterfactor_afname"] = meterfactor_match.group(1).replace(',', '.')
        data["index_type_afname"] = "BE_spotRLP"
        logging.info(f"Found meterfactor afname: {data['meterfactor_afname']}")
    else:
        logging.warning("Could not find meterfactor afname")

    balanceringskost_match = re.search(r'[+]\s*(\d+[,.]\d+)', text)
    if balanceringskost_match:
        data["balanceringskost_afname"] = balanceringskost_match.group(1).replace(',', '.')
        logging.info(f"Found balanceringskost afname: {data['balanceringskost_afname']}")
    else:
        logging.warning("Could not find balanceringskost afname")

    # Zoek meterfactor en balanceringskost voor injectie
    # DATS24 formule: (BE_spotSPP × 0,073-0,38)
    injectie_meterfactor_match = re.search(r'BE_spotSPP\s*[×x\*]\s*(\d+[,.]\d+)', text)
    if injectie_meterfactor_match:
        data["meterfactor_injectie"] = injectie_meterfactor_match.group(1).replace(',', '.')
        data["index_type_injectie"] = "BE_spotSPP"
        logging.info(f"Found meterfactor injectie: {data['meterfactor_injectie']}")
    else:
        logging.warning("Could not find meterfactor injectie")

    injectie_balanceringskost_match = re.search(r'[-]\s*(\d+[,.]\d+)', text)
    if injectie_balanceringskost_match:
        # Negatieve waarde voor injectie balanceringskost
        data["balanceringskost_injectie"] = "-" + injectie_balanceringskost_match.group(1).replace(',', '.')
        logging.info(f"Found balanceringskost injectie: {data['balanceringskost_injectie']}")
    else:
        logging.warning("Could not find balanceringskost injectie")

    logging.info(f"Completed processing for {pdf_path}")
    return data
