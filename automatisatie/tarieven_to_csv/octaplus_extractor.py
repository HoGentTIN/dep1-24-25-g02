import re
import os
from utils import extract_text_from_pdf, extract_date_from_filename, get_end_date, logging


def extract_octaplus_eco_clear_data(text, filename, date):
    """
    Extraheert tariefgegevens specifiek voor OCTA+ ECO CLEAR tariefkaarten.

    Args:
        text: Geëxtraheerde tekst uit de PDF
        filename: Bestandsnaam van de PDF
        date: Geëxtraheerde datum uit de bestandsnaam

    Returns:
        Dictionary met geëxtraheerde tariefgegevens
    """
    logging.info(f"Verwerken van OCTA+ ECO CLEAR tariefkaart: {filename}")

    # Initialiseer data dictionary
    data = {
        "leverancier": "OCTA+",
        "product": "ECO CLEAR",
        "contract_type": "variabel",
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
    vaste_vergoeding_patterns = [
        r'Vaste vergoeding[^\d]*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€ [Jj]aar\)\s*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Abonnement \(€\/jaar\)\s*(\d+[,.]\d+)'
    ]

    for pattern in vaste_vergoeding_patterns:
        vaste_vergoeding_match = re.search(pattern, text, re.IGNORECASE)
        if vaste_vergoeding_match:
            data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
            logging.info(f"Gevonden vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
            break

    # Zoek naar formule voor afname
    afname_patterns = [
        r'Enkelvoudige meter\s*:\s*Belpex\s*RLP\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+)',
        r'Belpex\s*RLP\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+)',
        r'Enkelvoudige meter\s*:\s*(\d+[,.]\d+)\s*\*\s*Belpex\s*RLP\s*\+\s*(\d+)'
    ]

    for pattern in afname_patterns:
        afname_formula_match = re.search(pattern, text, re.IGNORECASE)
        if afname_formula_match:
            data["meterfactor_afname"] = afname_formula_match.group(1).replace(',', '.')
            data["balanceringskost_afname"] = afname_formula_match.group(2)
            data["index_type_afname"] = "Belpex RLP"
            logging.info(f"Gevonden meterfactor afname: {data['meterfactor_afname']}")
            logging.info(f"Gevonden balanceringskost afname: {data['balanceringskost_afname']}")
            break

    # Zoek naar formule voor injectie
    injectie_patterns = [
        r'Belpex\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'injectie.*?Belpex\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'enkelvoudig\s*:\s*Belpex\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)'
    ]

    for pattern in injectie_patterns:
        injectie_formula_match = re.search(pattern, text, re.IGNORECASE)
        if injectie_formula_match:
            data["meterfactor_injectie"] = injectie_formula_match.group(1).replace(',', '.')
            data["balanceringskost_injectie"] = "-" + injectie_formula_match.group(2).replace(',', '.')
            data["index_type_injectie"] = "Belpex"
            logging.info(f"Gevonden meterfactor injectie: {data['meterfactor_injectie']}")
            logging.info(f"Gevonden balanceringskost injectie: {data['balanceringskost_injectie']}")
            break

    logging.info(f"Verwerking voltooid voor ECO CLEAR product")
    return data


def extract_octaplus_fixed_data(text, filename, date):
    """
    Extraheert tariefgegevens specifiek voor OCTA+ FIXED tariefkaarten.

    Args:
        text: Geëxtraheerde tekst uit de PDF
        filename: Bestandsnaam van de PDF
        date: Geëxtraheerde datum uit de bestandsnaam

    Returns:
        Dictionary met geëxtraheerde tariefgegevens
    """
    logging.info(f"Verwerken van OCTA+ FIXED tariefkaart: {filename}")

    # Initialiseer data dictionary
    data = {
        "leverancier": "OCTA+",
        "product": "FIXED",
        "contract_type": "vast",
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
    vaste_vergoeding_patterns = [
        r'Vaste vergoeding[^\d]*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€ [Jj]aar\)\s*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Vaste verg[^\d]*(\d+[,.]\d+)'
    ]

    for pattern in vaste_vergoeding_patterns:
        vaste_vergoeding_match = re.search(pattern, text, re.IGNORECASE)
        if vaste_vergoeding_match:
            data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
            logging.info(f"Gevonden vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
            break

    # Zoek vaste prijs voor afname (enkelvoudige meter)
    afname_patterns = [
        r'Enkelvoudige meter\s*(\d+[,.]\d+)',
        r'Enkelvoudige meter\s*:\s*(\d+[,.]\d+)',
        r'Energieprijzen[^\n]*Enkelvoudige meter\s*(\d+[,.]\d+)',
        r'Energieprijs[^\n]*Enkelvoudige meter\s*(\d+[,.]\d+)',
        r'Maandelijkse prijzen[^\n]*(\d+[,.]\d+)',
        r'Vast\s*(\d+[,.]\d+)',
        r'Energieprijzen\s*Vast\s*(\d+[,.]\d+)'
    ]

    for pattern in afname_patterns:
        afname_match = re.search(pattern, text, re.IGNORECASE)
        if afname_match:
            data["vaste_prijs_afname_eurocent_kwh"] = afname_match.group(1).replace(',', '.')
            logging.info(f"Gevonden vaste prijs afname: {data['vaste_prijs_afname_eurocent_kwh']}")
            break

    # Als we nog steeds geen vaste prijs hebben, zoek dan in de tabel
    if not data["vaste_prijs_afname_eurocent_kwh"]:
        # Probeer de prijs te vinden in de tabel
        table_patterns = [
            r'Enkelvoudige meter[^\n]*?(\d+[,.]\d+)',
            r'Vast[^\n]*?(\d+[,.]\d+)'
        ]

        for pattern in table_patterns:
            table_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if table_match:
                data["vaste_prijs_afname_eurocent_kwh"] = table_match.group(1).replace(',', '.')
                logging.info(f"Gevonden vaste prijs afname in tabel: {data['vaste_prijs_afname_eurocent_kwh']}")
                break

    # Als laatste redmiddel, zoek naar getallen die lijken op een vaste prijs
    if not data["vaste_prijs_afname_eurocent_kwh"]:
        # Zoek naar getallen tussen 10 en 30 die niet al ergens anders gebruikt zijn
        price_matches = re.findall(r'(\d+[,.]\d+)', text)
        for price in price_matches:
            price_float = float(price.replace(',', '.'))
            if 10 <= price_float <= 30 and price != data["vaste_vergoeding_euro_jaar"]:
                data["vaste_prijs_afname_eurocent_kwh"] = price.replace(',', '.')
                logging.info(f"Gevonden mogelijke vaste prijs afname: {data['vaste_prijs_afname_eurocent_kwh']}")
                break

    # Zoek vaste prijs voor injectie
    injectie_patterns = [
        r'Injectie[^\n]*Enkelvoudige meter\s*(\d+[,.]\d+)',
        r'Injectie[^\n]*Vast\s*(\d+[,.]\d+)'
    ]

    for pattern in injectie_patterns:
        injectie_match = re.search(pattern, text, re.IGNORECASE)
        if injectie_match:
            data["vaste_prijs_injectie_eurocent_kwh"] = injectie_match.group(1).replace(',', '.')
            logging.info(f"Gevonden vaste prijs injectie: {data['vaste_prijs_injectie_eurocent_kwh']}")
            break

    # Als we geen vaste prijs voor injectie vinden, zoek dan naar de formule
    if not data["vaste_prijs_injectie_eurocent_kwh"]:
        injectie_formula_patterns = [
            r'injectie.*?Belpex\s*M\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
            r'enkelvoudig\s*:\s*Belpex\s*M\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)'
        ]

        for pattern in injectie_formula_patterns:
            injectie_formula_match = re.search(pattern, text, re.IGNORECASE)
            if injectie_formula_match:
                data["meterfactor_injectie"] = injectie_formula_match.group(1).replace(',', '.')
                data["balanceringskost_injectie"] = "-" + injectie_formula_match.group(2).replace(',', '.')
                data["index_type_injectie"] = "Belpex M"
                logging.info(f"Gevonden meterfactor injectie: {data['meterfactor_injectie']}")
                logging.info(f"Gevonden balanceringskost injectie: {data['balanceringskost_injectie']}")
                break

    logging.info(f"Verwerking voltooid voor FIXED product")
    return data


def extract_octaplus_dynamic_data(text, filename, date):
    """
    Extraheert tariefgegevens specifiek voor OCTA+ DYNAMIC tariefkaarten.

    Args:
        text: Geëxtraheerde tekst uit de PDF
        filename: Bestandsnaam van de PDF
        date: Geëxtraheerde datum uit de bestandsnaam

    Returns:
        Dictionary met geëxtraheerde tariefgegevens
    """
    logging.info(f"Verwerken van OCTA+ DYNAMIC tariefkaart: {filename}")

    # Initialiseer data dictionary
    data = {
        "leverancier": "OCTA+",
        "product": "DYNAMIC",
        "contract_type": "dynamisch",
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
    # Probeer verschillende patronen voor vaste vergoeding
    vaste_vergoeding_patterns = [
        r'Vaste vergoeding[^\d]*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€ [Jj]aar\)\s*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€\)\s*(\d+[,.]\d+)',
        r'Abonnement \(€\/jaar\)\s*(\d+[,.]\d+)'
    ]

    for pattern in vaste_vergoeding_patterns:
        vaste_vergoeding_match = re.search(pattern, text, re.IGNORECASE)
        if vaste_vergoeding_match:
            data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
            logging.info(f"Gevonden vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
            break

    if not data["vaste_vergoeding_euro_jaar"]:
        logging.warning("Kon geen vaste vergoeding vinden")

    # Zoek naar formule voor afname
    # Probeer verschillende patronen voor de afname formule
    afname_patterns = [
        r'Belpex Hourly \* (\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
        r'Belpex\s*Hourly\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
        r'Belpex\s*H\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
        r'Enkelvoudige meter\s*:\s*Belpex\s*Hourly\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
        r'Enkelvoudige meter\s*:\s*(\d+[,.]\d+)\s*\*\s*Belpex\s*Hourly\s*\+\s*(\d+[,.]\d+)'
    ]

    for pattern in afname_patterns:
        afname_formula_match = re.search(pattern, text, re.IGNORECASE)
        if afname_formula_match:
            data["meterfactor_afname"] = afname_formula_match.group(1).replace(',', '.')
            data["balanceringskost_afname"] = afname_formula_match.group(2).replace(',', '.')
            data["index_type_afname"] = "Belpex Hourly"
            logging.info(f"Gevonden meterfactor afname: {data['meterfactor_afname']}")
            logging.info(f"Gevonden balanceringskost afname: {data['balanceringskost_afname']}")
            break

    if not data["meterfactor_afname"]:
        logging.warning("Kon geen meterfactor en balanceringskost voor afname vinden")

    # Zoek naar formule voor injectie
    # Probeer verschillende patronen voor de injectie formule
    injectie_patterns = [
        r'Belpex Hourly \* (\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'Belpex\s*Hourly\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'Belpex\s*H\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'Injectie\s*:\s*Belpex\s*Hourly\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'Injectie\s*:\s*(\d+[,.]\d+)\s*\*\s*Belpex\s*Hourly\s*\-\s*(\d+[,.]\d+)'
    ]

    for pattern in injectie_patterns:
        injectie_formula_match = re.search(pattern, text, re.IGNORECASE)
        if injectie_formula_match:
            data["meterfactor_injectie"] = injectie_formula_match.group(1).replace(',', '.')
            data["balanceringskost_injectie"] = "-" + injectie_formula_match.group(2).replace(',', '.')
            data["index_type_injectie"] = "Belpex Hourly"
            logging.info(f"Gevonden meterfactor injectie: {data['meterfactor_injectie']}")
            logging.info(f"Gevonden balanceringskost injectie: {data['balanceringskost_injectie']}")
            break

    if not data["meterfactor_injectie"]:
        logging.warning("Kon geen meterfactor en balanceringskost voor injectie vinden")

    logging.info(f"Verwerking voltooid voor DYNAMIC product")
    return data


def extract_octaplus_smart_variabel_data(text, filename, date):
    """
    Extraheert tariefgegevens specifiek voor OCTA+ SMART VARIABEL tariefkaarten.

    Args:
        text: Geëxtraheerde tekst uit de PDF
        filename: Bestandsnaam van de PDF
        date: Geëxtraheerde datum uit de bestandsnaam

    Returns:
        Dictionary met geëxtraheerde tariefgegevens
    """
    logging.info(f"Verwerken van OCTA+ SMART VARIABEL tariefkaart: {filename}")

    # Initialiseer data dictionary
    data = {
        "leverancier": "OCTA+",
        "product": "SMART VARIABEL",
        "contract_type": "variabel",
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
    vaste_vergoeding_patterns = [
        r'Vaste vergoeding[^\d]*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€ [Jj]aar\)\s*(\d+[,.]\d+)',
        r'Vaste vergoeding \(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Abonnement \(€\/jaar\)\s*(\d+[,.]\d+)'
    ]

    for pattern in vaste_vergoeding_patterns:
        vaste_vergoeding_match = re.search(pattern, text, re.IGNORECASE)
        if vaste_vergoeding_match:
            data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
            logging.info(f"Gevonden vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
            break

    # Zoek naar formule voor afname
    afname_patterns = [
        r'Enkelvoudige meter\s*:\s*Belpex\s*RLP\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+)',
        r'Enkelvoudige meter\s*:\s*(\d+[,.]\d+)\s*\*\s*Belpex\s*RLP\s*\+\s*(\d+)',
        r'Enkelvoudige meter[^\n]*Belpex RLP \* (\d+[,.]\d+)\s*\+\s*(\d+)'
    ]

    for pattern in afname_patterns:
        afname_formula_match = re.search(pattern, text, re.IGNORECASE)
        if afname_formula_match:
            data["meterfactor_afname"] = afname_formula_match.group(1).replace(',', '.')
            data["balanceringskost_afname"] = afname_formula_match.group(2)
            data["index_type_afname"] = "Belpex RLP"
            logging.info(f"Gevonden meterfactor afname: {data['meterfactor_afname']}")
            logging.info(f"Gevonden balanceringskost afname: {data['balanceringskost_afname']}")
            break

    # Zoek naar formule voor injectie
    injectie_patterns = [
        r'Belpex\s*M\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'injectie.*?Belpex\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
        r'enkelvoudig\s*:\s*Belpex\s*M\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)'
    ]

    for pattern in injectie_patterns:
        injectie_formula_match = re.search(pattern, text, re.IGNORECASE)
        if injectie_formula_match:
            data["meterfactor_injectie"] = injectie_formula_match.group(1).replace(',', '.')
            data["balanceringskost_injectie"] = "-" + injectie_formula_match.group(2).replace(',', '.')
            data["index_type_injectie"] = "Belpex M"
            logging.info(f"Gevonden meterfactor injectie: {data['meterfactor_injectie']}")
            logging.info(f"Gevonden balanceringskost injectie: {data['balanceringskost_injectie']}")
            break

    logging.info(f"Verwerking voltooid voor SMART VARIABEL product")
    return data


def extract_octaplus_data(pdf_path):
    """Extraheert tariefgegevens uit OCTA+ tariefkaarten."""
    logging.info(f"Verwerken van OCTA+ tariefkaart: {pdf_path}")

    # Extract text and date
    text = extract_text_from_pdf(pdf_path)
    filename = os.path.basename(pdf_path)
    date = extract_date_from_filename(filename)

    if not date:
        logging.error(f"Kon geen datum extraheren uit {filename}")
        return None

    if "dynamic" in filename.lower():
        return extract_octaplus_dynamic_data(text, filename, date)
    elif "eco-clear" in filename.lower() or "eco clear" in filename.lower():
        return extract_octaplus_eco_clear_data(text, filename, date)
    elif "fixed" in filename.lower():
        return extract_octaplus_fixed_data(text, filename, date)
    elif "smart" in filename.lower():
        return extract_octaplus_smart_variabel_data(text, filename, date)
    else:
        logging.error(f"Kon product type niet bepalen voor {filename}")
        return None
