import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
from pathlib import Path
from src.utils.logger import logging
import sys
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from src.utils.weather_db import get_db_connection, create_weather_table,create_metrics_table
import sqlite3
import time
import argparse
from datetime import datetime, timezone, timedelta

# --------- Helper to mask API key from URLs and text content ---------
def mask_api_key(content, api_key):
    if not api_key:
        return content
    if isinstance(content, str):
        content = content.replace(api_key, "***REDACTED***")
        parts = content.split("appid=")
        if len(parts) > 1:
            for i in range(1, len(parts)):
                end_idx = parts[i].find("&")
                if end_idx != -1:
                    parts[i] = "***REDACTED***" + parts[i][end_idx:]
                else:
                    parts[i] = "***REDACTED***"
            content = "appid=".join(parts)
        return content
    elif isinstance(content, dict):
        return {k: mask_api_key(v, api_key) for k, v in content.items()}
    elif isinstance(content, list):
        return [mask_api_key(v, api_key) for v in content]
    return content

def fetch_and_store_weather(city, api_key, db_path, out_dir):
    params = {"appid": api_key, "q": city, "units": "metric"}
    url = "https://api.openweathermap.org/data/2.5/weather"

    try:
        resp = requests.get(url, params=params, timeout=15)
        safe_url = mask_api_key(resp.url, api_key)
        logging.info(f"Request sent to URL: {safe_url}")
    except requests.exceptions.RequestException as e:
        safe_msg = mask_api_key(str(e), api_key)
        logging.error(f"Network error: {safe_msg}")
        return

    if resp.status_code != 200:
        try:
            err_json = resp.json()
            safe_err = mask_api_key(err_json, api_key)
            logging.error(f"HTTP {resp.status_code}: {safe_err}")
        except Exception:
            safe_text = mask_api_key(resp.text, api_key)
            logging.error(f"HTTP {resp.status_code}: {safe_text}")
        return

    data = resp.json()
    logging.info(
        "Weather data (truncated): %s",
        {k: data.get(k) for k in ["name", "dt", "main", "weather"]}
    )

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_city = city.replace(" ", "_")
    path = out_dir / f"raw_{safe_city}_{ts}.json"

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Wrote data to file: {path}")
    except OSError as e:
        safe_msg = mask_api_key(str(e), api_key)
        logging.error(f"File write error: {safe_msg}")

    # Prepare data for database insertion
    if not data or "main" not in data or "weather" not in data:
        logging.error("Incomplete weather data received.")
        return

    city_name = data.get("name", "Unknown")
    city_id = str(data.get("id", "Unknown"))
    country = data.get("sys", {}).get("country", "Unknown")
    ts_utc = data.get("dt", 0)
    dt = data.get("dt", 0)
    date_str = datetime.fromtimestamp(dt, tz=timezone.utc).strftime("%Y-%m-%d") if dt else ""
    captured_at_utc = ts
    temp_c = data.get("main", {}).get("temp", -273.15)
    feels_like_c = data.get("main",{}).get("feels_like", -273.15)
    humidity = data.get("main", {}).get("humidity", 0)
    pressure = data.get("main", {}).get("pressure", 0)
    wind_speed = data.get("wind", {}).get("speed", 0)
    wind_deg = data.get("wind", {}).get("deg", 0)
    weather_main = data.get("weather", [{}])[0].get("main", "Unknown")
    weather_desc = data.get("weather", [{}])[0].get("description", "Unknown")

    conn = get_db_connection(db_path)
    if conn:
        create_weather_table(conn)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR IGNORE INTO weather_raw (
                    city_name, city_id, country, ts_utc,date_str, captured_at_utc,
                    temp_c, feels_like_c, humidity, pressure,
                    wind_speed, wind_deg, weather_main, weather_desc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                """,
                (
                    city_name,
                    city_id,
                    country,
                    ts_utc,
                    date_str,
                    captured_at_utc,
                    temp_c,
                    feels_like_c,
                    humidity,
                    pressure,
                    wind_speed,
                    wind_deg,
                    weather_main,
                    weather_desc,
                ),
            )
            conn.commit()
            if cursor.rowcount == 0:
                logging.info(f"[SKIP] city={city_name} event={ts_utc} reason=duplicate")
            else:
                logging.info(
                    f"[OK] city={city_name} event={ts_utc} captured={captured_at_utc} "
                    f"temp={temp_c}C hum={humidity}% wind={wind_speed}mps inserted"
                )
            logging.info("Weather data inserted into database.")
        except sqlite3.Error as e:
            logging.error(f"Database insert error: {e}")
        finally:
            cursor.close()
            conn.close()
def aggregate_weather_metrics(db_path, start_ts, end_ts):
    conn = get_db_connection(db_path)
    if conn:
            try:
                create_metrics_table(conn)

                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        CITY_NAME, 
                        DATE(DATETIME(TS_UTC, 'UNIXEPOCH')) AS DATE_UTC,
                        AVG(TEMP_C) AS AVG_TEMP,
                        MIN(TEMP_C) AS MIN_TEMP,
                        MAX(TEMP_C) AS MAC_TEMP,
                        AVG(HUMIDITY) AS AVG_HUMIDITY,
                        COUNT(*) AS SAMPLES
                    FROM WEATHER_RAW
                    WHERE TS_UTC BETWEEN ? AND ?
                    GROUP BY CITY_NAME, DATE_UTC;
                    """,(start_ts, end_ts))
                rows = cursor.fetchall()
                for row in rows:
                    city_name, date_utc, avg_temp, min_temp, max_temp, avg_humidity, samples = row
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO weather_metrics (
                            city_name, date_utc, avg_temp, min_temp, max_temp,
                            avg_humidity, samples
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (city_name, date_utc, avg_temp, min_temp, max_temp, avg_humidity, samples)
                    )
                    conn.commit()
                    logging.info(f"Aggregated {len(rows)} rows into weather_metrics.")
            except sqlite3.Error as e:
                logging.error(f"Database aggregation error: {e}")
                return 0
            finally:
                    cursor.close()
                    conn.close()
                    logging.info("Database connection closed.")

def run_once(cities, api_key, db_path, out_dir):
    for city in cities:
        try:
            fetch_and_store_weather(city, api_key, db_path, out_dir)
        except Exception as e:
            logging.error(f"Failed to process city '{city}': {e}")

def get_date_window_ts(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    start = int(datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc).timestamp())
    end = int((datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc) + timedelta(days=1)).timestamp()) - 1
    return start, end

def main():
    parser = argparse.ArgumentParser(description="Fetch weather data for multiple cities.")
    parser.add_argument("cities", nargs="+", help="City names to fetch weather for (e.g. London Paris 'New York')")
    parser.add_argument("--schedule", "-s", type=int, help="Run every N minutes(optional)")
    parser.add_argument("--aggregate", type=str, choices=["today", "yesterday"], help="Aggregate metrics for a date window (today, yesterday, or YYYY-MM-DD)")
    parser.add_argument("--aggregate-date", type=str, help="Aggregate metrics for a specific date (YYYY-MM-DD)")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logging.error("Missing OPENWEATHER_API_KEY in .env")
        sys.exit(1)

    db_path = "data/weather_database.db"
    out_dir = "data"

 
    if args.aggregate:
        if args.aggregate == "today":
            today = datetime.now(timezone.utc).date()
            start_ts, end_ts = get_date_window_ts(today.strftime("%Y-%m-%d"))
        elif args.aggregate == "yesterday":
            yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
            start_ts, end_ts = get_date_window_ts(yesterday.strftime("%Y-%m-%d"))
        aggregate_weather_metrics(db_path, start_ts, end_ts)
        sys.exit(0)
    elif args.aggregate_date:
        start_ts, end_ts = get_date_window_ts(args.aggregate_date)
        aggregate_weather_metrics(db_path, start_ts, end_ts)
        sys.exit(0)

    if args.schedule:
        try:
            while True:
                run_once(args.cities, api_key, db_path, out_dir)
                logging.info(f"Waiting for {args.schedule} minutes before next run...")
                time.sleep(args.schedule * 60)
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully. Bye!")
            sys.exit(0)
    else:
        if not args.cities:
            logging.error("No cities provided. Please specify at least one city.")
            sys.exit(1)
        else:
            # Run once without scheduling
            logging.info("Running once without scheduling...")
            run_once(args.cities, api_key, db_path, out_dir)

if __name__ == "__main__":
    main()
