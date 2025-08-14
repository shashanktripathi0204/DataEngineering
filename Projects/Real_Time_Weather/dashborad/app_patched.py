import os
import sys
import time
import sqlite3
from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils.logger import logging

DB_DEFAULT_PATH = "data/weather_database.db"

def open_conn(db_path: str):
    """Open a SQLite connection with row access by column name."""
    logging.info(f"Opening database connection to: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data(ttl=30)
def get_cities(db_path: str):
    """Fetch distinct city names from weather_raw."""
    try:
        with open_conn(db_path) as conn:
            rows = conn.execute(
                "SELECT DISTINCT city_name FROM weather_raw ORDER BY 1;"
            ).fetchall()
        return [r["city_name"] for r in rows]
    except Exception as e:
        logging.error(f"Error fetching cities: {e}")
        return []

@st.cache_data(ttl=30)
def get_last_24h(db_path: str, city: str):
    """Fetch last 24h weather data for a city."""
    now_utc = int(datetime.now(timezone.utc).timestamp())
    start = now_utc - 24 * 3600
    try:
        with open_conn(db_path) as conn:
            rows = conn.execute(
                """
                SELECT ts_utc, temp_c, humidity
                FROM weather_raw
                WHERE city_name = ? AND ts_utc >= ?
                ORDER BY ts_utc
                """,
                (city, start),
            ).fetchall()
        times = [datetime.fromtimestamp(r["ts_utc"], tz=timezone.utc) for r in rows]
        temps = [r["temp_c"] for r in rows]
        hums = [r["humidity"] for r in rows]
        return times, temps, hums
    except Exception as e:
        logging.error(f"Error fetching last 24h data for {city}: {e}")
        return [], [], []

@st.cache_data(ttl=60)
def get_daily_metrics(db_path: str, city: str, days: int = 14):
    """Fetch daily weather metrics for a city."""
    try:
        with open_conn(db_path) as conn:
            rows = conn.execute(
                """
                SELECT date_utc, avg_temp, min_temp, max_temp, avg_humidity, samples
                FROM weather_metrics
                WHERE city_name = ?
                ORDER BY date_utc DESC
                LIMIT ?
                """,
                (city, days),
            ).fetchall()
        rows = list(rows)[::-1]
        return (
            [r["date_utc"] for r in rows],
            [r["avg_temp"] for r in rows],
            [r["min_temp"] for r in rows],
            [r["max_temp"] for r in rows],
            [r["avg_humidity"] for r in rows],
            [r["samples"] for r in rows],
        )
    except Exception as e:
        logging.error(f"Error fetching daily metrics for {city}: {e}")
        return [], [], [], [], [], []

def main():
    logging.info("Starting Streamlit Weather Dashboard app")
    st.set_page_config(page_title="Weather Dashboard", page_icon="⛅", layout="wide")

    st.title("⛅ Weather Dashboard")
    st.caption("Backed by your SQLite database. All times are UTC.")

    # Sidebar controls
    st.sidebar.header("Controls")
    db_path = st.sidebar.text_input("Database path", DB_DEFAULT_PATH)

    if not db_path or not os.path.exists(db_path):
        st.error("Database path is invalid or does not exist.")
        st.stop()

    cities = get_cities(db_path)
    if not cities:
        st.info("No cities found in weather_raw yet. Let the ingestor run, then refresh.")
        st.stop()

    st.sidebar.divider()
    city = st.sidebar.selectbox("City", options=cities)
    view = st.sidebar.radio("View", options=["Last 24h (raw)", "Daily (metrics)"])
    st.sidebar.divider()
    st.sidebar.write(f"DB: {db_path}")

    if view == "Last 24h (raw)":
        times, temps, hums = get_last_24h(db_path, city)
        if not times:
            st.warning("No data in the last 24 hours for this city.")
            st.stop()

        st.subheader(f"Last 24 hours - {city}")
        df = pd.DataFrame({"time": times, "Temperature (°C)": temps, "Humidity (%)": hums})
        st.line_chart(df, x="time", y=["Temperature (°C)", "Humidity (%)"])

        with st.expander("Show data table"):
            st.dataframe(df, use_container_width=True)

    else:
        days = st.slider("Days", min_value=7, max_value=60, value=14, step=1)
        dates, avg_t, min_t, max_t, avg_h, samples = get_daily_metrics(db_path, city, days)
        if not dates:
            st.warning("No daily metrics yet. Run aggregation and try again.")
            st.stop()

        st.subheader(f"Daily metrics - {city}")
        temp_df = pd.DataFrame({"Date": dates, "Min (°C)": min_t, "Avg (°C)": avg_t, "Max (°C)": max_t})
        st.line_chart(temp_df, x="Date", y=["Min (°C)", "Avg (°C)", "Max (°C)"])

        hum_df = pd.DataFrame({"Date": dates, "Avg Humidity (%)": avg_h})
        st.line_chart(hum_df, x="Date", y="Avg Humidity (%)")

        with st.expander("Show metrics table"):
            st.dataframe(
                {
                    "Date": dates,
                    "Avg Temp": avg_t,
                    "Min Temp": min_t,
                    "Max Temp": max_t,
                    "Avg Humidity": avg_h,
                    "Samples": samples,
                },
                use_container_width=True,
            )

    st.caption("Tip: keep your ingestor running in another terminal. Re-run the daily aggregation to refresh metrics.")

if __name__ == "__main__":
    main()