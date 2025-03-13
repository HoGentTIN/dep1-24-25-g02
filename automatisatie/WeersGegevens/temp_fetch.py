from datetime import datetime, timedelta
import pandas as pd
import requests
import time
import os
import random


def get_start_date():
    # Define a start date for data collection
    # If a CSV already exists, get the latest date from it
    csv_file = "weather_data.csv"
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            if not df.empty and 'DateKey' in df.columns:
                last_date = df['DateKey'].max()
                return str(last_date) if pd.notna(last_date) else (datetime.now() - timedelta(days=7)).strftime(
                    "%Y%m%d")
        except Exception as e:
            print(f"Error reading existing CSV: {e}")

    # Default to 7 days ago if no CSV exists or can't be read
    return (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")


def find_missing_dates(last_date):
    # Determine missing dates from the last available date until yesterday
    start_date = datetime.strptime(last_date, "%Y%m%d") + timedelta(days=1)
    end_date = datetime.now() - timedelta(days=1)
    missing_dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d").tolist()
    return missing_dates


def fetch_weather_data(date, max_retries=3, initial_delay=5):
    # Fetch weather data for a specific date with retry logic
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            print(f"Fetching data for: {date} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(
                f"https://opendata.meteo.be/service/ows?service=WFS&version=2.0.0&request=GetFeature&typenames=aws:aws_1day&outputformat=application/json&CQL_FILTER=(timestamp between '{date} 00:00:00' AND '{date} 23:59:59')"
            )
            print(f"Status code: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    records = data.get("features", [])
                    if records:
                        return records
                    else:
                        print(f"No data found for {date}")
                except Exception as e:
                    print(f"Error processing JSON for {date}: {e}")
            else:
                print(f"Failed to fetch data for {date}. Status code: {response.status_code}")

            # If we're here, we need to retry
            if attempt < max_retries - 1:  # Don't sleep after the last attempt
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                # Exponential backoff with jitter
                delay = delay * 2 + random.uniform(0, 1)

        except Exception as e:
            print(f"Exception during fetch for {date}: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay = delay * 2 + random.uniform(0, 1)

    print(f"All retries failed for {date}")
    return []


def process_weather_data(records):
    # Convert API response to a DataFrame with the correct columns
    if not records:
        return pd.DataFrame()

    data = [feature["properties"] for feature in records]
    df = pd.DataFrame(data)

    # Format date and time columns
    df['DateKey'] = df['timestamp'].str[:4] + df['timestamp'].str[5:7] + df['timestamp'].str[8:10]
    df['TimeKey'] = df['timestamp'].str[11:13] + df['timestamp'].str[14:16] + df['timestamp'].str[17:19]

    # Rename code to WeatherStationID
    df.rename(columns={'code': 'WeatherStationID'}, inplace=True)

    # Reorder columns to match expected format
    columns = ["DateKey", "TimeKey", "WeatherStationID", "PrecipQuantity", "TempAvg", "TempMax", "TempMin",
               "TempGrassPt100Avg", "TempSoilAvg", "TempSoilAvg5cm", "TempSoilAvg10cm",
               "TempSoilAvg20cm", "TempSoilAvg50cm", "WindSpeed10m", "WindSpeedAvg30m",
               "WindGustsSpeed", "HumidityRelShelterAvg", "Pressure", "SunDuration", "ShortWaveFromSkyAvg",
               "SunIntAvg"]

    # Map the actual column names to the desired column names
    column_mapping = {
        'precip_quantity': 'PrecipQuantity',
        'temp_avg': 'TempAvg',
        'temp_max': 'TempMax',
        'temp_min': 'TempMin',
        'temp_grass_pt100_avg': 'TempGrassPt100Avg',
        'temp_soil_avg': 'TempSoilAvg',
        'temp_soil_avg_5cm': 'TempSoilAvg5cm',
        'temp_soil_avg_10cm': 'TempSoilAvg10cm',
        'temp_soil_avg_20cm': 'TempSoilAvg20cm',
        'temp_soil_avg_50cm': 'TempSoilAvg50cm',
        'wind_speed_10m': 'WindSpeed10m',
        'wind_speed_avg_30m': 'WindSpeedAvg30m',
        'wind_gusts_speed': 'WindGustsSpeed',
        'humidity_rel_shelter_avg': 'HumidityRelShelterAvg',
        'pressure': 'Pressure',
        'sun_duration': 'SunDuration',
        'short_wave_from_sky_avg': 'ShortWaveFromSkyAvg',
        'sun_int_avg': 'SunIntAvg'
    }

    # Rename columns according to mapping
    df.rename(columns=column_mapping, inplace=True)

    # Only include columns that exist in the data
    available_columns = [col for col in columns if col in df.columns]
    df = df.reindex(columns=available_columns)

    return df.dropna(subset=["DateKey", "WeatherStationID"])


def save_to_csv(df, filename="weather_data.csv"):
    # Save DataFrame to CSV, appending if the file exists
    if df.empty:
        print("No data to save.")
        return

    if os.path.exists(filename):
        # Read existing CSV to check for duplicates
        existing_df = pd.read_csv(filename)

        # Combine and remove duplicates
        combined_df = pd.concat([existing_df, df]).drop_duplicates()

        # Save the combined data
        combined_df.to_csv(filename, index=False)
        print(f"Added {len(df)} records to {filename}. Total records: {len(combined_df)}")
    else:
        # Create new CSV
        df.to_csv(filename, index=False)
        print(f"Created new file {filename} with {len(df)} records.")


# Main process
def main():
    start_date = get_start_date()
    missing_dates = find_missing_dates(start_date)

    if not missing_dates:
        print("No new dates to process.")
        return

    print(f"Processing {len(missing_dates)} dates from {missing_dates[0]} to {missing_dates[-1]}")

    all_weather_data = pd.DataFrame()

    for date in missing_dates:
        # Fetch data with retry logic
        weather_records = fetch_weather_data(date)

        if weather_records:
            # Process the data
            df_weather = process_weather_data(weather_records)

            if not df_weather.empty:
                # Append to our collection
                all_weather_data = pd.concat([all_weather_data, df_weather])

        # Add a delay between requests to avoid overloading the API
        time.sleep(3)

    # Save all collected data to CSV
    if not all_weather_data.empty:
        save_to_csv(all_weather_data)
    else:
        print("No data was collected.")


if __name__ == "__main__":
    main()
