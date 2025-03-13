import pandas as pd
from sqlalchemy import create_engine
import os


def import_weather_csv_to_db(csv_file="weather_data.csv"):
    """
    Import weather data from CSV file to SQL Server database
    """
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        return False

    try:
        # Database connection details
        server = r"localhost"  # Server name or IP address
        database = "DEP1_DWH"  # Database name

        # Create connection with Windows Authentication
        engine = create_engine(f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server")

        # Read CSV file
        print(f"Reading data from {csv_file}...")
        df_weather = pd.read_csv(csv_file)

        # Get weather station mapping from database
        print("Fetching weather station information...")
        weather_stations = pd.read_sql("SELECT WeatherStationID, WeatherStationKey FROM DimWeatherStation", engine)

        # Merge with weather station keys
        df_weather['WeatherStationID'] = df_weather['WeatherStationID'].astype(int)
        weather_stations['WeatherStationID'] = weather_stations['WeatherStationID'].astype(int)
        df_weather = df_weather.merge(weather_stations, on="WeatherStationID", how="left")

        # Check for missing station mappings
        missing_stations = df_weather[df_weather['WeatherStationKey'].isna()]['WeatherStationID'].unique()
        if len(missing_stations) > 0:
            print(f"Warning: {len(missing_stations)} weather stations not found in database: {missing_stations}")
            print("These records will be excluded from import.")
            df_weather = df_weather.dropna(subset=['WeatherStationKey'])

        # Format columns for FactWeather table
        fact_weather = df_weather.reindex(columns=[
            "DateKey", "TimeKey", "WeatherStationKey",
            "PrecipQuantity", "TempAvg", "TempMax", "TempMin",
            "TempGrassPt100Avg", "TempSoilAvg", "TempSoilAvg5cm",
            "TempSoilAvg10cm", "TempSoilAvg20cm", "TempSoilAvg50cm",
            "WindSpeed10m", "WindSpeedAvg30m", "WindGustsSpeed",
            "HumidityRelShelterAvg", "Pressure", "SunDuration",
            "ShortWaveFromSkyAvg", "SunIntAvg"
        ])

        # Import to database
        print(f"Importing {len(fact_weather)} records to FactWeather table...")
        fact_weather.to_sql("FactWeather", con=engine, if_exists="append", index=False)

        print("Import completed successfully.")
        return True

    except Exception as e:
        print(f"Error during import: {e}")
        return False


if __name__ == "__main__":
    # You can specify a different CSV file as an argument
    import sys

    csv_file = "../../data/input/weather_data.csv"

    import_weather_csv_to_db(csv_file)
