import re
from utils import extract_text_from_pdf, extract_date_from_filename, get_end_date, logging


def extract_bolt_data(pdf_path):
    """Extraheert tariefgegevens uit Bolt tariefkaarten."""
    logging.info(f"Processing Bolt tariff card: {pdf_path}")

    # Extract text and date
    text = extract_text_from_pdf(pdf_path)
    filename = pdf_path.split("/")[-1]
    date = extract_date_from_filename(filename)

    if not date:
        logging.error(f"Could not extract date from {filename}")
        return None

    # Determine product type
    product = "ELEKTRICITEIT" if "elektriciteit" in filename.lower() else "VAST"
    logging.info(f"Detected product: {product}")

    # Initialize data dictionary
    data = {
        "leverancier": "BOLT",
        "product": product,
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
    vaste_vergoeding_match = re.search(r'vaste vergoeding[^\d]*(\d+[,.]\d+)', text, re.IGNORECASE)
    if vaste_vergoeding_match:
        data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
        logging.info(f"Found vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
    else:
        logging.warning("Could not find vaste vergoeding")

    if "VAST" in product:
        # Logica voor vast contract
        data["contract_type"] = "vast"
        # Zoek vaste prijzen voor afname
        afname_match = re.search(r'afname[^\d]*(\d+[,.]\d+)', text, re.IGNORECASE)
        if afname_match:
            data["vaste_prijs_afname_eurocent_kwh"] = afname_match.group(1).replace(',', '.')
            logging.info(f"Found vaste prijs afname: {data['vaste_prijs_afname_eurocent_kwh']}")
        else:
            logging.warning("Could not find vaste prijs afname")

        # Zoek vaste prijzen voor injectie
        injectie_match = re.search(r'injectie[^\d]*(\d+[,.]\d+)', text, re.IGNORECASE)
        if injectie_match:
            data["vaste_prijs_injectie_eurocent_kwh"] = injectie_match.group(1).replace(',', '.')
            logging.info(f"Found vaste prijs injectie: {data['vaste_prijs_injectie_eurocent_kwh']}")
        else:
            logging.warning("Could not find vaste prijs injectie")
    else:
        # Logica voor variabel contract
        data["contract_type"] = "variabel"

        # Print a section of the text for debugging
        logging.debug(f"Text sample for regex matching: {text[:500]}...")

        # Zoek meterfactor en balanceringskost voor afname
        meterfactor_match = re.search(r'Belpex\s*\*\s*(\d+\.\d+)', text)
        if meterfactor_match:
            data["meterfactor_afname"] = meterfactor_match.group(1)
            data["index_type_afname"] = "BELPEX"
            logging.info(f"Found meterfactor afname: {data['meterfactor_afname']}")
        else:
            logging.warning("Could not find meterfactor afname")

        balanceringskost_match = re.search(r'\+\s*(\d+\.\d+)', text)
        if balanceringskost_match:
            data["balanceringskost_afname"] = balanceringskost_match.group(1)
            logging.info(f"Found balanceringskost afname: {data['balanceringskost_afname']}")
        else:
            logging.warning("Could not find balanceringskost afname")

        # Zoek meterfactor en balanceringskost voor injectie
        injectie_match = re.search(r'Injectie[^\n]*Belpex\s*\*\s*(\d+\.\d+)', text, re.IGNORECASE)
        if injectie_match:
            data["meterfactor_injectie"] = injectie_match.group(1)
            data["index_type_injectie"] = "BELPEX"
            logging.info(f"Found meterfactor injectie: {data['meterfactor_injectie']}")
        else:
            logging.warning("Could not find meterfactor injectie")

    logging.info(f"Completed processing for {pdf_path}")
    return data
