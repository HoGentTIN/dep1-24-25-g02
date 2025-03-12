# -*- coding: utf-8 -*-
import concurrent
import re
import os
import json
import csv
from dotenv import load_dotenv
import time
import queue
from concurrent.futures import ThreadPoolExecutor
from google import genai


def extract_energy_data_from_pdf(pdf_path, api_key):
    # Initialize the Gemini client with SSL verification disabled for troubleshooting
    client = genai.Client(api_key=api_key)

    # Extract ContractKey from path
    # Handle both forward and backward slashes in paths
    path_parts = re.split(r'[/\\]', pdf_path)

    # Find the provider and product parts (typically the last two directories before the filename)
    if len(path_parts) >= 3:
        # Get the last two directory names before the filename
        provider = path_parts[-3] if len(path_parts) >= 3 else ""
        product = path_parts[-2] if len(path_parts) >= 2 else ""
        contract_key = f"{provider}_{product}"
    else:
        # Fallback if path structure is different
        contract_key = os.path.basename(pdf_path).split('-')[0].upper()

    # Load the PDF file
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    # Create the prompt for Gemini
    prompt = """
Extraheer de volgende energiekosten parameters uit dit PDF document:
- DateKey: De datum in YYYY-MM-DD formaat (zoek naar datums zoals Januari 2024 en zet deze om naar 2024-01-01)
- SingleMeterFixed
- DualMeterDayFixed
- DualMeterNightFixed
- ExclusiveNightMeterFixed
- SingleMeterVariableMeterFactor
- SingleMeterVariableBalancingCost
- DualMeterDayVariableMeterFactor
- DualMeterDayVariableBalancingCost
- DualMeterNightVariableMeterFactor
- DualMeterNightVariableBalancingCost
- ExclusiveNightMeterVariableMeterFactor
- ExclusiveNightMeterVariableBalancingCost
- DynamicMeterCost
- DynamicBalancingCost
- SingleMeterInjectionMeterFactor
- SingleMeterInjectionBalancingCost
- DualMeterDayInjectionMeterFactor
- DualMeterDayInjectionBalancingCost
- DualMeterNightInjectionMeterFactor
- DualMeterNightInjectionBalancingCost
- AdministrativeCosts
- GreenElectricity
- WKK

Als het document een vast contract gebruikt, vul dan de vaste waarden in. Als het document een variabel contract gebruikt, vul dan de variabele waarden in.

Let op: in deze documenten wordt de komma (,) gebruikt als decimaal scheidingsteken. Zet alle waarden om naar punt (.) als decimaal scheidingsteken in de uitvoer. 16,18 is bijvoorbeeld 16.18 en niet 0.1618 hetzelfde met alle andere waarden! Als een waarde 0.xxxx is maar dit kan eigenlijk niet kloppen, dan is het waarschijnlijk een decimaal scheidingsteken probleem en moet je het maal 100 doen. 0.1618 wordt dan 16.18. Onder andere ook specifiek bij WWK en groene stroom.
Als het gratis is, zet 0 in plaats van 'Gratis'.

Voor variabele kosten, extraheer waar mogelijk de waarden uit de berekening en niet uit de geschatte prijs bijvoorbeeld bij: 'Belpex RLP * 1,127 + 17,5' is 1.127 de variabele meterfactor en 17.5 de variabele balanceringskost.
Bij injectie kunnen niet beide waarde leeg zijn, bij 0,0376 * BELPEXM -0,625 is het dus 0.0376 de variabele meterfactor en -0.625 de variabele balanceringskost en niet de -2.59 die erbij staat.

Geef de resultaten terug als een JSON object met exact deze veldnamen in het Engels. Als een waarde niet gevonden wordt, laat deze dan leeg, gebruik "" en niet null. Geef alleen de numerieke waarde, zonder valuta of frequentie, etc. Neem geen parameters op die niet gevraagd zijn.

Belangrijk: Houd alle parameternamen in het Engels in de JSON uitvoer.
    """

    # Make the API call with the PDF file with retry logic
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-pro",
                contents=[
                    {"text": prompt},
                    {"inline_data": {"mime_type": "application/pdf", "data": pdf_content}}
                ]
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise

    # Extract the JSON from the response
    try:
        # Try to find and parse JSON in the response
        response_text = response.text

        # Look for JSON content between triple backticks if present
        if "```" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("``````")[0]
        else:
            json_str = response_text

        # Parse the JSON
        data = json.loads(json_str)

        # Add the ContractKey from the path
        data["ContractKey"] = contract_key

        # Add EnergyCostKey if DateKey and ContractKey are present
        if data.get("DateKey") and data.get("ContractKey"):
            data["EnergyCostKey"] = f"{data['DateKey']}_{data['ContractKey']}"
        else:
            data["EnergyCostKey"] = ""

        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.replace(",", ".")

        return data
    except Exception as e:
        print(f"Error parsing response: {e}")
        print("Raw response:", response.text)
        return None


def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {output_path}")


def json_to_csv(json_path, csv_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Define the field order to match the required output format
    fields = [
        "EnergyCostKey", "DateKey", "ContractKey", "SingleMeterFixed",
        "DualMeterDayFixed", "DualMeterNightFixed", "ExclusiveNightMeterFixed",
        "SingleMeterVariableMeterFactor", "SingleMeterVariableBalancingCost",
        "DualMeterDayVariableMeterFactor", "DualMeterDayVariableBalancingCost",
        "DualMeterNightVariableMeterFactor", "DualMeterNightVariableBalancingCost",
        "ExclusiveNightMeterVariableMeterFactor", "ExclusiveNightMeterVariableBalancingCost",
        "DynamicMeterCost", "DynamicBalancingCost", "SingleMeterInjectionMeterFactor",
        "SingleMeterInjectionBalancingCost", "DualMeterDayInjectionMeterFactor",
        "DualMeterDayInjectionBalancingCost", "DualMeterNightInjectionMeterFactor",
        "DualMeterNightInjectionBalancingCost", "AdministrativeCosts",
        "GreenElectricity", "WKK"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        # Use semicolon as delimiter instead of comma
        writer = csv.writer(f, delimiter=';')
        writer.writerow(fields)  # Write header

        # Write data row
        row = [data.get(field, "") for field in fields]
        writer.writerow(row)

    print(f"CSV file saved to {csv_path}")


def is_already_processed(pdf_path, json_output_dir):
    """Check if a PDF has already been processed by looking for its JSON output"""
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    json_path = os.path.join(json_output_dir, f"{base_name}_extracted.json")
    return os.path.exists(json_path)


def process_pdf(pdf_path, api_key, json_output_dir, results_queue):
    """Process a single PDF file and add the results to the queue"""
    try:
        # Check if file has already been processed
        if is_already_processed(pdf_path, json_output_dir):
            print(f"Skipping already processed file: {pdf_path}")
            return True

        print(f"Processing PDF: {pdf_path}")
        # Extract data from the PDF
        data = extract_energy_data_from_pdf(pdf_path, api_key)

        if data:
            # Save individual JSON in the dedicated directory
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            json_path = os.path.join(json_output_dir, f"{base_name}_extracted.json")
            save_to_json(data, json_path)

            # Add to results queue
            results_queue.put(data)
            print(f"Successfully extracted data from {pdf_path}")
            return True
        else:
            print(f"Failed to extract data from {pdf_path}")
            return False
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False


def rate_limited_executor(pdf_paths, api_key, json_output_dir, max_workers=3, requests_per_minute=10):
    """Process PDFs with rate limiting to respect API limits"""
    results_queue = queue.Queue()
    processed_count = 0
    successful_count = 0

    # Calculate delay between requests to stay under rate limit
    delay_between_requests = 60 / requests_per_minute  # in seconds

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit initial batch of tasks
        futures = []
        for i, pdf_path in enumerate(pdf_paths[:max_workers]):
            futures.append(executor.submit(process_pdf, pdf_path, api_key, json_output_dir, results_queue))
            processed_count += 1
            time.sleep(delay_between_requests)  # Rate limiting

        # Process remaining PDFs as workers become available
        for i, pdf_path in enumerate(pdf_paths[max_workers:], max_workers):
            # Wait for a task to complete before submitting a new one
            completed, futures = concurrent.futures.wait(
                futures,
                return_when=concurrent.futures.FIRST_COMPLETED
            )

            # Check results of completed tasks
            for future in completed:
                if future.result():
                    successful_count += 1

            # Submit a new task
            futures.add(executor.submit(process_pdf, pdf_path, api_key, json_output_dir, results_queue))
            processed_count += 1
            time.sleep(delay_between_requests)  # Rate limiting

        # Wait for remaining tasks to complete
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                successful_count += 1

    # Collect all results from the queue
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    print(f"{processed_count} PDFs processed, {successful_count} successfully extracted")
    return results


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        return

    # Define input directory and output files/directories
    input_directory = "../leveranciers_tarieven/tariefkaarten"
    output_file = "energy_costs.csv"
    json_output_dir = "extracted_json"

    # Create JSON output directory if it doesn't exist
    os.makedirs(json_output_dir, exist_ok=True)

    # Define the field order to match the required output format
    fieldnames = [
        "EnergyCostKey", "DateKey", "ContractKey", "SingleMeterFixed",
        "DualMeterDayFixed", "DualMeterNightFixed", "ExclusiveNightMeterFixed",
        "SingleMeterVariableMeterFactor", "SingleMeterVariableBalancingCost",
        "DualMeterDayVariableMeterFactor", "DualMeterDayVariableBalancingCost",
        "DualMeterNightVariableMeterFactor", "DualMeterNightVariableBalancingCost",
        "ExclusiveNightMeterVariableMeterFactor", "ExclusiveNightMeterVariableBalancingCost",
        "DynamicMeterCost", "DynamicBalancingCost", "SingleMeterInjectionMeterFactor",
        "SingleMeterInjectionBalancingCost", "DualMeterDayInjectionMeterFactor",
        "DualMeterDayInjectionBalancingCost", "DualMeterNightInjectionMeterFactor",
        "DualMeterNightInjectionBalancingCost", "AdministrativeCosts",
        "GreenElectricity", "WKK"
    ]

    # Collect all PDF paths first
    pdf_paths = []
    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                pdf_paths.append(pdf_path)

    print(f"Found {len(pdf_paths)} PDF files to process")

    # Process PDFs with rate limiting
    rate_limited_executor(
        pdf_paths,
        api_key,
        json_output_dir,
        max_workers=20,
        requests_per_minute=100
    )

    print("Finished processing PDFs")

if __name__ == "__main__":
    main()
