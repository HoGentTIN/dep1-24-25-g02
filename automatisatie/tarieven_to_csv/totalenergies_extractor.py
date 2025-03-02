import re
import os
from utils import extract_text_from_pdf, extract_date_from_filename, get_end_date, logging


def extract_totalenergies_data(pdf_path):
    """Extraheert tariefgegevens uit TotalEnergies tariefkaarten."""
    logging.info(f"Verwerken van TotalEnergies tariefkaart: {pdf_path}")

    # Extract text and date
    text = extract_text_from_pdf(pdf_path)
    filename = os.path.basename(pdf_path)
    date = extract_date_from_filename(filename)

    if not date:
        logging.error(f"Kon geen datum extraheren uit {filename}")
        return None

    # Bepaal het product type
    product = ""
    contract_type = ""

    if "pixel-next-vast" in filename.lower() or "pixel-blue-fixed" in filename.lower() or "pixel-next" in filename.lower():
        product = "PIXEL NEXT VAST"
        contract_type = "vast"
    elif "pixel-edrive" in filename.lower() or "emobility" in filename.lower():
        product = "PIXEL EDRIVE"
        contract_type = "variabel"
    elif "pixie" in filename.lower():
        product = "PIXIE"
        contract_type = "variabel"
    elif "pixel" in filename.lower():
        product = "PIXEL"
        contract_type = "variabel"
    else:
        logging.error(f"Kon product type niet bepalen voor {filename}")
        return None

    logging.info(f"Gedetecteerd product: {product}, contract type: {contract_type}")

    # Initialiseer data dictionary
    data = {
        "leverancier": "TOTALENERGIES",
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

    # Extract vaste vergoeding
    vaste_vergoeding_patterns = [
        r'Vaste\s+vergoeding\s*\(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Vaste\s+vergoeding\s*\(0\)\s*\(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Vaste\s+vergoeding\s*0\s*\(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Vaste\s+vergoeding\s*\(€\s*[Jj]aar\)\s*(\d+[,.]\d+)',
        r'Abonnement\s*\(€\/jaar\)\s*(\d+[,.]\d+)',
        r'Abonnement\s*:\s*(\d+[,.]\d+)',
        r'Vaste\s+vergoeding\s*\(0\)\s*\(€\/jaar\)\s*(\d+)'
    ]

    for pattern in vaste_vergoeding_patterns:
        vaste_vergoeding_match = re.search(pattern, text, re.IGNORECASE)
        if vaste_vergoeding_match:
            data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_match.group(1).replace(',', '.')
            logging.info(f"Gevonden vaste vergoeding: {data['vaste_vergoeding_euro_jaar']}")
            break

    # Als we nog geen vaste vergoeding hebben gevonden, zoek dan naar een getal na "Vaste vergoeding"
    if not data["vaste_vergoeding_euro_jaar"]:
        vaste_vergoeding_alt = re.search(r'Vaste\s+vergoeding[^\d]*(\d+)', text, re.IGNORECASE)
        if vaste_vergoeding_alt:
            data["vaste_vergoeding_euro_jaar"] = vaste_vergoeding_alt.group(1)
            logging.info(f"Gevonden vaste vergoeding (alternatief): {data['vaste_vergoeding_euro_jaar']}")

    # Afhankelijk van het contract type, zoek naar specifieke informatie
    if contract_type == "vast":
        # Voor PIXEL NEXT VAST: zoek vaste prijs voor afname
        afname_patterns = [
            r'Enkelvoudige\s+[Mm]eter\s*(\d+[,.]\d+)',
            r'Enkelvoudige\s+[Mm]eter\s*:\s*(\d+[,.]\d+)',
            r'Normaal\s+tarief\s*(\d+[,.]\d+)',
            r'Energieprijs\s*\(c€\/kWh\)\s*(\d+[,.]\d+)'
        ]

        for pattern in afname_patterns:
            afname_match = re.search(pattern, text, re.IGNORECASE)
            if afname_match:
                data["vaste_prijs_afname_eurocent_kwh"] = afname_match.group(1).replace(',', '.')
                logging.info(f"Gevonden vaste prijs afname: {data['vaste_prijs_afname_eurocent_kwh']}")
                break

        # Zoek vaste prijs voor injectie of injectieformule
        injectie_prijs_patterns = [
            r'Injectie[^\n]*Enkelvoudige\s+[Mm]eter\s*(\d+[,.]\d+)',
            r'Injectie[^\n]*Normaal\s+tarief\s*(\d+[,.]\d+)',
            r'Injectieprijs\s*\(c€\/kWh\)\s*(\d+[,.]\d+)'
        ]

        for pattern in injectie_prijs_patterns:
            injectie_match = re.search(pattern, text, re.IGNORECASE)
            if injectie_match:
                data["vaste_prijs_injectie_eurocent_kwh"] = injectie_match.group(1).replace(',', '.')
                logging.info(f"Gevonden vaste prijs injectie: {data['vaste_prijs_injectie_eurocent_kwh']}")
                break

        # Als geen vaste injectieprijs, zoek naar formule
        if not data["vaste_prijs_injectie_eurocent_kwh"]:
            injectie_formula_patterns = [
                r'Injectie[^\n]*BELPEX\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
                r'Injectie[^\n]*BELPEX\s*×\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
                r'Injectie[^\n]*(\d+[,.]\d+)\s*\*\s*BELPEX\s*\-\s*(\d+[,.]\d+)'
            ]

            for pattern in injectie_formula_patterns:
                injectie_formula_match = re.search(pattern, text, re.IGNORECASE)
                if injectie_formula_match:
                    data["meterfactor_injectie"] = injectie_formula_match.group(1).replace(',', '.')
                    data["balanceringskost_injectie"] = "-" + injectie_formula_match.group(2).replace(',', '.')
                    data["index_type_injectie"] = "BELPEX"
                    logging.info(f"Gevonden meterfactor injectie: {data['meterfactor_injectie']}")
                    logging.info(f"Gevonden balanceringskost injectie: {data['balanceringskost_injectie']}")
                    break

    else:  # variabel contract
        # Voor PIXEL, PIXEL EDRIVE, PIXIE: zoek meterfactor en balanceringskost
        # Zoek naar formule voor afname
        afname_formula_patterns = [
            r'(\d+[,.]\d+)\s*\*\s*BELPEXM?_?RLP\s*\+\s*(\d+[,.]\d+)',
            r'BELPEXM?_?RLP\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
            r'BELPEXM?_?RLP\s*\+\s*(\d+[,.]\d+)',
            r'Enkelvoudige\s+[Mm]eter\s*:\s*BELPEXM?_?RLP\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
            r'Enkelvoudige\s+[Mm]eter\s*:\s*(\d+[,.]\d+)\s*\*\s*BELPEXM?_?RLP\s*\+\s*(\d+[,.]\d+)',
            r'Normaal\s+tarief\s*:\s*BELPEXM?_?RLP\s*\*\s*(\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
            r'Normaal\s+tarief\s*:\s*(\d+[,.]\d+)\s*\*\s*BELPEXM?_?RLP\s*\+\s*(\d+[,.]\d+)',
            r'BELPEXM?_?RLP\s*×\s*(\d+[,.]\d+)\s*\+\s*(\d+[,.]\d+)',
            r'Tariefformule[^\n]*(\d+[,.]\d+)\s*\*\s*BELPEXM?_?RLP\s*\+\s*(\d+[,.]\d+)'
        ]

        for pattern in afname_formula_patterns:
            afname_formula_match = re.search(pattern, text, re.IGNORECASE)
            if afname_formula_match:
                # Controleer of er 1 of 2 groepen zijn
                if len(afname_formula_match.groups()) == 2:
                    data["meterfactor_afname"] = afname_formula_match.group(1).replace(',', '.')
                    data["balanceringskost_afname"] = afname_formula_match.group(2).replace(',', '.')
                else:
                    data["meterfactor_afname"] = "1.0"  # Default waarde als niet gevonden
                    data["balanceringskost_afname"] = afname_formula_match.group(1).replace(',', '.')

                data["index_type_afname"] = "BELPEX_RLP"
                logging.info(f"Gevonden meterfactor afname: {data['meterfactor_afname']}")
                logging.info(f"Gevonden balanceringskost afname: {data['balanceringskost_afname']}")
                break

        # Zoek naar formule voor injectie
        injectie_formula_patterns = [
            r'Injectie[^\n]*(\d+[,.]\d+)\s*\*\s*BELPEXM?\s*\-\s*(\d+[,.]\d+)',
            r'Injectie[^\n]*BELPEXM?\s*\*\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
            r'Injectie[^\n]*BELPEXM?\s*×\s*(\d+[,.]\d+)\s*\-\s*(\d+[,.]\d+)',
            r'Injectie\*\*\*[^\n]*(\d+[,.]\d+)\s*\*\s*BELPEXM?\s*\-\s*(\d+[,.]\d+)',
            r'(\d+[,.]\d+)\s*\*\s*BELPEXM?\s*\-\s*(\d+[,.]\d+)'
        ]

        for pattern in injectie_formula_patterns:
            injectie_formula_match = re.search(pattern, text, re.IGNORECASE)
            if injectie_formula_match:
                data["meterfactor_injectie"] = injectie_formula_match.group(1).replace(',', '.')
                data["balanceringskost_injectie"] = "-" + injectie_formula_match.group(2).replace(',', '.')
                data["index_type_injectie"] = "BELPEX"
                logging.info(f"Gevonden meterfactor injectie: {data['meterfactor_injectie']}")
                logging.info(f"Gevonden balanceringskost injectie: {data['balanceringskost_injectie']}")
                break

    logging.info(f"Verwerking voltooid voor {product} product")
    return data

