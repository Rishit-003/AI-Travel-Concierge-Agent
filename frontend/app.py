import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from backend.agent.tools import generate_trip_plan
from datetime import date
def main():
    # Set page configuration
    st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")

    st.title("🌍 AI Travel Planner")
    st.markdown("Fill in the details below to generate your custom travel itinerary.")

    # Create the input form
    with st.form("travel_form"):
        st.subheader("Trip Details")
        
        # 1 & 2. Starting Location and Destination
        col1, col2 = st.columns(2)
        with col1:
            start_location = st.text_input("Starting Location", placeholder="e.g., Ahmedabad, Vadodara")
        with col2:
            destination = st.text_input("Destination", placeholder="e.g., Mumbai, Manali")

        # 3 & 4. Dates
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("Trip Start Date", value=date.today())
        with col4:
            end_date = st.date_input("Trip End Date", value=date.today())
        
        #5
        st.write("---")

        st.subheader("✈️ Travel & Accommodation")
        transport_options = st.multiselect(
        "How do you plan to travel?",
        ["Own Vehicle", "Flight", "Train", "Bus", "Rental Car", "Public Transport"],
         help="Options to reach your destination"
        )

        accommodation_type = st.multiselect(
        "Preferred Stay",
         ["Hotel", "Apartment/Airbnb", "Hostel", "Resort", "Camping"],
         help="Options For Stay in your destination"
        )

        # 5. Travel Preferences (Checkboxes)
        st.write("---")
        st.subheader("🎨 Experience & Preferences")

        # More realistic and diverse options
        preference_options = [
    "Couple 👩‍❤️‍👨", "Solo Travel 🧘", "Family Friendly 👨‍👩‍👧‍👦", 
    "Non-Veg 🍗", "Vegetarian 🥗", "Vegan 🌱",
    "Budget 💰", "Luxury ✨", "Adventure 🧗", 
    "Nature 🌿", "Historical 🏛️", "Food Exploration 🍜", 
    "Nightlife 💃", "Shopping 🛍️", "Pet Friendly 🐾"
    ]

        selected_prefs = st.multiselect(
        "Choose your travel style and dietary preferences:",
        options=preference_options,
        placeholder="Select Preference"
         )

        # 6. Other Preferences
        other_prefs = st.text_area("Other Preferences", placeholder="e.g., Pet friendly, wheelchair accessible, specific dietary needs...")

        # 7. Submit Button
        submit_button = st.form_submit_button(label="Plan My Trip")

    # Logic after submission    

    if submit_button:
      if end_date < start_date:
        st.error("Error: End Date cannot be before Start Date.")
      elif not start_location or not destination:
        st.warning("Please provide both a starting location and a destination.")
      else:
        total_days = (end_date - start_date).days + 1

        # Combine multiselect tags with the custom text area
        all_prefs = selected_prefs.copy()
        if other_prefs.strip():
            all_prefs.append(other_prefs.strip())
        
        display_prefs = ", ".join(all_prefs) if all_prefs else "Balanced travel"
        display_transport = ", ".join(transport_options) if transport_options else "Not specified"
        display_Accomodation = ", ".join(accommodation_type) if accommodation_type else "Not specified"

        # Display Enhanced Summary
        st.success("Form Submitted Successfully!")
        st.markdown("---")
        st.subheader("📋 Trip Summary")
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.write(f"**From:** {start_location}")
            st.write(f"**To:** {destination}")
            st.write(f"**Total Days:** {total_days}")
        with col_right:
            st.write(f"**Start:** {start_date}")
            st.write(f"**End:** {end_date}")
            st.write(f"**Transport:** {display_transport}")
        
        st.write("**Accommodation:**")
        st.info(display_Accomodation)

        st.write("**Preferences & Style:**")
        st.info(display_prefs)
        
        with st.spinner("Generating your itinerary..."):
            trip_plan = generate_trip_plan(
                start_location,
                destination,
                start_date,
                end_date,
                total_days,
                display_transport,
                display_Accomodation,
                display_prefs
            )

        st.subheader("🤖 AI Generated Itinerary")
        st.write(trip_plan)
if __name__ == "__main__":
    main()