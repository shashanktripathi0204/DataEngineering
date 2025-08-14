# Weather Data Fetcher & Aggregator

This Python script fetches weather data for one or more cities from the **OpenWeather API**, stores the raw data locally as JSON files, saves it into an SQLite database, and optionally aggregates daily weather metrics. A **Streamlit dashboard** is also provided to visualize the stored weather data.

## Features
- **Fetch weather data** from the [OpenWeather API](https://openweathermap.org/api)
- **Store raw JSON files** with timestamped filenames
- **Save weather data** in an SQLite database
- **Aggregate daily metrics** (average, min, max temperature, humidity, etc.)
- **Run once or schedule** periodic fetching
- **Secure API key handling** with masking in logs
- **Visualize data** with an interactive **Streamlit dashboard**

---

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt

**requirements.txt**
```
requests
python-dotenv
streamlit
pandas
```
> Note: SQLite is part of Python’s standard library.

---

## Environment Variables

Create a `.env` file in the project root with:

```
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

---

## Database

The script uses `data/weather_database.db` as the SQLite database.

Two tables are managed:
- **weather_raw** → stores raw weather data
- **weather_metrics** → stores aggregated daily weather metrics

---

```
## Usage

### 1. Run the Ingestor(main.py)
This script fetches and stores weather data.

#### Run Once (No Scheduling)
```bash
python weather_script.py London Paris "New York"
```
#### Run on Schedule
Fetch data every **N** minutes:
```bash
python weather_script.py London Paris -s 30
```
> Fetches every 30 minutes until stopped.

#### Aggregate Today's Metrics
```bash
python weather_script.py --aggregate today
```

#### Aggregate Yesterday's Metrics
```bash
python weather_script.py --aggregate yesterday
```

#### Aggregate Specific Date
```bash
python weather_script.py --aggregate-date 2025-08-10
```
### 2. Run the Streamlit Dashboard (app.py)
This script visualizes the data stored in the database.

#### Start the dashboard:
```bash
streamlit run dashboard/app.py
```

The dashboard offers two views:

Last 24h (raw): Shows a line chart of raw temperature and humidity data from the last 24 hours.

Daily (metrics): Displays charts of aggregated daily metrics (min, max, and average temperature, and average humidity). You can adjust the number of days to view.
---

## Script Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `cities` | list | One or more city names |
| `--schedule`, `-s` | int | Interval in minutes between fetches |
| `--aggregate` | str | Aggregate metrics for `today` or `yesterday` |
| `--aggregate-date` | str | Aggregate metrics for a specific date (YYYY-MM-DD) |

---

## Example

Fetch weather for **Delhi** and **Mumbai** every 10 minutes:
```bash
python weather_script.py Delhi Mumbai -s 10
```

Aggregate metrics for **2025-08-13**:
```bash
python weather_script.py --aggregate-date 2025-08-13
```

---

## Logging

Logs are handled via the `src.utils.logger` module and show:
- API requests (API keys masked)
- Database insertions
- Errors and warnings

---

## File Structure

```
.
├── app.py                  # dashboard logic
├── data/                   # Stores database & raw JSON files
├── src/
│   └── utils/
│       ├── logger.py       # Logging configuration
│       └── weather_db.py   # DB connection and table creation
├── .env                    # Contains API key
├── weather_script.py       # Main script
├── requirements.txt
└── README.md
```

---

## License
This project is for educational and personal use.
