from datetime import datetime, timedelta
from sqlalchemy import create_engine
import pandas as pd
import requests
import pyodbc

# Gegevens voor de verbinding
server = r"localhost"  # Servernaam of IP-adres van je SQL Server
database = "DEP1_DWH"  # Naam van je database

# Maak de verbindingsstring met Windows Authenticatie
engine = create_engine("mssql+pyodbc://@{}/{}?driver=ODBC+Driver+17+for+SQL+Server".format(server, database))

def get_last_date():
    # Haalt de laatste datum op die in de database staat
    query = "SELECT MAX(DateKey) AS LastDate FROM FactWeather"
    last_date = pd.read_sql(query, engine)["LastDate"].iloc[0]
    return str(last_date) if pd.notna(last_date) else (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

def find_missing_dates(last_date):
    # Bepaal de ontbrekende datums vanaf de laatste beschikbare datum tot gisteren
    start_date = datetime.strptime(last_date, "%Y%m%d") + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    missing_dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d").tolist()
    return missing_dates

def fetch_weather_data(dates):
    # Haalt weerdata op voor een reeks datums
    all_records = []
    for date in dates:
        response = requests.get(f"https://opendata.meteo.be/service/ows?service=WFS&version=2.0.0&request=GetFeature&typenames=aws:aws_1day&outputformat=application/json&CQL_FILTER=(timestamp between '{date} 00:00:00' AND '{date} 23:59:59')")
        if response.status_code == 200:
            data = response.json()
            all_records.extend(data.get("features", []))
        else:
            print(f"Kon data van {date} niet ophalen.")
    return all_records

def process_weather_data(records):
    # Zet de API response om naar een DataFrame met de juiste kolommen
    data = [feature["properties"] for feature in records]
    df = pd.DataFrame(data)
    df['DateKey'] = df['timestamp'].str[:4] + df['timestamp'].str[5:7] + df['timestamp'].str[8:10]
    df['TimeKey'] = df['timestamp'].str[11:13] + df['timestamp'].str[14:16] + df['timestamp'].str[17:19]
    df.rename(columns={'station_id': 'WeatherStationID'}, inplace=True)
    df = df.reindex(columns=["DateKey", "TimeKey", "WeatherStationID", "PrecipQuantity", "TempAvg", "TempMax", "TempMin",
                              "TempGrassPt100Avg", "TempSoilAvg", "TempSoilAvg5cm", "TempSoilAvg10cm", 
                              "TempSoilAvg20cm", "TempSoilAvg50cm", "WindSpeed10m", "WindSpeedAvg30m", 
                              "WindGustsSpeed", "HumidityRelShelterAvg", "Pressure", "SunDuration", "ShortWaveFromSkyAvg", 
                              "SunIntAvg"])
    return df.dropna(subset=["DateKey", "WeatherStationID"])

def get_weather_station_keys():
    # Haalt bestaande WeatherStationKeys op en maakt een mapping
    query = "SELECT WeatherStationID, WeatherStationKey FROM DimWeatherStation"
    return pd.read_sql(query, engine)

def merge_weather_station_keys(df, station_keys):
    # Voegt de juiste WeatherStationKeys toe aan de dataset
    df = df.merge(station_keys, on="WeatherStationID", how="left")
    return df.drop(columns=["WeatherStationID"])

def save_to_database(df, table_name):
    # Slaat het DataFrame op in de database
    if not df.empty:
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        print(f"{len(df)} records toegevoegd aan {table_name}.")

# Hoofdproces
last_date = get_last_date()
missing_dates = find_missing_dates(last_date)
weather_station_keys = get_weather_station_keys()

if missing_dates:
    weather_records = fetch_weather_data(missing_dates)
    if weather_records:
        df_weather = process_weather_data(weather_records)
        df_weather = merge_weather_station_keys(df_weather, weather_station_keys)
        save_to_database(df_weather, "FactWeather")
    else:
        print("Geen bruikbare data opgehaald.")
