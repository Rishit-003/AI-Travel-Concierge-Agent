from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import GEMINI_API_KEY
from langchain.tools import tool
from backend.rag.vector_store import load_vector_store

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY
)

@tool("generate_trip_plan")
def generate_trip_plan(
    start_location,
    destination,
    start_date,
    end_date,
    total_days,
    display_transport,
    display_accommodation,
    display_prefs
):
    """
    Generates a detailed day-by-day travel itinerary based on user inputs such as
    location, dates, transport preferences, accommodation, and travel style.
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
    try:
        response = llm.invoke(prompt)
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