
from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "weather_forecast.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "weather_cleaned.csv"
DB_FILE = BASE_DIR / "data" / "climate.db"

def main():
    if not INPUT_FILE.exists():
        print("Weather CSV not found. Run fetch_weather.py first.")
        return

    # Load collected data
    df = pd.read_csv(INPUT_FILE)

    print("Original rows:", len(df))

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Convert date and numeric fields
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_columns = [
        "max_temperature_c",
        "min_temperature_c",
        "precipitation_mm",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove records without essential fields
    df = df.dropna(
        subset=[
            "date",
            "city",
            "max_temperature_c",
            "min_temperature_c",
        ]
    )

    # Remove duplicate city/date records
    df = df.drop_duplicates(subset=["city", "date"])

    # Validate temperature ranges and rainfall
    df = df[
        df["max_temperature_c"].between(-90, 65)
        & df["min_temperature_c"].between(-90, 65)
        & (df["precipitation_mm"].isna()
           | df["precipitation_mm"].ge(0))
    ].copy()

    # Store date in consistent YYYY-MM-DD format
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Save cleaned CSV
    df.to_csv(OUTPUT_FILE, index=False)

    # Store cleaned records in SQLite
    with sqlite3.connect(DB_FILE) as connection:
        df.to_sql(
            "weather_forecast",
            connection,
            if_exists="replace",
            index=False,
        )

    print("Cleaned rows:", len(df))
    print("CSV saved:", OUTPUT_FILE)
    print("Database saved:", DB_FILE)
    print("\nPreview:")
    print(df.head().to_string(index=False))

if __name__ == "__main__":
    main()