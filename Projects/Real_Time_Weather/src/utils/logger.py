import logging
import os

print("=== INSIDE Logger.py ===")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/app.log',
    filemode='a',  # Overwrite on each run. Use 'a' for append.
    force=True
)

# --------- Lower urllib3 and requests log level to WARNING ---------
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# --------- Global API key redaction filter ---------
class ApiKeyFilter(logging.Filter):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
    def filter(self, record):
        # Redact API key in main log message
        if self.api_key and self.api_key in str(record.msg):
            record.msg = str(record.msg).replace(self.api_key, "***REDACTED***")
        # Redact API key in arguments (if used in formatting)
        if hasattr(record, 'args') and isinstance(record.args, tuple):
            record.args = tuple(
                a.replace(self.api_key, "***REDACTED***") if isinstance(a, str) and self.api_key in a else a
                for a in record.args
            )
        return True

api_key = os.getenv("OPENWEATHER_API_KEY")
if api_key:
    logging.getLogger().addFilter(ApiKeyFilter(api_key))

print("Logging is configured. You can now use the logging module in your scripts.")
