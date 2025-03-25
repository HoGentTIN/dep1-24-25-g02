# %%
import re
import camelot
import os
import csv
import pandas as pd
from pathlib import Path

# %%
pdf_folder = r'C:\Users\sfsan\Documents\Hogeschool\DEPI\dep1-24-25-g02\tariefkaarten\TOTALENERGIES\PIXEL NEXT VAST'
pdf_files = [str(file) for file in Path(pdf_folder).glob("*.pdf")]
csv_file = "totalenergiesnextvast.csv"
file_exists = os.path.isfile(csv_file)

# %%
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

df_tepnv = pd.DataFrame(columns=header)

df_tepnv.head()

# %%
table = camelot.read_pdf(pdf_folder + '/totalenergies-pixel-next-vast-2023-08.pdf', pages='1')

# %%
for file_path in pdf_files:
    table = camelot.read_pdf(pdf_folder + '/totalenergies-pixel-next-vast-2023-08.pdf', pages='1')
    
    verbruik = table[0].df
    bijdrageWkk = table[1].df
    vastevergoeding = table[2].df

    match = re.search(r'(\d{4})-(\d{2})', os.path.basename(file_path))
    date_key = f"{match.group(1)}{match.group(2)}01" if match else "Unknown"
    
    new_row = {
    "DateKey": date_key,
    "ContractKey": "13",
    "SingleMeterFixed": verbruik.at[3, 0],
    "DualMeterDayFixed": verbruik.at[3, 1],
    "DualMeterNightFixed": verbruik.at[3, 2],
    "ExclusiveNightMeterFixed": verbruik.at[3, 3],
    "GreenElectricity": bijdrageWkk.at[1, 0],
    "AdministrativeCosts": bijdrageWkk.at[1, 0],
    }

  
    for col in df.columns:
        if col not in new_row:
            new_row[col] = ''

    df = df.append(new_row, ignore_index=True)



