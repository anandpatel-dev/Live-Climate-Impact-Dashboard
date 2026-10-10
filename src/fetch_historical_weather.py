from pathlib import Path
import time

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://archive-api.open-meteo.com/v1/archive"

CITIES = {
    "Satna": (24.58, 80.83),
    "Bhopal": (23.26, 77.41),
    "Delhi": (28.61, 77.21),
    "Mumbai": (19.08, 72.88),
}

START_DATE = "2020-01-01"
END_DATE = "2025-12-31"


def main():
    all_records = []

    with requests.Session() as session:
        for city, coordinates in CITIES.items():
            latitude, longitude = coordinates

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": START_DATE,
                "end_date": END_DATE,
                "daily": (
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_sum"
                ),
                "timezone": "Asia/Kolkata",
            }

            print(f"Fetching historical data for {city}...")

            try:
                response = session.get(
                    API_URL,
                    params=params,
                    timeout=60,
                )
                response.raise_for_status()
                payload = response.json()

                raw_file = (
                    RAW_DIR
                    / f"{city.lower()}_historical_weather.json"
                )
                raw_file.write_text(
                    response.text,
                    encoding="utf-8",
                )

                daily = payload.get("daily", {})

                if not daily or not daily.get("time"):
                    print(f"No daily records returned for {city}.")
                    continue

                frame = pd.DataFrame({
                    "date": daily["time"],
                    "city": city,
                    "latitude": latitude,
                    "longitude": longitude,
                    "max_temperature_c": daily[
                        "temperature_2m_max"
                    ],
                    "min_temperature_c": daily[
                        "temperature_2m_min"
                    ],
                    "precipitation_mm": daily[
                        "precipitation_sum"
                    ],
                })

                frame["date"] = pd.to_datetime(
                    frame["date"],
                    errors="coerce",
                )

                numeric_columns = [
                    "max_temperature_c",
                    "min_temperature_c",
                    "precipitation_mm",
                ]

                for column in numeric_columns:
                    frame[column] = pd.to_numeric(
                        frame[column],
                        errors="coerce",
                    )

                frame = frame.dropna(
                    subset=[
                        "date",
                        "max_temperature_c",
                        "min_temperature_c",
                    ]
                )

                valid_temperature = (
                    frame["max_temperature_c"].between(-90, 65)
                    & frame["min_temperature_c"].between(-90, 65)
                )

                valid_precipitation = (
                    frame["precipitation_mm"].isna()
                    | frame["precipitation_mm"].ge(0)
                )

                frame = frame[
                    valid_temperature & valid_precipitation
                ].copy()

                frame["date"] = frame["date"].dt.strftime(
                    "%Y-%m-%d"
                )

                all_records.append(frame)
                print(f"  Valid records: {len(frame)}")

            except (
                requests.RequestException,
                ValueError,
                KeyError,
            ) as error:
                print(f"  Failed for {city}: {error}")

            time.sleep(1)

    if not all_records:
        raise RuntimeError(
            "No historical data collected. "
            "Check your internet connection and API response."
        )

    result = pd.concat(all_records, ignore_index=True)

    result = result.drop_duplicates(
        subset=["city", "date"]
    )

    result = result.sort_values(
        ["city", "date"]
    )

    output_file = PROCESSED_DIR / "historical_weather.csv"
    result.to_csv(output_file, index=False)

    print("\nHistorical weather collection complete.")
    print("Total rows:", len(result))
    print("Number of cities:", result["city"].nunique())
    print(
        "Date range:",
        result["date"].min(),
        "to",
        result["date"].max(),
    )
    print("Saved CSV:", output_file)

    print("\nPreview:")
    print(result.head(5).to_string(index=False))


if __name__ == "__main__":
    main()