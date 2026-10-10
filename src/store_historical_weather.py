from pathlib import Path
import sqlite3
from datetime import datetime, timezone

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "data" / "processed" / "historical_weather.csv"
DB_FILE = BASE_DIR / "data" / "climate.db"

TABLE_NAME = "historical_weather"

REQUIRED_COLUMNS = [
    "date",
    "city",
    "latitude",
    "longitude",
    "max_temperature_c",
    "min_temperature_c",
    "precipitation_mm",
]


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Historical CSV not found: {CSV_FILE}"
        )

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV_FILE)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV is missing required columns: {missing_columns}"
        )

    df = df[REQUIRED_COLUMNS].copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    numeric_columns = [
        "latitude",
        "longitude",
        "max_temperature_c",
        "min_temperature_c",
        "precipitation_mm",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    if df[["date", "city"]].isna().any().any():
        raise ValueError("CSV contains missing dates or city names.")

    if df.duplicated(["city", "date"]).any():
        raise ValueError("CSV contains duplicate city-date records.")

    if df[numeric_columns].isna().any().any():
        raise ValueError("CSV contains missing or invalid numeric values.")

    fetched_at = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    records = [
        (
            row.date,
            row.city,
            row.latitude,
            row.longitude,
            row.max_temperature_c,
            row.min_temperature_c,
            row.precipitation_mm,
            "Open-Meteo Historical Archive API",
            fetched_at,
        )
        for row in df.itertuples(index=False)
    ]

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS historical_weather (
            date TEXT NOT NULL,
            city TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            max_temperature_c REAL NOT NULL,
            min_temperature_c REAL NOT NULL,
            precipitation_mm REAL,
            source TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            PRIMARY KEY (city, date)
        )
    """

    insert_sql = """
        INSERT INTO historical_weather (
            date,
            city,
            latitude,
            longitude,
            max_temperature_c,
            min_temperature_c,
            precipitation_mm,
            source,
            fetched_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(city, date) DO UPDATE SET
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            max_temperature_c = excluded.max_temperature_c,
            min_temperature_c = excluded.min_temperature_c,
            precipitation_mm = excluded.precipitation_mm,
            source = excluded.source,
            fetched_at = excluded.fetched_at
    """

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute(create_table_sql)
        connection.executemany(insert_sql, records)

        total_rows = connection.execute(
            "SELECT COUNT(*) FROM historical_weather"
        ).fetchone()[0]

        city_counts = connection.execute(
            """
            SELECT city, COUNT(*)
            FROM historical_weather
            GROUP BY city
            ORDER BY city
            """
        ).fetchall()

        forecast_table_exists = connection.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'weather_forecast'
            """
        ).fetchone()[0] == 1

    print("\nHistorical data stored successfully!")
    print("Database:", DB_FILE)
    print("Rows processed from CSV:", len(records))
    print("Rows in historical_weather table:", total_rows)

    print("\nRecords per city:")
    for city, count in city_counts:
        print(f"{city}: {count}")

    print(
        "\nExisting weather_forecast table preserved:",
        "Yes" if forecast_table_exists else "Not found",
    )


if __name__ == "__main__":
    main()