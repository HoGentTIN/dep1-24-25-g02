from datetime import datetime, timedelta
from sqlalchemy import create_engine
import requests
import pandas as pd

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

def find_next_missing_date(last_date):
    # Bepaal de eerstvolgende ontbrekende datum vanaf de laatste beschikbare datum tot gisteren
    start_date = datetime.strptime(last_date, "%Y%m%d") + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    if start_date > end_date:
        return None  # Geen ontbrekende data
    return start_date.strftime("%Y-%m-%d")

def get_weather_station_keys():
    # Haalt bestaande WeatherStationKeys op en maakt een mapping
    query = "SELECT WeatherStationID, WeatherStationKey FROM DimWeatherStation"
    return pd.read_sql(query, engine)

def merge_weather_station_keys(df, station_keys):
    # Ensure both columns to merge have the same data type (int64)
    df['WeatherStationID'] = df['WeatherStationID'].astype(int)
    station_keys['WeatherStationID'] = station_keys['WeatherStationID'].astype(int)
    
    # Perform the merge
    df = df.merge(station_keys, on="WeatherStationID", how="left")
    return df.drop(columns=["WeatherStationID"])

def save_to_database(df, table_name):
    # Slaat het DataFrame op in de database
    if not df.empty:
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        print(f"{len(df)} records toegevoegd aan {table_name}.")


last_date = get_last_date()
date = find_next_missing_date(last_date)
weather_station_keys = get_weather_station_keys()

# Haal de data op
response = requests.get(f"https://opendata.meteo.be/service/ows?service=WFS&version=2.0.0&request=GetFeature&typenames=aws:aws_1day&outputformat=application/json&CQL_FILTER=(timestamp between '{date} 00:00:00' AND '{date} 23:59:59')")

if response.status_code == 200:
    data = response.json()

    # Zet JSON om naar DataFrame
    df = pd.json_normalize(data["features"], sep="_")

    # Selecteer alleen de relevante kolommen
    df = df[['properties_code', 'properties_timestamp', 'properties_precip_quantity',
             'properties_temp_avg', 'properties_temp_max', 'properties_temp_min',
             'properties_temp_grass_pt100_avg', 'properties_temp_soil_avg',
             'properties_temp_soil_avg_5cm', 'properties_temp_soil_avg_10cm',
             'properties_temp_soil_avg_20cm', 'properties_temp_soil_avg_50cm',
             'properties_wind_speed_10m', 'properties_wind_speed_avg_30m',
             'properties_wind_gusts_speed', 'properties_humidity_rel_shelter_avg',
             'properties_pressure', 'properties_sun_duration',
             'properties_short_wave_from_sky_avg', 'properties_sun_int_avg']]

    # Optioneel: Verwijder "properties_" uit de kolomnamen voor nettere output
    df.columns = [col.replace("properties_", "") for col in df.columns]

    df = df.rename(columns={"code": "WeatherStationID"})

    df['DateKey'] = df['timestamp'].str[:4] + df['timestamp'].str[5:7] + df['timestamp'].str[8:10]
    df['TimeKey'] = df['timestamp'].str[11:13] + df['timestamp'].str[14:16]
    df = merge_weather_station_keys(df, weather_station_keys)
    
    df = df.rename(columns={"precip_quantity": "PrecipQuantity","temp_avg": "TempAvg","temp_max": "TempMax","temp_min": "TempMin",
                            "temp_grass_pt100_avg": "TempGrassPt100Avg","temp_soil_avg": "TempSoilAvg","temp_soil_avg_5cm": "TempSoilAvg5cm",
                            "temp_soil_avg_10cm": "TempSoilAvg10cm","temp_soil_avg_20cm": "TempSoilAvg20cm",
                            "temp_soil_avg_50cm": "TempSoilAvg50cm","wind_speed_10m": "WindSpeed10m",
                            "wind_speed_avg_30m": "WindSpeedAvg30m","wind_gusts_speed": "WindGustsSpeed",
                            "humidity_rel_shelter_avg": "HumidityRelShelterAvg","pressure": "Pressure","sun_duration": "SunDuration",
                            "short_wave_from_sky_avg": "ShortWaveFromSkyAvg","sun_int_avg": "SunIntAvg"})

    df = df.reindex(columns=["DateKey", "TimeKey", "WeatherStationKey", "PrecipQuantity", "TempAvg", "TempMax", "TempMin",
                              "TempGrassPt100Avg", "TempSoilAvg", "TempSoilAvg5cm", "TempSoilAvg10cm", 
                              "TempSoilAvg20cm", "TempSoilAvg50cm", "WindSpeed10m", "WindSpeedAvg30m", 
                              "WindGustsSpeed", "HumidityRelShelterAvg", "Pressure", "SunDuration", "ShortWaveFromSkyAvg", 
                              "SunIntAvg"])
    print(df.count)
    save_to_database(df, "FactWeather")

else:
    print(f"Fout bij het ophalen van data: {response.status_code}")
