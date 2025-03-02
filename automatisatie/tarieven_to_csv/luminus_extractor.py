import re
from utils import extract_text_from_pdf, extract_date_from_filename, get_end_date, logging


def extract_luminus_data(pdf_path):
    """Extraheert tariefgegevens uit Luminus tariefkaarten."""
    logging.info(f"Verwerken van Luminus tariefkaart: {pdf_path}")

    # Extract text and date
    text = extract_text_from_pdf(pdf_path)
    filename = pdf_path.split("/")[-1]
    date = extract_date_from_filename(filename)

    if not date:
        logging.error(f"Kon geen datum extraheren uit {filename}")
        return None

    # Initialiseer data dictionary
    data = {
        "leverancier": "LUMINUS",
        "product": "DYNAMIC",
        "contract_type": "dynamisch",  # Luminus Dynamic is een dynamisch contract
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
    vaste_vergoeding_match = re.search(r'Vaste vergoeding\s*\(\s*€\s*/\s*jaar\s*\)\s*(\d+[,.]\d+)', text, re.IGNORECASE)
    if vaste_vergoeding_match:
        data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
        logging.info(f"Gevonden vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
    else:
        logging.warning("Kon geen vaste vergoeding vinden")

    # Zoek meterfactor en balanceringskost voor afname
    afname_formula_match = re.search(r'Dag\s*\([^)]*\)\s*=\s*(\d+[,.]\d+)\s*[×x]\s*Belpex\s*H\s*\+\s*(\d+[,.]\d+)',
                                     text)
    if afname_formula_match:
        data["meterfactor_afname"] = afname_formula_match.group(1).replace(',', '.')
        data["balanceringskost_afname"] = afname_formula_match.group(2).replace(',', '.')
        data["index_type_afname"] = "Belpex H"
        logging.info(f"Gevonden meterfactor afname: {data['meterfactor_afname']}")
        logging.info(f"Gevonden balanceringskost afname: {data['balanceringskost_afname']}")
    else:
        logging.warning("Kon geen meterfactor en balanceringskost voor afname vinden")

    # Zoek meterfactor en balanceringskost voor injectie
    injectie_formula_match = re.search(r'Dag\s*\([^)]*\)\s*=\s*(\d+[,.]\d+)\s*[×x]\s*Belpex\s*H\s*-\s*(\d+[,.]\d+)',
                                       text)
    if injectie_formula_match:
        data["meterfactor_injectie"] = injectie_formula_match.group(1).replace(',', '.')
        data["balanceringskost_injectie"] = "-" + injectie_formula_match.group(2).replace(',', '.')  # Negatieve waarde
        data["index_type_injectie"] = "Belpex H"
        logging.info(f"Gevonden meterfactor injectie: {data['meterfactor_injectie']}")
        logging.info(f"Gevonden balanceringskost injectie: {data['balanceringskost_injectie']}")
    else:
        logging.warning("Kon geen meterfactor en balanceringskost voor injectie vinden")

    logging.info(f"Verwerking voltooid voor {pdf_path}")
    return data
