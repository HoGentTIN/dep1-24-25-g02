#!/usr/bin/env python
# coding: utf-8

# In[203]:


import re
import camelot
import os
import csv
import pdfplumber
import re
from pathlib import Path

# In[204]:

pdf_folder = '../../../leveranciers_tarieven/tariefkaarten/OCTA+/ECO CLEAR'

pdf_files = [str(file) for file in Path(pdf_folder).glob("*.pdf")]


def convert_ecoclear(file_path):


    # In[205]:


    csv_file = "octaplus_ecoclear.csv"


    # In[206]:


    contract_key = "OCTAPLUS_ECOCLEAR"


    # In[207]:


    data = dict()


    # In[208]:


    tables = camelot.read_pdf(file_path, pages="all", flavor="hybrid")


    # In[209]:


    for i, table in enumerate(tables):
        df = table.df
        if df.isin(["Vaste vergoeding (€/jaar)"]).any().any():
            fixed_fee_row = df.index[df.isin(["Vaste vergoeding (€/jaar)"]).any(axis=1)][0]
            number = re.findall(r'-?\d+,\d+', df.loc[fixed_fee_row][1])[0].replace(",", '.')
            data['AdministrativeCosts'] = float(number)


    # In[210]:


    for i, table in enumerate(tables):
        df = table.df
        if df.isin(["Enkelvoudige meter"]).any().any():
            fixed_fee_row = df.index[df.isin(["Enkelvoudige meter"]).any(axis=1)][0]
            data["SingleMeterFixed"] = df.loc[fixed_fee_row][1]
        if df.isin(["Piekuren"]).any().any():
            fixed_fee_row = df.index[df.isin(["Piekuren"]).any(axis=1)][0]
            data["DualMeterDayFixed"] = df.loc[fixed_fee_row][1]
        if df.isin(["Daluren"]).any().any():
            fixed_fee_row = df.index[df.isin(["Daluren"]).any(axis=1)][0]
            data["DualMeterNightFixed"] = df.loc[fixed_fee_row][1]
        if df.isin(["Uitsluitend nachtmeter"]).any().any():
            fixed_fee_row = df.index[df.isin(["Uitsluitend nachtmeter"]).any(axis=1)][0]
            data["ExclusiveNightMeterFixed"] = df.loc[fixed_fee_row][1]


    # In[211]:


    flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))


    # In[212]:


    with pdfplumber.open(file_path) as pdf:
        tables = []
        for page in pdf.pages:
            tables.append(tables.append(page.extract_tables()))
        cells = list(flatten(tables))


    # In[213]:


    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if "Kosten WKK" in page.extract_text():
                for line in page.extract_text().split("\n"):
                    if "Kosten groene stroom " in line:
                        numbers = re.findall(r'-?\d+,\d+', line)
                        numbers = [float(num.replace(',', '.')) for num in numbers]
                        data['GreenElectricity']= numbers[-1]
                    if "Kosten WKK" in line:
                        numbers = re.findall(r'-?\d+,\d+', line)
                        numbers = [float(num.replace(',', '.')) for num in numbers]
                        data['WKK'] = numbers[-1]


    # In[214]:


    data


    # In[215]:
    year, month = re.search(r'(\d{4})-(\d{2})', file_path).groups()
    date_key = f"{year}{month}01"  # Format as yyyymmdd with day as 01

    print("currently processing", date_key)

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if "De elektriciteitsprijs voor OCTA+ Eco Clear" in page.extract_text():
                text = page.extract_text().replace("\n", " ")

                # Afname
                data["SingleMeterVariableMeterFactor"], data["SingleMeterVariableBalancingCost"] = re.findall(
                    r'\d+(?:,\d+)?', re.search(r'Enkelvoudige meter :\s*Belpex RLP \* [\d,]+ \+ [\d,]+', text).group(0))
                data["DualMeterDayVariableMeterFactor"], data["DualMeterDayVariableBalancingCost"] = re.findall(
                    r'\d+(?:,\d+)?',
                    re.search(r'Tweevoudige meter – Piek :\s*Belpex RLP \* [\d,]+ \+ [\d,]+', text).group(0))
                data["DualMeterNightVariableMeterFactor"], data["DualMeterNightVariableBalancingCost"] = re.findall(
                    r'\d+(?:,\d+)?',
                    re.search(r'Tweevoudige meter – Dal :\s*Belpex RLP \* [\d,]+ \+ [\d,]+', text).group(0))
                data["ExclusiveNightMeterVariableMeterFactor"], data[
                    "ExclusiveNightMeterVariableBalancingCost"] = re.findall(r'\d+(?:,\d+)?', re.search(
                    r'Exclusief Nachtmeter :\s*Belpex RLP \* [\d,]+ \+ [\d,]+', text).group(0))

                # Injectie
                try:
                    data["SingleMeterInjectionMeterFactor"], data["SingleMeterInjectionBalancingCost"] = re.findall(
                        r'\d+(?:,\d+)?', re.search(r'enkelvoudig :\s*Belpex \* [\d,]+ \- [\d,]+', text).group(0))
                    data["SingleMeterInjectionBalancingCost"] = -float(
                        data["SingleMeterInjectionBalancingCost"].replace(",", "."))

                    data["DualMeterDayInjectionMeterFactor"], data["DualMeterDayInjectionBalancingCost"] = re.findall(
                        r'\d+(?:,\d+)?', re.search(r'tweevoudig/piekuren : Belpex \* [\d,]+ \- [\d,]+', text).group(0))
                    data["DualMeterDayInjectionBalancingCost"] = -float(
                        data["DualMeterDayInjectionBalancingCost"].replace(",", "."))

                    data["DualMeterNightInjectionMeterFactor"], data[
                        "DualMeterNightInjectionBalancingCost"] = re.findall(r'\d+(?:,\d+)?', re.search(
                        r'tweevoudig/daluren : Belpex \* [\d,]+ \- [\d,]+', text).group(0))
                    data["DualMeterNightInjectionBalancingCost"] = -float(
                        data["DualMeterNightInjectionBalancingCost"].replace(",", "."))
                except:
                    print(f"Datekey {date_key} failed, taking default values instead")
                    data["SingleMeterInjectionMeterFactor"] = data["DualMeterDayInjectionMeterFactor"] = data["DualMeterNightInjectionMeterFactor"] = 0.915
                    data["SingleMeterInjectionBalancingCost"] = data["DualMeterDayInjectionBalancingCost"] = data["DualMeterNightInjectionBalancingCost"] = 19.83


    # In[216]:


    year, month = re.search(r'(\d{4})-(\d{2})', file_path).groups()
    date_key = f"{year}{month}01"  # Format as yyyymmdd with day as 01


    # In[217]:


    file_exists = os.path.isfile(csv_file)


    # In[218]:


    data = {key: value.replace(',', '.') if isinstance(value, str) else value for key, value in data.items()}


    # In[219]:


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


for file in pdf_files:
    convert_ecoclear(file)