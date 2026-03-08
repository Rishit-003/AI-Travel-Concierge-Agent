from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY
)


def generate_trip_plan(
        start_location,
        destination,
        start_date,
        end_date,
        total_days,
        display_transport,
        display_Accomodation,
        display_prefs
):

    prompt = f"""
You are an intelligent AI Travel Planner.

Your task is to generate a personalized travel itinerary based on the user's trip details.

User Trip Details:
Starting Location: {start_location}
Destination: {destination}
Start Date: {start_date}
End Date: {end_date}
Total Days: {total_days}

Transportation Options: {display_transport}
Accommodation Preference: {display_Accomodation}

User Preferences:
{display_prefs}

Instructions:

1. Use the total number of days to generate a complete itinerary.
2. If user preferences are provided, prioritize them when selecting attractions, food, and activities.
3. If preferences are not provided, generate a balanced itinerary including:
   - Popular attractions
   - Local food experiences
   - Cultural experiences
   - Relaxation time

4. Generate a day-by-day itinerary.

For each day include:
- Places to visit
- Activities
- Food suggestions
- Travel tips

5. Additional information to include:
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

    response = llm.invoke(prompt)

    return response.content