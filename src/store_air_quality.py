from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "data" / "processed" / "air_quality_current.csv"
DB_FILE = BASE_DIR / "data" / "climate.db"


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Air-quality CSV not found: {CSV_FILE}"
        )

    df = pd.read_csv(CSV_FILE)

    required_columns = [
        "city",
        "latitude",
        "longitude",
        "observation_time",
        "pm2_5_ug_m3",
        "pm10_ug_m3",
        "us_aqi",
        "source",
        "fetched_at_utc",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing CSV columns: {missing}. "
            f"Found columns: {df.columns.tolist()}"
        )

    df = df[required_columns].copy()

    df["city"] = df["city"].astype("string").str.strip()

    numeric_columns = [
        "latitude",
        "longitude",
        "pm2_5_ug_m3",
        "pm10_ug_m3",
        "us_aqi",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    if df[["city", "observation_time"]].isna().any().any():
        raise ValueError("City or observation time is missing.")

    if df["city"].eq("").any():
        raise ValueError("An empty city name was found.")

    if df.duplicated(["city", "observation_time"]).any():
        raise ValueError(
            "Duplicate city and observation-time records found."
        )

    if df[numeric_columns].isna().any().any():
        raise ValueError(
            "Missing or invalid numeric air-quality values found."
        )

    if (df[["pm2_5_ug_m3", "pm10_ug_m3"]] < 0).any().any():
        raise ValueError("Negative particulate-matter values found.")

    if (df["us_aqi"] < 0).any():
        raise ValueError("Negative US AQI value found.")

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS air_quality (
            city TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            observation_time TEXT NOT NULL,
            pm2_5_ug_m3 REAL NOT NULL,
            pm10_ug_m3 REAL NOT NULL,
            us_aqi REAL NOT NULL,
            source TEXT NOT NULL,
            fetched_at_utc TEXT NOT NULL,
            PRIMARY KEY (city, observation_time)
        )
    """

    insert_sql = """
        INSERT INTO air_quality (
            city,
            latitude,
            longitude,
            observation_time,
            pm2_5_ug_m3,
            pm10_ug_m3,
            us_aqi,
            source,
            fetched_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(city, observation_time) DO UPDATE SET
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            pm2_5_ug_m3 = excluded.pm2_5_ug_m3,
            pm10_ug_m3 = excluded.pm10_ug_m3,
            us_aqi = excluded.us_aqi,
            source = excluded.source,
            fetched_at_utc = excluded.fetched_at_utc
    """

    records = list(
        df.itertuples(index=False, name=None)
    )

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute(create_table_sql)
        connection.executemany(insert_sql, records)

        total_rows = connection.execute(
            "SELECT COUNT(*) FROM air_quality"
        ).fetchone()[0]

        city_counts = connection.execute(
            """
            SELECT city, COUNT(*)
            FROM air_quality
            GROUP BY city
            ORDER BY city
            """
        ).fetchall()

        weather_tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN ('weather_forecast', 'historical_weather')
            ORDER BY name
            """
        ).fetchall()

    print("\nAir-quality data stored successfully!")
    print("Database:", DB_FILE)
    print("New CSV records processed:", len(df))
    print("Total records in air_quality:", total_rows)

    print("\nRecords per city:")
    for city, count in city_counts:
        print(f"{city}: {count}")

    print("\nExisting weather tables:")
    for (table_name,) in weather_tables:
        print(table_name)


if __name__ == "__main__":
    main()