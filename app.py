from PIL import Image
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# ────────────────────────────────────────────────
# Page Config & Safe Logo
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="AgPilotApp – Aerial Application Performance Tool",
    page_icon="⌯✈︎",
    layout="wide",
    initial_sidebar_state="auto"
)

# Green preview theme
st.markdown("""
    <meta name="theme-color" content="#4CAF50">
    <link rel="icon" href="https://img.icons8.com/color/48/000000/helicopter.png" type="image/png">
""", unsafe_allow_html=True)

# Try to load custom logo from GitHub raw URL
LOGO_URL = "https://raw.githubusercontent.com/captn357417/agpilot-app/main/AgPilotApp.png"
try:
    st.logo(LOGO_URL, size="medium")
except Exception:
    try:
        st.logo("AgPilotApp.png", size="medium")  # fallback to local
    except Exception:
        st.markdown("### AgPilotApp ⌯✈︎ (logo not loaded – check file/URL)")

# ────────────────────────────────────────────────
# Session State Initialization
# ────────────────────────────────────────────────
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'custom_empty_weight' not in st.session_state:
    st.session_state.custom_empty_weight = None
if 'show_risk' not in st.session_state:
    st.session_state.show_risk = False

# ────────────────────────────────────────────────
# Aircraft Database
# ────────────────────────────────────────────────
AIRCRAFT_DATA = {
    "Air Tractor AT-502B": {
        "name": "Air Tractor AT-502B",
        "base_takeoff_ground_roll_ft": 1140,
        "base_takeoff_to_50ft_ft": 2600,
        "base_landing_ground_roll_ft": 600,
        "base_landing_to_50ft_ft": 1350,
        "base_climb_rate_fpm": 870,
        "base_stall_flaps_down_mph": 68,
        "best_climb_speed_mph": 111,
        "base_empty_weight_lbs": 4546,
        "base_fuel_capacity_gal": 170,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 500,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 9400,
        "max_landing_weight_lbs": 8000,
        "glide_ratio": 8.0,
        "description": "Single-engine piston ag aircraft"
    },
    "Air Tractor AT-602": {
        "name": "Air Tractor AT-602",
        "base_takeoff_ground_roll_ft": 1400,
        "base_takeoff_to_50ft_ft": 2800,
        "base_landing_ground_roll_ft": 850,
        "base_landing_to_50ft_ft": 1850,
        "base_climb_rate_fpm": 1050,
        "base_stall_flaps_down_mph": 74,
        "best_climb_speed_mph": 118,
        "base_empty_weight_lbs": 6200,
        "base_fuel_capacity_gal": 380,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 600,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 12500,
        "max_landing_weight_lbs": 11000,
        "glide_ratio": 7.2,
        "description": "Turbine ag aircraft – balanced payload & performance",
        "hover_ceiling_ige_max_gw": 0,
        "hover_ceiling_oge_max_gw": 0
    },
    # ... (all other aircraft entries remain unchanged - keeping them out here for brevity)
    # Make sure to copy-paste ALL aircraft entries from your original file
}

# ────────────────────────────────────────────────
# Density Altitude Calculation (Enstrom 480 POH method)
# ────────────────────────────────────────────────
def calculate_density_altitude(pressure_alt_ft, oat_c):
    isa_temp_c = 15 - (2 * (pressure_alt_ft / 1000))
    deviation = oat_c - isa_temp_c
    da_ft = pressure_alt_ft + (120 * deviation)
    return round(da_ft)

# ────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────
def adjust_for_weight(value, current_weight, base_weight, exponent=1.5):
    return value * (current_weight / base_weight) ** exponent

def adjust_for_runway_condition(value, condition):
    multipliers = {
        "Paved / Dry Hard Surface": 1.00,
        "Dry Grass / Firm Turf": 1.15,
        "Wet Grass / Damp Turf": 1.45,
        "Soft / Muddy / Rough": 1.80
    }
    factor = multipliers.get(condition, 1.00)
    return value * factor

def adjust_for_wind(value, wind_kts):
    factor = 1 - (0.1 * wind_kts / 9)
    return value * max(factor, 0.5)

def adjust_for_da(value, da_ft):
    factor = 1 + (0.07 * da_ft / 1000)
    return value * factor

@st.cache_data
def compute_takeoff(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    ground_roll = adjust_for_weight(data["base_takeoff_ground_roll_ft"], weight_lbs, data["max_takeoff_weight_lbs"])
    ground_roll = adjust_for_da(ground_roll, da_ft)
    ground_roll = adjust_for_wind(ground_roll, wind_kts)
    ground_roll = adjust_for_runway_condition(ground_roll, runway_condition)
    to_50ft = adjust_for_weight(data["base_takeoff_to_50ft_ft"], weight_lbs, data["max_takeoff_weight_lbs"])
    to_50ft = adjust_for_da(to_50ft, da_ft)
    to_50ft = adjust_for_wind(to_50ft, wind_kts)
    to_50ft = adjust_for_runway_condition(to_50ft, runway_condition) * 1.10
    return ground_roll, to_50ft

# ... (keep all your other @st.cache_data functions: compute_landing, compute_climb_rate, etc.)

# ────────────────────────────────────────────────
# Risk Assessment
# ────────────────────────────────────────────────
def show_risk_assessment():
    st.subheader("Risk Assessment")
    st.caption("Score each factor 0–10 (higher = more risk).")
    total_risk = 0
    # ... (rest of the function remains unchanged)

# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
st.title("AgPilot")
st.markdown("Performance calculator for agricultural aircraft & helicopters")
st.caption("Prototype – educational use only. Always refer to the official Pilot Operating Handbook (POH) for actual operations.")

# Fleet, aircraft selection, custom empty weight, etc. (keep your original logic)

# ... (your existing code for inputs, weather, TFR map, performance calculation)

if st.button("Calculate Performance", type="primary"):
    # ... (your calculation and display logic)

    # Climb chart
    st.subheader("Rate of Climb vs Pressure Altitude")
    altitudes = np.linspace(0, 12000, 60)
    climb_rates = [compute_climb_rate(alt, oat_c, weight_lbs, selected_aircraft) for alt in altitudes]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(altitudes, climb_rates, color='darkgreen', linewidth=2.2)
    ax.set_xlabel("Pressure Altitude (ft)")
    ax.set_ylabel("Rate of Climb (fpm)")
    ax.set_title(f"Climb Performance – {aircraft_data['name']} – OAT {oat_c}°C, Weight {weight_lbs} lbs")
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # ────────────────────────────────────────────────
    # Emergency Response Button & Checklist
    # ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Emergency Response")

    if st.button("Activate Emergency Response", type="primary", use_container_width=True,
                 help="Tap only in real emergency – shows immediate action checklist"):

        st.markdown("**Priority: Aviate → Navigate → Communicate**")

        with st.expander("**Immediate Actions Checklist**", expanded=True):
            st.markdown("""
                1. **Declare an emergency / Call 911 / Render first aid**
                   - Make sure fuel shut-off is off and battery switch turned off.
                   - Evacuate upwind if fire/chemical risk
                   - Always look for possible contamination from spray mixture or fuel and advise medical responders along with providing SDS’s
                   - Spill Response Action (See Spill Response Procedure)
                   - Preservation of: Wreckage, documents
                2. **Observe and note witnesses**
                   - Secure the scene with spill response coordination
                   - Do not speak to the media or make statements to government officials
                   - State: "Company has contacted the appropriate authorities for a full investigation to ensure understanding of events and to prevent further harm."
                   - Do not, under any circumstances, speculate as to the cause of an accident / incident or other emergency
                3. **All press and/or media inquiries should be referred to [Name] or [Name].**
                   - Company Management notify FAA and NTSB
                   - Direct all calls to other managers
                   - Contact local Law Enforcement
                   - Make arrangements to preserve any wreckage
                4. **Prepare statement for release to the press.**
                   - Activate ELT if equipped
                   - Treat injuries (first aid kit), stay with aircraft if safe
                   - Call 911 or local (Kittitas County Sheriff: 509-962-1234; KVFR: 509-925-5555)
            """.strip())

        st.markdown("**Local Emergency Contacts**")
        st.markdown("""
        - **Emergency**: **911**
        - **Poison Control** (chemical exposure): **1-800-222-1222**
        - **Nearest Trauma Center**: Central Washington Hospital (Wenatchee) or Yakima Valley Memorial
        """)

        st.markdown("[Call 911 (Emergency)](tel:911)", unsafe_allow_html=True)
        st.info("This is a quick-reference checklist only. Follow your company Emergency Response Plan and official guidance at all times.")

    st.markdown("---")

# Feedback section
st.subheader("Your Feedback – Help Improve AgPilot")
rating = st.feedback("stars")
comment = st.text_area(
    "Any suggestions send screenshot to cvh@centralvalleyheli.com",
    height=120,
    placeholder="To keep AgPilot free send comments to email above"
)

if st.button("Safe flying & have a Blessed day ⌯✈︎"):
    if rating is not None:
        stars = rating + 1
        st.success(f"Thank you! You rated **{stars} stars**.")
        if comment.strip():
            st.caption(f"Comment: {comment}")
    else:
        st.warning("Please select a star rating.")
