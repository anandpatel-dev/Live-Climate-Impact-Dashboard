
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import pandas as pd

# folders added for raw and processed data
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Cities with their coordinates
CITIES = {
    "Satna": {"latitude": 24.58, "longitude": 80.83},
    "Bhopal": {"latitude": 23.26, "longitude": 77.41},
    "Delhi": {"latitude": 28.61, "longitude": 77.21},
    "Mumbai": {"latitude": 19.08, "longitude": 72.88},
}

API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(city, coordinates):
    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "wind_speed_10m",
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
        ],
        "timezone": "Asia/Kolkata",
        "forecast_days": 7,
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    # Save original API response
    raw_file = RAW_DIR / f"{city.lower()}_weather.json"
    with raw_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    # Convert daily data to a table
    daily = data["daily"]

    df = pd.DataFrame({
        "date": daily["time"],
        "city": city,
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "max_temperature_c": daily["temperature_2m_max"],
        "min_temperature_c": daily["temperature_2m_min"],
        "precipitation_mm": daily["precipitation_sum"],
    })

    # Save processed data
    return df, data["current"]


def main():
    all_weather = []

    for city, coordinates in CITIES.items():
        try:
            df, current = fetch_weather(city, coordinates)
            all_weather.append(df)

            print(f"\n{city}: SUCCESS")
            print(f"Current temperature: "
                  f"{current['temperature_2m']} °C")
            print(f"Humidity: "
                  f"{current['relative_humidity_2m']}%")

        except (requests.RequestException, KeyError, ValueError) as error:
            print(f"\n{city}: FAILED - {error}")

    if all_weather:
        result = pd.concat(all_weather, ignore_index=True)

        output_file = PROCESSED_DIR / "weather_forecast.csv"
        result.to_csv(output_file, index=False)

        print("\nData saved successfully!")
        print(f"Total rows: {len(result)}")
        print(f"File location: {output_file}")
        print(result.head(10).to_string(index=False))
    else:
        print("\nNo data was collected. Check your internet connection.")


if __name__ == "__main__":
    main()