import argparse
import os
import csv
import logging
from bolt_extractor import extract_bolt_data
from dats24_extractor import extract_dats24_data
from energie_be_extractor import extract_energiebe_data
from luminus_extractor import extract_luminus_data
from octaplus_extractor import extract_octaplus_data
from totalenergies_extractor import extract_totalenergies_data


def verwerk_kaarten(input_dir, output_csv, leverancier=None):
    """Verwerkt tariefkaarten en schrijft de gegevens naar een CSV-bestand."""
    logging.info(f"Start verwerking van tariefkaarten uit {input_dir}")

    fieldnames = [
        "leverancier", "product", "contract_type", "vanaf_datum", "tot_datum",
        "vaste_vergoeding_euro_jaar", "vaste_prijs_afname_eurocent_kwh",
        "meterfactor_afname", "balanceringskost_afname", "index_type_afname",
        "vaste_prijs_injectie_eurocent_kwh", "meterfactor_injectie",
        "balanceringskost_injectie", "index_type_injectie"
    ]

    results = []
    processed_files_count = 0

    # Zoek alle PDF-bestanden
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".pdf"):
                # Filter op leverancier indien opgegeven
                if leverancier:
                    if leverancier.lower() not in file.lower():
                        continue

                processed_files_count += 1
                pdf_path = os.path.join(root, file)
                logging.info(f"Verwerken van tariefkaart: {pdf_path}")

                # Extract data based on supplier
                data = None
                if "bolt" in file.lower():
                    data = extract_bolt_data(pdf_path)
                elif "dats24" in file.lower():
                    data = extract_dats24_data(pdf_path)
                elif "energie-be" in file.lower():
                    data = extract_energiebe_data(pdf_path)
                elif "luminus" in file.lower():
                    data = extract_luminus_data(pdf_path)
                elif "octa+" in file.lower():
                    data = extract_octaplus_data(pdf_path)
                elif "totalenergies" in file.lower():
                    data = extract_totalenergies_data(pdf_path)
                # Voeg hier andere leveranciers toe

                if data:
                    results.append(data)

    logging.info(f"{processed_files_count} tariefkaarten gevonden, {len(results)} succesvol verwerkt")

    # Controleer of het bestand al bestaat
    file_exists = os.path.isfile(output_csv)

    # Schrijf resultaten naar CSV (append als het bestand al bestaat)
    if results:
        mode = 'a' if file_exists else 'w'
        with open(output_csv, mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Alleen header schrijven als het een nieuw bestand is
            if not file_exists:
                writer.writeheader()
            writer.writerows(results)
        logging.info(f"Succesvol {len(results)} records toegevoegd aan {output_csv}")
    else:
        logging.warning(f"Geen gegevens om te schrijven naar {output_csv}")


if __name__ == "__main__":
    input_directory = "../leveranciers_tarieven/tariefkaarten"
    output_file = "tarieven.csv"
    leverancier = "totalenergies"

    if leverancier:
        logging.info(f"Start extractie van {leverancier} tariefkaarten")
        verwerk_kaarten(input_directory, output_file, leverancier)
        logging.info(f"Extractie van {leverancier} tariefkaarten voltooid")
    else:
        logging.info("Start extractie van tariefkaarten voor alle leveranciers")
        verwerk_kaarten(input_directory, output_file)
        logging.info("Extractie van tariefkaarten voltooid")