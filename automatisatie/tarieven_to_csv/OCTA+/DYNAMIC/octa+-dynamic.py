#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

# In[150]:
pdf_folder = '../../../leveranciers_tarieven/tariefkaarten/OCTA+/DYNAMIC'

# Get all PDF files in the folder
pdf_files = [str(file) for file in Path(pdf_folder).glob("*.pdf")]



def convert_dynamic(file_path):
    import re
    import camelot
    import os
    import csv
    import pdfplumber
    import re

    # In[152]:

    csv_file = "octaplus_dynamic.csv"

    # In[153]:

    contract_key = "OCTAPLUS_DYNAMIC"

    # In[154]:

    data = dict()

    # In[155]:

    tables = camelot.read_pdf(file_path, pages="all", flavor="stream")

    # In[156]:

    for i, table in enumerate(tables):
        df = table.df
        if df.isin(["Vaste vergoeding (€/jaar)"]).any().any():
            fixed_fee_row = df.index[df.isin(["Vaste vergoeding (€/jaar)"]).any(axis=1)][0]
            number = re.findall(r'-?\d+,\d+', df.loc[fixed_fee_row][1])[0].replace(",", '.')
            data['AdministrativeCosts'] = float(number)

    # In[157]:

    flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))

    # In[158]:

    with pdfplumber.open(file_path) as pdf:
        tables = []
        for page in pdf.pages:
            tables.append(tables.append(page.extract_tables()))
        cells = list(flatten(tables))

    # In[159]:

    for cell in cells:
        if "Kosten WKK" in str(cell):
            numbers = re.findall(r'-?\d+,\d+', cell)
            numbers = [float(num.replace(',', '.')) for num in numbers]
            data['GreenElectricity'], data["WKK"] = numbers
            break

    # In[160]:

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if "De elektriciteitsprijs voor OCTA+ Dynamic wordt elk uur geïndexeerd" in page.extract_text():
                for line in page.extract_text().split("\n"):
                    if "als volgt: Belpex Hourly *" in line:
                        numbers = re.findall(r'-?\d+,\d+', line)
                        numbers = [float(num.replace(',', '.')) for num in numbers]
                        data['DynamicMeterCost'], data["DynamicBalancingCost"] = numbers
                        break

    # In[162]:

    year, month = re.search(r'(\d{4})-(\d{2})', file_path).groups()
    date_key = f"{year}{month}01"  # Format as yyyymmdd with day as 01

    # In[163]:

    file_exists = os.path.isfile(csv_file)

    # In[164]:

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

        # Prepare data row in the specified order
        row_data = [
            date_key,
            contract_key,
            data.get('SingleMeterFixed', ''),
            data.get('DualMeterDayFixed', ''),
            data.get('DualMeterNightFixed', ''),
            data.get('ExclusiveNightMeterFixed', ''),
            data.get('SingleMeterVariableMeterFactor', ''),
            data.get('SingleMeterVariableBalancingCost', ''),
            data.get('DualMeterDayVariableMeterFactor', ''),
            data.get('DualMeterDayVariableBalancingCost', ''),
            data.get('DualMeterNightVariableMeterFactor', ''),
            data.get('DualMeterNightVariableBalancingCost', ''),
            data.get('ExclusiveNightMeterVariableMeterFactor', ''),
            data.get('ExclusiveNightMeterVariableBalancingCost', ''),
            data.get('DynamicMeterCost', ''),
            data.get('DynamicBalancingCost', ''),
            data.get('SingleMeterInjectionMeterFactor', ''),
            data.get('SingleMeterInjectionBalancingCost', ''),
            data.get('DualMeterDayInjectionMeterFactor', ''),
            data.get('DualMeterDayInjectionBalancingCost', ''),
            data.get('DualMeterNightInjectionMeterFactor', ''),
            data.get('DualMeterNightInjectionBalancingCost', ''),
            data.get('AdministrativeCosts', ''),
            data.get('GreenElectricity', ''),
            data.get('WKK', '')
        ]

        # Write data row
        writer.writerow(row_data)

    print(f"Data for {date_key} successfully written to {csv_file}")



for pdf in pdf_files:
    convert_dynamic(pdf)