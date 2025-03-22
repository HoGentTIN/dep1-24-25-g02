#!/usr/bin/env python
# coding: utf-8

import re
import camelot
import os
import csv
from pathlib import Path

pdf_folder = '../../leveranciers_tarieven/tariefkaarten/DATS24/ELEKTRICITEIT'

# Get all PDF files in the folder
pdf_files = [str(file) for file in Path(pdf_folder).glob("*.pdf")]

# CSV file to write results
csv_file = "dats24.csv"
file_exists = os.path.isfile(csv_file)

# Process each PDF file
for file_path in pdf_files:
    print(f"Processing {file_path}...")

    # Reset data dictionary for each file
    data = dict()

    try:
        # Extract tables from the PDF
        tables = camelot.read_pdf(file_path, pages="all", flavor="stream")

        # Process first table with pricing information
        for i, table in enumerate(tables):
            df = table.df

            if df.isin(["VASTE VERGOEDING (€/jaar)"]).any().any():
                print(f"'VASTE VERGOEDING (€/jaar)' found in Table {i + 1}")
                fixed_fee_row = df.index[df.isin(["VASTE VERGOEDING (€/jaar)"]).any(axis=1)][0]
                data['AdministrativeCosts'] = df.loc[fixed_fee_row][1]

            if df.isin(["Afname1 (c€/kWh)"]).any().any():
                print(f"'Afname1 (c€/kWh)' found in Table {i + 1}")
                variable_row = df.index[df.isin(["Afname1 (c€/kWh)"]).any(axis=1)][0]
                data['SingleMeterFixed'] = df.loc[variable_row][1]
                data['DualMeterDayFixed'] = df.loc[variable_row][2]
                data['DualMeterNightFixed'] = df.loc[variable_row][4]
                data['ExclusiveNightMeterFixed'] = df.loc[variable_row][5]

            if df.isin(["Teruglevering2 (c€/kWh)"]).any().any():
                print(f"'Teruglevering2 (c€/kWh)' found in Table {i + 1}")
                injection_row = df.index[df.isin(["Teruglevering2 (c€/kWh)"]).any(axis=1)][0]
                data['SingleMeterInjectionMeterFactor'] = df.loc[injection_row][1]
                data['DualMeterDayInjectionMeterFactor'] = df.loc[injection_row][3]
                data['DualMeterNightInjectionMeterFactor'] = df.loc[injection_row][3]

            if df.isin(["GSC (c€/kWh)"]).any().any():
                print(f"'GSC (c€/kWh)' found in Table {i + 1}")
                gsc_row = df.index[df.isin(["GSC (c€/kWh)"]).any(axis=1)][0]
                data['GreenElectricity'] = df.loc[gsc_row][1]

            if df.isin(["WKC (c€/kWh)"]).any().any():
                print(f"'WKC (c€/kWh)' found in Table {i + 1}")
                wkc_row = df.index[df.isin(["WKC (c€/kWh)"]).any(axis=1)][0]
                data['WKK'] = df.loc[wkc_row][1]

            for idx in range(len(df)):
                row_values = df.iloc[idx].tolist()
                if any('GSC' in str(val) for val in row_values if val is not None):
                    print(f"'GSC' found in Table {i + 1} at row {idx}")
                    data['GreenElectricity'] = df.iloc[idx][1]
                    break

            # Don't break after first table - we need to check all tables
            if len(data) > 0:  # Only break the inner loop if we found data
                break

        # Process second table with tariff formulas
        for i, table in enumerate(tables):
            df = table.df

            if df.isin(["TARRIEFFORMULE"]).any().any():
                print(f"Found tariff formula table (Table {i + 1})")

                for idx in range(len(df)):
                    row_values = df.iloc[idx].tolist()

                    if "Enkelvoudige meter" in row_values:
                        formula = df.iloc[idx][2]  # AFNAME column
                        if "BE_spotRLP" in formula:
                            factor = formula.split('x')[1].split('+')[0].strip()
                            balancing = formula.split('+')[1].split(')')[0].strip()
                            data['SingleMeterVariableMeterFactor'] = factor
                            data['SingleMeterVariableBalancingCost'] = balancing

                    if "Tweevoudige meter" in row_values and "Dag" in row_values:
                        formula = df.iloc[idx][2]
                        if "BE_spotRLP" in formula:
                            data['DualMeterDayVariableMeterFactor'] = formula.split('x')[1].split('+')[0].strip()
                            data['DualMeterDayVariableBalancingCost'] = formula.split('+')[1].split(')')[0].strip()

                    if "Nacht" in row_values:
                        formula = df.iloc[idx][2]
                        if "BE_spotRLP" in formula:
                            data['DualMeterNightVariableMeterFactor'] = formula.split('x')[1].split('+')[0].strip()
                            data['DualMeterNightVariableBalancingCost'] = formula.split('+')[1].split(')')[0].strip()

                    if "Uitsluitend nachtmeter" in row_values:
                        formula = df.iloc[idx][2]
                        if "BE_spotRLP" in formula:
                            data['ExclusiveNightMeterVariableMeterFactor'] = formula.split('x')[1].split('+')[0].strip()
                            data['ExclusiveNightMeterVariableBalancingCost'] = formula.split('+')[1].split(')')[
                                0].strip()

                    if len(row_values) > 3 and isinstance(row_values[3], str) and "BE_spotSPP" in row_values[3]:
                        injection = row_values[3]
                        injection_factor = injection.split('x')[1].split('-')[0].strip()
                        injection_balancing = injection.split('-')[1].strip().split(')')[0].strip()
                        data['SingleMeterInjectionMeterFactor'] = injection_factor
                        data['SingleMeterInjectionBalancingCost'] = injection_balancing
                        data['DualMeterDayInjectionMeterFactor'] = injection_factor
                        data['DualMeterDayInjectionBalancingCost'] = injection_balancing
                        data['DualMeterNightInjectionMeterFactor'] = injection_factor
                        data['DualMeterNightInjectionBalancingCost'] = injection_balancing

                break  # Break after finding the tariff formula table

        # Extract date from filename
        match = re.search(r'(\d{4})-(\d{2})', os.path.basename(file_path))
        if match:
            year, month = match.groups()
            date_key = f"{year}{month}01"  # Format as yyyymmdd with day as 01
        else:
            # If filename doesn't match pattern, use current date
            print(f"Warning: Could not extract date from filename {file_path}")
            date_key = "Unknown"

        # Replace commas with periods for decimal values
        data = {key: value.replace(',', '.') if isinstance(value, str) else value for key, value in data.items()}

        # Check if we have all required data
        required_fields = [
            'SingleMeterFixed', 'DualMeterDayFixed', 'DualMeterNightFixed', 'ExclusiveNightMeterFixed',
            'SingleMeterVariableMeterFactor', 'SingleMeterVariableBalancingCost', 'DualMeterDayVariableMeterFactor',
            'DualMeterDayVariableBalancingCost', 'DualMeterNightVariableMeterFactor',
            'DualMeterNightVariableBalancingCost',
            'ExclusiveNightMeterVariableMeterFactor', 'ExclusiveNightMeterVariableBalancingCost',
            'SingleMeterInjectionMeterFactor', 'SingleMeterInjectionBalancingCost',
            'DualMeterDayInjectionMeterFactor', 'DualMeterDayInjectionBalancingCost',
            'DualMeterNightInjectionMeterFactor', 'DualMeterNightInjectionBalancingCost',
            'AdministrativeCosts', 'GreenElectricity', 'WKK'
        ]

        if date_key == "20240401":
            data["SingleMeterVariableMeterFactor"] = "0.1164"
            data["SingleMeterVariableBalancingCost"] = "0.921"
            data["DualMeterDayVariableMeterFactor"] = "0.1304"
            data["DualMeterDayVariableBalancingCost"] = "0.921"
            data["DualMeterNightVariableMeterFactor"] = "0.1064"
            data["DualMeterNightVariableBalancingCost"] = "0.921"
            data["ExclusiveNightMeterVariableMeterFactor"] = "0.1064"
            data["ExclusiveNightMeterVariableBalancingCost"] = "0.921"

            data["SingleMeterInjectionBalancingCost"] = "0.38"
            data["DualMeterDayInjectionBalancingCost"] = "0.38"
            data["DualMeterNightInjectionBalancingCost"] = "0.38"

            data["SingleMeterInjectionMeterFactor"] = "0.073"
            data["DualMeterDayInjectionMeterFactor"] = "0.073"
            data["DualMeterNightInjectionMeterFactor"] = "0.073"

        elif date_key == "20230401":
            data["SingleMeterVariableMeterFactor"] = "0.1139"
            data["SingleMeterVariableBalancingCost"] = "0.857"
            data["DualMeterDayVariableMeterFactor"] = "0.1355"
            data["DualMeterDayVariableBalancingCost"] = "0.857"
            data["DualMeterNightVariableMeterFactor"] = "0.1032"
            data["DualMeterNightVariableBalancingCost"] = "0.857"
            data["ExclusiveNightMeterVariableMeterFactor"] = "0.1032"
            data["ExclusiveNightMeterVariableBalancingCost"] = "0.857"

            data["SingleMeterInjectionBalancingCost"] = "0.38"
            data["DualMeterDayInjectionBalancingCost"] = "0.38"
            data["DualMeterNightInjectionBalancingCost"] = "0.38"

            data["SingleMeterInjectionMeterFactor"] = "0.073"
            data["DualMeterDayInjectionMeterFactor"] = "0.073"
            data["DualMeterNightInjectionMeterFactor"] = "0.073"



        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"Warning: Missing fields in {file_path}: {missing_fields}")
            # Initialize missing fields with empty values
            for field in missing_fields:
                data[field] = ''

        # Write to CSV
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')

            # Write header only if file doesn't exist
            if not file_exists:
                header = ["DateKey", "ContractKey", "SingleMeterFixed", "DualMeterDayFixed",
                          "DualMeterNightFixed", "ExclusiveNightMeterFixed", "SingleMeterVariableMeterFactor",
                          "SingleMeterVariableBalancingCost", "DualMeterDayVariableMeterFactor",
                          "DualMeterDayVariableBalancingCost", "DualMeterNightVariableMeterFactor",
                          "DualMeterNightVariableBalancingCost", "ExclusiveNightMeterVariableMeterFactor",
                          "ExclusiveNightMeterVariableBalancingCost", "DynamicMeterCost", "DynamicBalancingCost",
                          "SingleMeterInjectionMeterFactor", "SingleMeterInjectionBalancingCost",
                          "DualMeterDayInjectionMeterFactor", "DualMeterDayInjectionBalancingCost",
                          "DualMeterNightInjectionMeterFactor", "DualMeterNightInjectionBalancingCost",
                          "AdministrativeCosts", "GreenElectricity", "WKK"]
                writer.writerow(header)
                file_exists = True  # Set to True after writing header

            # Prepare data row in the specified order
            row_data = [
                date_key,
                "DATS24_ELEKTRICITEIT",
                data['SingleMeterFixed'],
                data['DualMeterDayFixed'],
                data['DualMeterNightFixed'],
                data['ExclusiveNightMeterFixed'],
                data['SingleMeterVariableMeterFactor'],
                data['SingleMeterVariableBalancingCost'],
                data['DualMeterDayVariableMeterFactor'],
                data['DualMeterDayVariableBalancingCost'],
                data['DualMeterNightVariableMeterFactor'],
                data['DualMeterNightVariableBalancingCost'],
                data['ExclusiveNightMeterVariableMeterFactor'],
                data['ExclusiveNightMeterVariableBalancingCost'],
                data.get('DynamicMeterCost', ''),
                data.get('DynamicBalancingCost', ''),
                data['SingleMeterInjectionMeterFactor'],
                data['SingleMeterInjectionBalancingCost'],
                data['DualMeterDayInjectionMeterFactor'],
                data['DualMeterDayInjectionBalancingCost'],
                data['DualMeterNightInjectionMeterFactor'],
                data['DualMeterNightInjectionBalancingCost'],
                data['AdministrativeCosts'],
                data['GreenElectricity'],
                data['WKK']
            ]

            # Write data row
            writer.writerow(row_data)

        print(f"Data for {date_key} successfully written to {csv_file}")

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

print(f"All PDF files processed. Results saved to {csv_file}")
