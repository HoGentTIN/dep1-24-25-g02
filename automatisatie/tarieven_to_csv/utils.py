import os
import re
import pdfplumber
import datetime
import logging

# Configureer logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("extraction_debug.log"),
        logging.StreamHandler()
    ]
)


def save_extracted_text(pdf_path, text):
    """Slaat de geëxtraheerde tekst op voor debugging doeleinden."""
    filename = os.path.basename(pdf_path)
    output_dir = "debug_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"{filename.replace('.pdf', '')}_extracted.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

    logging.info(f"Geëxtraheerde tekst opgeslagen in: {output_file}")


def extract_text_from_pdf(pdf_path):
    """Extraheert tekst uit een PDF-bestand."""
    logging.info(f"Extracting text from: {pdf_path}")
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
                else:
                    logging.warning(f"No text extracted from page in {pdf_path}")

        logging.info(f"Extracted {len(text)} characters from {pdf_path}")
        # Sla de geëxtraheerde tekst op voor debugging
        save_extracted_text(pdf_path, text)
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return ""


def extract_date_from_filename(filename):
    """Extraheert datum uit bestandsnaam zoals 'leverancier-product-2023-01.pdf'."""
    logging.info(f"Extracting date from filename: {filename}")
    pattern = r'(\d{4})-(\d{2})'
    match = re.search(pattern, filename)
    if match:
        year, month = match.groups()
        date = f"{year}-{month}-01"
        logging.info(f"Extracted date: {date}")
        return date
    logging.warning(f"Could not extract date from filename: {filename}")
    return None


def get_end_date(start_date):
    """Berekent einddatum (laatste dag van de maand)."""
    logging.info(f"Calculating end date for: {start_date}")
    try:
        year, month, _ = start_date.split("-")
        if month == "12":
            next_month = "01"
            next_year = str(int(year) + 1)
        else:
            next_month = str(int(month) + 1).zfill(2)
            next_year = year

        end_date = f"{next_year}-{next_month}-01"
        # Converteer naar datetime en trek 1 dag af
        end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        end_datetime = end_datetime.replace(day=1) - datetime.timedelta(days=1)
        result = end_datetime.strftime("%Y-%m-%d")
        logging.info(f"Calculated end date: {result}")
        return result
    except Exception as e:
        logging.error(f"Error calculating end date for {start_date}: {e}")
        return None
