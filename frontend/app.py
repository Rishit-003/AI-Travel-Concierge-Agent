import streamlit as st
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
            start_location = st.text_input("Starting Location", placeholder="e.g., New York, USA")
        with col2:
            destination = st.text_input("Destination", placeholder="e.g., Tokyo, Japan")

        # 3 & 4. Dates
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("Trip Start Date", value=date.today())
        with col4:
            end_date = st.date_input("Trip End Date", value=date.today())

        # 5. Travel Preferences (Checkboxes)
        st.write("---")
        st.subheader("Travel Preferences")
        
        pref_col1, pref_col2 = st.columns(2)
        
        with pref_col1:
            budget = st.checkbox("Budget travel")
            luxury = st.checkbox("Luxury travel")
            adventure = st.checkbox("Adventure")
            nature = st.checkbox("Nature")
            history = st.checkbox("Historical places")
            
        with pref_col2:
            food = st.checkbox("Food exploration")
            family = st.checkbox("Family friendly")
            solo = st.checkbox("Solo travel")
            nightlife = st.checkbox("Nightlife")
            shopping = st.checkbox("Shopping")

        # 6. Other Preferences
        other_prefs = st.text_area("Other Preferences", placeholder="e.g., Pet friendly, wheelchair accessible, specific dietary needs...")

        # 7. Submit Button
        submit_button = st.form_submit_button(label="Plan My Trip")

    # Logic after submission
    if submit_button:
        # Input Validation: Ensure dates are logical
        if end_date < start_date:
            st.error("Error: End Date cannot be before Start Date.")
        elif not start_location or not destination:
            st.warning("Please provide both a starting location and a destination.")
        else:
            # Calculate total days
            total_days = (end_date - start_date).days + 1

            # Collect checkbox preferences
            pref_map = {
                "Budget travel": budget, "Luxury travel": luxury, "Adventure": adventure,
                "Nature": nature, "Historical places": history, "Food exploration": food,
                "Family friendly": family, "Solo travel": solo, "Nightlife": nightlife,
                "Shopping": shopping
            }
            
            selected_prefs = [name for name, checked in pref_map.items() if checked]
            
            # Combine checkbox prefs and text area prefs
            final_prefs_list = selected_prefs.copy()
            if other_prefs.strip():
                final_prefs_list.append(other_prefs.strip())

            # Handle empty preferences
            if not final_prefs_list:
                display_prefs = "Balanced travel"
            else:
                display_prefs = ", ".join(final_prefs_list)

            # Display Trip Summary
            st.success("Form Submitted Successfully!")
            st.markdown("---")
            st.subheader("📋 Trip Summary")
            
            st.write(f"**From:** {start_location}")
            st.write(f"**To:** {destination}")
            st.write(f"**Start Date:** {start_date}")
            st.write(f"**End Date:** {end_date}")
            st.write(f"**Total Days:** {total_days}")
            
            st.write("**Preferences:**")
            st.info(display_prefs)

if __name__ == "__main__":
    main()