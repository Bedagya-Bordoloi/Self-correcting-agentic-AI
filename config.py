import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# System Configuration
MAX_RETRIES = 5
ACCEPTANCE_THRESHOLD = 0.2
MODEL_NAME = "gemini-2.5-flash"             # ← this is the correct, working name for your key

# Rate Limiting Configuration
RATE_LIMIT_BASE_DELAY = 5.0                 # Base delay in seconds when rate limited
RATE_LIMIT_BACKOFF_MULTIPLIER = 1.5         # Exponential backoff multiplier for consecutive rate limits
INITIAL_RATE_LIMIT_DELAY = 60.0             # Default delay if not specified in error

# Securely load the Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

# Shared client
client = genai.Client(api_key=GOOGLE_API_KEY)

LOG_DB_PATH = "experiment_logs.json"