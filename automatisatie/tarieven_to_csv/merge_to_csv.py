import os
import json
import csv
from pathlib import Path


def json_files_to_csv(json_dir, output_csv):
    """
    Convert all JSON files in a directory to a single CSV file with consistent field order.

    Args:
        json_dir (str): Directory containing JSON files
        output_csv (str): Path to output CSV file
    """
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

    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

    if not json_files:
        print(f"No JSON files found in {json_dir}")
        return

    # Create CSV file with the specified field order
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        # Write header row
        writer.writerow(fields)

        # Process each JSON file
        for json_file in json_files:
            try:
                with open(os.path.join(json_dir, json_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Create a row with values in the correct order
                row = []
                for field in fields:
                    # Get value from JSON, handle missing fields, empty strings, and None values
                    value = data.get(field, "")

                    # Convert None to empty string
                    if value is None:
                        value = ""

                    # Ensure numeric values are handled consistently
                    # (some may be stored as strings, others as numbers)
                    if isinstance(value, (int, float)):
                        value = str(value)

                    row.append(value)

                # Write the row to CSV
                writer.writerow(row)
                print(f"Processed {json_file}")

            except Exception as e:
                print(f"Error processing {json_file}: {e}")

    print(f"CSV file created at {output_csv}")


def main():
    # Directory containing JSON files
    json_dir = "extracted_json"

    # Output CSV file
    output_csv = "../../data/input/energy_costs.csv"

    # Convert JSON files to CSV
    json_files_to_csv(json_dir, output_csv)


if __name__ == "__main__":
    main()
