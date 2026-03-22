from backend.config import GEMINI_API_KEY
from langchain.tools import tool
from backend.weather_service import build_trip_weather_report, compact_weather_for_prompt

_planning_llm = None


def _get_planning_llm():
    global _planning_llm
    if _planning_llm is None:
        from langchain_google_genai import ChatGoogleGenerativeAI

        _planning_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
        )
    return _planning_llm

@tool("get_trip_weather")
def get_trip_weather(destination: str, start_date: str, end_date: str):
    """
    Fetches OpenWeatherMap forecast summaries for the destination between start_date and end_date.
    Use ISO dates YYYY-MM-DD. Call when the user gives trip dates and a destination and you need
    weather to tailor activities (rain gear, indoor backups, heat, etc.).
    """
    try:
        from datetime import datetime as dt_module

        s = dt_module.strptime(start_date.strip()[:10], "%Y-%m-%d").date()
        e = dt_module.strptime(end_date.strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        return "Invalid dates. Use YYYY-MM-DD for start_date and end_date."
    md, err = build_trip_weather_report(destination, s, e)
    if err:
        return f"Weather lookup failed: {err}"
    return compact_weather_for_prompt(md)


@tool("generate_trip_plan")
def generate_trip_plan(
    start_location,
    destination,
    start_date,
    end_date,
    total_days,
    display_transport,
    display_accommodation,
    display_prefs,
    weather_summary="No detailed weather forecast was provided.",
):
    """
    Generates a detailed day-by-day travel itinerary based on user inputs such as
    location, dates, transport preferences, accommodation, and travel style.
    Pass weather_summary from get_trip_weather or from the user's message when available.
    """
    prompt = f"""
You are an intelligent AI Travel Planner.

Your task is to generate a personalized travel itinerary based on the user's trip details.

User Trip Details:
Starting Location: {start_location}
Destination: {destination}
Start Date: {start_date}
End Date: {end_date}
Total Days: {total_days} days

Transportation Options: {display_transport}
Accommodation Preference: {display_accommodation}

User Preferences:
{display_prefs}

Weather context (use this to adjust daily plans — indoor alternatives if rain, lighter activities if extreme heat, layers if cold):
{weather_summary}

Instructions:
1. High priority to User preferences while generating the itinerary.
2. Use the total number of days to generate a complete itinerary.
3. If user preferences are provided, prioritize them when selecting attractions, food, and activities.
4. If preferences are not provided, generate a balanced itinerary including:
   - Popular attractions
   - Local food experiences
   - Cultural experiences
   - Relaxation time

5. Generate a day-by-day itinerary(in format of Day X and Date :- dd/mm/yyyy).

For each day include:
- Places to visit
- Activities
- Food suggestions
- Travel tips
- A short weather-aware note when forecast data is available (what to pack or schedule adjustments)

6. Additional information to include:
- Estimated travel distance between attractions
- Best transportation methods
- Tips for tourists
- Best visiting times for major attractions

Rules:
- Do not exceed the total number of trip days.
- Distribute attractions logically across days.
- Avoid repeating the same locations.
- Optimize travel time between places.
"""
    try:
        response = _get_planning_llm().invoke(prompt)
        return response.content if response else "No response generated."
    except Exception as e:
        return f"❌ Error generating plan: {str(e)}"

@tool("search_uploaded_documents")
def search_uploaded_documents(query: str):
    """
    Searches the uploaded documents (PDF/TXT) using vector similarity
    and returns the most relevant information based on the user query.
    """
    try:
        from backend.rag.vector_store import load_vector_store

        vector_store = load_vector_store()

        if not vector_store:
            return "No documents found. Please upload a file first."

        docs = vector_store.similarity_search(query, k=3)

        if not docs:
            return "No relevant information found in documents."

        content = "\n\n".join([d.page_content for d in docs])
        return content

    except Exception as e:
        return f"❌ Error searching documents: {str(e)}"