import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Potluck Party Planner",
    page_icon="🍲",
    layout="centered",  # Centered layout looks better on mobile
    initial_sidebar_state="collapsed"
)

# Custom CSS for "Vibe Coding" aesthetics
st.markdown("""
    <style>
        .stApp {
            background-color: #144228;
            color: white;
        }
        .main-header {
            font-family: 'Brush Script MT', cursive;
            font-size: 3.5rem;
            font-weight: 700;
            color: #D4AF37; /* Festive Gold */
            text-align: center;
            margin-bottom: -20px;
            text-shadow: 2px 2px 4px #000000;
        }
        /* Hide Streamlit Header/Top Bar and remove its space */
        header[data-testid="stHeader"] {
            display: none;
        }
        /* Hide Hamburger Menu and remove its space */
        #MainMenu {
            display: none;
        }
        /* Reduce top padding of the main container */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        /* Mobile Optimization */
        @media only screen and (max-width: 600px) {
            .main-header {
                font-size: 1.2rem !important; /* Further reduced for mobile */
                margin-bottom: 0px !important;
                margin-left: 3px !important;
                width: 100% !important;
                display: block !important;
                text-align: center !important;
            }
            h2 {
                font-size: 1.5rem !important;
            }
            h4 {
                font-size: 1rem !important;
            }
        }
        /* Removed broad text color rule to prevent conflict with Streamlit's internal UI */

        /* Specific override for the white food cards */
        .food-card, .food-card strong, .food-card span {
            color: black !important;
        }
        /* Custom styling for the submit button */
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #E74C3C !important; /* Softer Red */
            color: white !important;
            border-color: #E74C3C !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #C0392B !important; /* Darker red on hover */
            border-color: #C0392B !important;
        }
        .metric-card {
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }
        /* Mobile adjustment to ensure metrics don't squish too much */
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
    </style>

    <!-- Background Audio -->
    <audio autoplay loop hidden>
        <source src="https://actions.google.com/sounds/v1/holidays/jingle_bells.ogg" type="audio/ogg">
        Your browser does not support the audio element.
    </audio>
""", unsafe_allow_html=True)

# --- DATA HANDLING ---

# Establish connection
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    """Fetches data from Google Sheets with caching (TTL)."""
    try:
        df = conn.read(ttl=5)
        # Check if the dataframe is empty or missing expected columns
        expected_cols = ["Name", "Category", "Dish", "Note"]
        
        # If the sheet is completely empty or just has header row but no data, pandas might infer types weirdly.
        # If columns are missing, we initialize them.
        if df.empty or not set(expected_cols).issubset(df.columns):
            return pd.DataFrame(columns=expected_cols)
        
        # Fill NaN values to avoid errors in display
        return df.fillna("")
    except Exception as e:
        st.error(f"Could not load data. Check your connection secrets. Error: {e}")
        return pd.DataFrame(columns=["Name", "Category", "Dish", "Note"])

def add_entry(name, category, dish, note):
    """Adds a new entry to the Google Sheet."""
    df = get_data()
    
    # Duplicate Prevention (Case insensitive check on Dish name)
    if not df.empty and dish.lower().strip() in df['Dish'].str.lower().str.strip().values:
        return False, "This dish is already on the list! Please bring something else."

    new_entry = pd.DataFrame([{
        "Name": name,
        "Category": category,
        "Dish": dish,
        "Note": note
    }])
    
    updated_df = pd.concat([df, new_entry], ignore_index=True)
    conn.update(data=updated_df)
    return True, "Dish added successfully!"

# Load Data
df = get_data()

# --- HEADER & DASHBOARD (VISUAL HIERARCHY) ---
st.markdown("<h1 class='main-header'> 🎅🏾 Rish & Tina's 🤶🏻<br>🎄 Friendsmas Potluck 2025 🎄</h1>", unsafe_allow_html=True)

# --- CATEGORIZED DISPLAY (4 COLUMNS) ---
st.markdown("<h2 style='text-align: center; color: white;'>📋 The MENU (so far...)</h2>", unsafe_allow_html=True)

if df.empty:
    st.info("The list is empty! Be the first to add a dish below.")
else:
    col_sides, col_mains, col_desserts, col_drinks = st.columns(4)

    def display_category(column, title, categories):
        with column:
            st.markdown(f"**{title}**")
            # Filter data for the specific categories (list)
            cat_df = df[df['Category'].isin(categories)]
            
            if cat_df.empty:
                st.markdown(f"<em style='color:grey; font-size:0.8em'>None yet</em>", unsafe_allow_html=True)
            else:
                for _, row in cat_df.iterrows():
                    st.markdown(f"""
                    <div class="food-card" style="
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 8px;
                        margin-bottom: 8px;
                        background-color: #FFF8E7;
                        font-size: 0.9em;">
                        <div style="margin-bottom: 2px;"><strong>{row['Dish']}</strong></div>
                        <div style="color:gray; font-size:0.85em; margin-bottom: 2px;">{row['Name']}</div>
                        {f'<div style="font-size:0.8em; color: #555;">📝 {row["Note"]}</div>' if row["Note"] else ''}
                    </div>
                    """, unsafe_allow_html=True)

    # 1. Sides + Appetizers
    display_category(col_sides, "🥗 Sides & Apps", ["🥗 Sides", "🥨 Appetizers"])

    # 2. Mains
    display_category(col_mains, "🍗 Mains", ["🍗 Mains"])

    # 3. Desserts
    display_category(col_desserts, "🍰 Desserts", ["🍰 Dessert"])

    # 4. Drinks
    display_category(col_drinks, "🍺 Drinks", ["🍺 Drinks"])

st.divider()

# --- INPUT FORM ---
st.markdown("<h4 style='text-align: center; color: white;'> Add your dish below!</h4>", unsafe_allow_html=True)
with st.form("potluck_form", clear_on_submit=True, border=False):
    
    CATEGORIES = ["🍗 Mains", "🥗 Sides & Apps", "🍰 Dessert", "🍺 Drinks", "🥨 Appetizers"]
    f_category = st.selectbox("Category", CATEGORIES)
    
    f_dish = st.text_input("Dish Name", placeholder="e.g., Grandma's Lasagna")
    
    col1, col2 = st.columns(2)
    f_name = col1.text_input("Your Name", placeholder="e.g., Alex")
    f_partner = col2.text_input("Partner's Name (Optional)", placeholder="e.g., Sam")
    
    f_note = st.text_area("Dietary Notes (Optional)", placeholder="e.g., Vegetarian, Contains Nuts")
    
    submitted = st.form_submit_button("Bring it! 🔔", use_container_width=True)
    
    if submitted:
        if not f_name.strip():
            st.error("Please enter your name.")
        elif not f_dish.strip():
            st.error("Please tell us what you're bringing.")
        else:
            # Combine names
            full_name = f_name.strip()
            if f_partner.strip():
                full_name += f" & {f_partner.strip()}"
                
            success, message = add_entry(full_name, f_category, f_dish, f_note)
            if success:
                st.toast(message, icon="✅")
                st.balloons()
                # Clear cache so the new entry shows up immediately
                conn.reset()
                time.sleep(1) # Brief pause to let toast show before reload
                st.rerun()
            else:
                st.error(message)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Made with Streamlit 🎈</div>", unsafe_allow_html=True)
