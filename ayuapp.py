import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Ayurveda Treatment Center",
    page_icon="🌿",
    layout="centered"
)

# ---------------------------------------------------------
# Database Connection (Google Sheets)
# ---------------------------------------------------------
@st.cache_resource
def get_gsheet_connection():
    # Define required Google Sheets API scopes
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Retrieve credentials configured in Streamlit Secrets (.streamlit/secrets.toml)
    credentials_info = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    
    # Authorize gspread client and open spreadsheet
    client = gspread.authorize(credentials)
    spreadsheet_url = st.secrets["spreadsheet_url"]
    sheet = client.open_by_url(spreadsheet_url).sheet1
    return sheet

# Initialize connection with graceful error handling
try:
    sheet = get_gsheet_connection()
except Exception:
    sheet = None

# ---------------------------------------------------------
# UI Layout & Navigation
# ---------------------------------------------------------
st.title("🌿 Ayurveda Treatment Center")

# Navigation tabs
tab_info, tab_book, tab_admin = st.tabs(["About Us", "Book Appointment", "Admin Portal"])

# ---------------------------------------------------------
# Tab 1: Business Details
# ---------------------------------------------------------
with tab_info:
    st.header("Welcome to Our Healing Center")
    st.markdown("""
    Experience authentic Ayurvedic treatments designed to restore balance and vitality to your body and mind.
    
    ### 🌿 Treatments Offered
    * **Herbal Steam Baths** — Rejuvenating herbal steam sessions
    * **Abhyanga** — Full body herbal oil massage
    * **Panchakarma** — Complete detoxification therapies
    
    ---
    ### 📍 Center Location & Hours
    * **Location:** Pallimulla,Panadura, Sri Lanka
    * **Opening Hours:** Saturday – 09:00 AM – 13:00 PM |  17:00 PM - 21:00 PM
                         Sunday – 09:00 AM – 13:00 PM | 17:00 PM - 21:00 PM
                         Monday - 05:00 PM - 09:00 PM
                         Tuesday - 09:00AM - 13:00PM | 17:00 PM - 21:00 PM
                         Wednesday -  - 09:00AM - 13:00PM | 17:00 PM - 21:00 PM
                         Thursday - - 09:00AM - 13:00PM | 17:00 PM - 21:00 PM
                         Friday - 05:00 PM - 09:00 PM
    * **Contact Phone:** +94 76 313 0817  |  +94 72 350 4585
    * **Email:** fernandrasanga@gmail.com
    """)

# ---------------------------------------------------------
# Tab 2: Customer Booking Form
# ---------------------------------------------------------
with tab_book:
    st.header("Book Your Visit")
    
    with st.form("booking_form", clear_on_submit=True):
        full_name = st.text_input("Full Name*")
        phone_number = st.text_input("Phone Number*")
        email_address = st.text_input("Email Address")
        
        treatment_selected = st.selectbox(
            "Select Treatment*",
            ["Herbal Steam Bath", "Abhyanga Massage", "Panchakarma Therapy", "General Consultation", "Nasna Karma", "Other"]
        )
        
        booking_date = st.date_input("Preferred Date*", min_value=date.today())
        booking_time = st.selectbox(
            "Preferred Time Slot*",
            ["09:00 AM", "11:00 AM", "02:00 PM", "04:00 PM"]
        )
        additional_notes = st.text_area("Special Notes or Medical Concerns (Optional)")
        
        submitted = st.form_submit_button("Submit Booking Request")
        
        if submitted:
            if not full_name or not phone_number:
                st.error("Please fill in all required fields (Name and Phone Number).")
            elif sheet is None:
                st.error("Database connection missing. Please configure Streamlit Secrets.")
            else:
                try:
                    # Append new booking row to Google Sheet
                    row_data = [
                        full_name,
                        phone_number,
                        email_address,
                        treatment_selected,
                        str(booking_date),
                        booking_time,
                        additional_notes
                    ]
                    sheet.append_row(row_data)
                    st.success("Your booking request has been submitted successfully! We will contact you shortly to confirm.")
                except Exception as err:
                    st.error(f"Failed to submit booking: {err}")

# ---------------------------------------------------------
# Tab 3: Restricted Admin Dashboard
# ---------------------------------------------------------
with tab_admin:
    st.header("Admin Dashboard")
    
    # Store admin authentication state
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
        
    if not st.session_state.admin_authenticated:
        # Password login prompt
        admin_password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            # Fetch password securely from Streamlit secrets
            correct_password = st.secrets.get("admin_password", "default_admin_pass")
            if admin_password == correct_password:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    else:
        st.success("Authenticated as Administrator")
        
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
            
        st.subheader("Current Customer Bookings")
        
        if sheet is not None:
            try:
                # Fetch all recorded rows from Google Sheet
                records = sheet.get_all_records()
                if records:
                    df = pd.DataFrame(records)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No bookings recorded yet.")
            except Exception as err:
                st.error(f"Error fetching bookings data: {err}")
        else:
            st.error("Google Sheets connection unavailable.")
