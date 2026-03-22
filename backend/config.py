import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Get OpenWeatherMap API Key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Validate API Keys
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY is not set in the .env file")

if not WEATHER_API_KEY:
    print("⚠️  WARNING: WEATHER_API_KEY is not set in the .env file. Weather features will be unavailable.")