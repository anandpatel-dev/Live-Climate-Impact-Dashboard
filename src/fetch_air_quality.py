from pathlib import Path
from datetime import datetime, timezone
import json
import time

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

OUTPUT_FILE = PROCESSED_DIR / "air_quality_current.csv"

CITIES = {
    "Satna": (24.58, 80.83),
    "Bhopal": (23.26, 77.41),
    "Delhi": (28.61, 77.21),
    "Mumbai": (19.08, 72.88),
}


def main():
    records = []
    fetched_at = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    with requests.Session() as session:
        for city, coordinates in CITIES.items():
            latitude, longitude = coordinates

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "pm2_5,pm10,us_aqi",
                "timezone": "Asia/Kolkata",
            }

            print(f"Fetching air quality for {city}...")

            try:
                response = session.get(
                    API_URL,
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                payload = response.json()

                raw_file = (
                    RAW_DIR
                    / f"{city.lower()}_air_quality_latest.json"
                )

                raw_file.write_text(
                    json.dumps(payload, indent=2),
                    encoding="utf-8",
                )

                current = payload.get("current", {})

                if not current or not current.get("time"):
                    print(f"  No current data returned for {city}.")
                    continue

                record = {
                    "city": city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "observation_time": current.get("time"),
                    "pm2_5_ug_m3": current.get("pm2_5"),
                    "pm10_ug_m3": current.get("pm10"),
                    "us_aqi": current.get("us_aqi"),
                    "source": "Open-Meteo Air Quality API",
                    "fetched_at_utc": fetched_at,
                }

                records.append(record)
                print(
                    f"  PM2.5: {record['pm2_5_ug_m3']}, "
                    f"PM10: {record['pm10_ug_m3']}, "
                    f"US AQI: {record['us_aqi']}"
                )

            except (requests.RequestException, ValueError) as error:
                print(f"  Failed for {city}: {error}")

            time.sleep(1)

    if not records:
        raise RuntimeError(
            "No air-quality data collected. "
            "Check your internet connection and API response."
        )

    new_data = pd.DataFrame(records)

    if OUTPUT_FILE.exists():
        old_data = pd.read_csv(OUTPUT_FILE)

        combined = pd.concat(
            [old_data, new_data],
            ignore_index=True,
        )
    else:
        combined = new_data

    combined = combined.drop_duplicates(
        subset=["city", "observation_time"],
        keep="last",
    )

    combined = combined.sort_values(
        ["city", "observation_time"]
    )

    combined.to_csv(OUTPUT_FILE, index=False)

    print("\nAir-quality collection complete.")
    print("Cities fetched:", new_data["city"].nunique())
    print("New records:", len(new_data))
    print("Total saved records:", len(combined))
    print("CSV file:", OUTPUT_FILE)
    print("\nLatest fetched data:")
    print(new_data.to_string(index=False))


if __name__ == "__main__":
    main()