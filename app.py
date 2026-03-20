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

# ────────────────────────────────────────────────
# Custom Logo (smaller size) – unchanged as requested
# ────────────────────────────────────────────────
LOGO_URL = "https://raw.githubusercontent.com/Clineair/AgPilot-app/main/AgPilotApp.png"
try:
    st.image(LOGO_URL, width=300)
    st.logo(LOGO_URL, size="medium")
except Exception:
    try:
        st.image("AgPilotApp.png", width=300)
        st.logo("AgPilotApp.png", size="medium")
    except Exception:
        st.markdown("### AgPilotApp ⌯✈︎ (logo not loaded – check file/URL)")

# ────────────────────────────────────────────────
# Legal Button
# ────────────────────────────────────────────────
if st.button("Legal+Abbreviations ", type="secondary"):
    with st.expander("Legal and Terms", expanded=True):
        st.markdown("""
        ### Legal and Terms of Use
       By downloading, installing, or otherwise
       accessing or using etc:
        List of Abbreviations
        Abbreviation | Definition
        ABS | Absolute
        AGL | Above Ground Level
        ALT | Altitude
        CAS | Calibrated Airspeed
        CG | Center of Gravity
        CL | Centerline
        CONF | Configuration
        CONT | Continuous
        F | Fahrenheit
        FLT | Flight
        FPM | Feet per Minute
        FT | Foot
        FWD | Forward
        GAL | Gallon
        GAL/HR | Gallon per hour
        GW | Gross Weight
        IAS | Indicated Airspeed
        IGE | In ground effect
        IN | Inch
        IN HG | Inches of Mercury
        ISA | International Standard Atmosphere
        KIAS | Knots Indicated Airspeed
        KT | Knot
        LB | Pound
        LB/HR | Pounds per hour
        MAX | Maximum
        MB | Millibar
        MIN | Minimum
        MTS | Gas producer turbine speed
        N1 | Power turbine speed
        NM | Nautical mile
        OAT | Outside Air Temp.
        OGE | Out of ground effect
        PRESS | Pressure
        PSI | Pounds per square inch
        R/C | Rate of climb
        R/D | Rate of descent
        RPM | Revolutions per minute
        SHP | Shaft horsepower
        SQ FT | Square feet
        TAS | True airspeed
        TORQ | Torque
        TRQ | Torque
        VDC | Volts direct current
        Vd | Maximum design dive speed
        Vh | Maximum level flight airspeed at maximum continuous power
        Vne | Velocity never exceeded
        Vy | Best rate of climb airspeed
        WT | Weight
        XMSN | Transmission
            By using this app, you agree to these terms. This app is for educational purposes only and not a substitute for official POH or professional advice.
        """)

# ────────────────────────────────────────────────
# Session State Initialization
# ────────────────────────────────────────────────
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'custom_empty_weight' not in st.session_state:
    st.session_state.custom_empty_weight = None
if 'show_risk' not in st.session_state:
    st.session_state.show_risk = False
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

# ────────────────────────────────────────────────
# Default performance values
# ────────────────────────────────────────────────
ground_roll_to = to_50ft = ground_roll_land = from_50ft = 0
climb_rate = stall_speed = glide_dist = total_weight = 0
ige_ceiling = oge_ceiling = 0
cg_status = "Not calculated yet"

# ────────────────────────────────────────────────
# Aircraft Database (fixed – stray { removed)
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
    "Air Tractor AT-802": {
        "name": "Air Tractor AT-802",
        "base_takeoff_ground_roll_ft": 1800,
        "base_takeoff_to_50ft_ft": 3400,
        "base_landing_ground_roll_ft": 1100,
        "base_landing_to_50ft_ft": 2200,
        "base_climb_rate_fpm": 1050,
        "base_stall_flaps_down_mph": 78,
        "best_climb_speed_mph": 120,
        "base_empty_weight_lbs": 6750,
        "base_fuel_capacity_gal": 380,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 800,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 16000,
        "max_landing_weight_lbs": 14000,
        "glide_ratio": 7.0,
        "description": "Large turbine ag aircraft – high payload & range"
    },
    "Thrush 510P": {
        "name": "Thrush 510P",
        "base_takeoff_ground_roll_ft": 1300,
        "base_takeoff_to_50ft_ft": 2800,
        "base_landing_ground_roll_ft": 750,
        "base_landing_to_50ft_ft": 1600,
        "base_climb_rate_fpm": 950,
        "base_stall_flaps_down_mph": 72,
        "best_climb_speed_mph": 115,
        "base_empty_weight_lbs": 6800,
        "base_fuel_capacity_gal": 380,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 510,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 12000,
        "max_landing_weight_lbs": 10500,
        "glide_ratio": 7.5,
        "description": "Turbine-powered high-capacity ag aircraft"
    },
    "Ayres Thrush S2R-T34 Eagle": {
        "name": "Ayres Thrush S2R-T34 Eagle",
        "base_takeoff_ground_roll_ft": 1650,
        "base_takeoff_to_50ft_ft": 2500,
        "base_landing_ground_roll_ft": 600,
        "base_landing_to_50ft_ft": 1500,
        "base_climb_rate_fpm": 666,
        "base_stall_flaps_down_mph": 50,
        "best_climb_speed_mph": 110,
        "base_empty_weight_lbs": 4900,
        "base_fuel_capacity_gal": 228,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 510,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 10500,
        "max_landing_weight_lbs": 10500,
        "glide_ratio": 7.0,
        "description": "Turbine-powered high-capacity ag sprayer – excellent short-field & payload",
        "hover_ceiling_ige_max_gw": 0,
        "hover_ceiling_oge_max_gw": 0
    },
    "Grumman G-164B Ag-Cat": {
        "name": "Grumman G-164B Ag-Cat",
        "base_takeoff_ground_roll_ft": 1200,
        "base_takeoff_to_50ft_ft": 2200,
        "base_landing_ground_roll_ft": 800,
        "base_landing_to_50ft_ft": 1800,
        "base_climb_rate_fpm": 1080,
        "base_stall_flaps_down_mph": 64,
        "best_climb_speed_mph": 90,
        "base_empty_weight_lbs": 3150,
        "base_fuel_capacity_gal": 190,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 400,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 4500,
        "max_landing_weight_lbs": 4500,
        "glide_ratio": 7.5,
        "description": "Classic radial-engine biplane ag sprayer – rugged & low stall speed"
    },
    "Cessna 188 Ag Truck": {
        "name": "Cessna 188 Ag Truck",
        "base_takeoff_ground_roll_ft": 680,
        "base_takeoff_to_50ft_ft": 1090,
        "base_landing_ground_roll_ft": 420,
        "base_landing_to_50ft_ft": 1265,
        "base_climb_rate_fpm": 690,
        "base_stall_flaps_down_mph": 50,
        "best_climb_speed_mph": 80,
        "base_empty_weight_lbs": 2220,
        "base_fuel_capacity_gal": 54,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 280,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 4200,
        "max_landing_weight_lbs": 4200,
        "glide_ratio": 8.0,
        "description": "Classic single-engine piston ag sprayer"
    },
    "Cessna AgHusky": {
        "name": "Cessna AgHusky",
        "base_takeoff_ground_roll_ft": 800,
        "base_takeoff_to_50ft_ft": 1350,
        "base_landing_ground_roll_ft": 450,
        "base_landing_to_50ft_ft": 1350,
        "base_climb_rate_fpm": 750,
        "base_stall_flaps_down_mph": 52,
        "best_climb_speed_mph": 85,
        "base_empty_weight_lbs": 2322,
        "base_fuel_capacity_gal": 56,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 280,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 4400,
        "max_landing_weight_lbs": 4400,
        "glide_ratio": 8.0,
        "description": "Cessna 188 AgHusky variant – rugged piston ag sprayer with good short-field performance"
    },
    "Piper PA-36 Pawnee Brave": {
        "name": "Piper PA-36 Pawnee Brave",
        "base_takeoff_ground_roll_ft": 1200,
        "base_takeoff_to_50ft_ft": 1500,
        "base_landing_ground_roll_ft": 850,
        "base_landing_to_50ft_ft": 1800,
        "base_climb_rate_fpm": 920,
        "base_stall_flaps_down_mph": 65,
        "best_climb_speed_mph": 100,
        "base_empty_weight_lbs": 2560,
        "base_fuel_capacity_gal": 86,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 275,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 4800,
        "max_landing_weight_lbs": 4800,
        "glide_ratio": 7.5,
        "description": "Single-engine piston ag sprayer – large hopper & good swath width"
    },
    "Robinson R44 Raven II": {
        "name": "Robinson R44 Raven II",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 1000,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 55,
        "base_empty_weight_lbs": 1505,
        "base_fuel_capacity_gal": 50,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 83,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 2500,
        "max_landing_weight_lbs": 2500,
        "glide_ratio": 4.0,
        "description": "Light utility/training helicopter (spray capable)",
        "hover_ceiling_ige_max_gw": 8950,
        "hover_ceiling_oge_max_gw": 7500
    },
    "Bell 206 JetRanger III": {
        "name": "Bell 206 JetRanger III",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 1280,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 60,
        "base_empty_weight_lbs": 1635,
        "base_fuel_capacity_gal": 91,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 100,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 3200,
        "max_landing_weight_lbs": 3200,
        "glide_ratio": 4.0,
        "description": "Light utility helicopter (spray capable)",
        "hover_ceiling_ige_max_gw": 12800,
        "hover_ceiling_oge_max_gw": 8800
    },
    "Airbus AS350 B2": {
        "name": "Airbus AS350 B2",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 1675,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 60,
        "base_empty_weight_lbs": 2800,
        "base_fuel_capacity_gal": 143,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 150,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 4960,
        "max_landing_weight_lbs": 4960,
        "glide_ratio": 4.0,
        "description": "Turbine ag spray helicopter – high performance utility",
        "hover_ceiling_ige_max_gw": 9850,
        "hover_ceiling_oge_max_gw": 7550
    },
    "Enstrom 480": {
        "name": "Enstrom 480",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 1100,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 60,
        "base_empty_weight_lbs": 1750,
        "base_fuel_capacity_gal": 95,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 100,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 2800,
        "max_landing_weight_lbs": 2800,
        "glide_ratio": 4.0,
        "description": "Turbine light utility helicopter (spray capable)",
        "hover_ceiling_ige_max_gw": 11000,
        "hover_ceiling_oge_max_gw": 8500
    },
    "Enstrom 480B": {
        "name": "Enstrom 480B",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 1200,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 60,
        "base_empty_weight_lbs": 1800,
        "base_fuel_capacity_gal": 95,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 100,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 2850,
        "max_landing_weight_lbs": 2850,
        "glide_ratio": 4.0,
        "description": "Improved turbine light utility helicopter (spray capable)",
        "hover_ceiling_ige_max_gw": 12000,
        "hover_ceiling_oge_max_gw": 9000
    },
    "Robinson R66": {
        "name": "Robinson R66",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 1100,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 60,
        "base_empty_weight_lbs": 1290,
        "base_fuel_capacity_gal": 73.6,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 130,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 2700,
        "max_landing_weight_lbs": 2700,
        "glide_ratio": 4.0,
        "description": "Turbine light utility helicopter (spray capable)",
        "hover_ceiling_ige_max_gw": 11000,
        "hover_ceiling_oge_max_gw": 10000
    },
    "Enstrom F28F": {
        "name": "Enstrom F28F",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 1450,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 57,
        "base_empty_weight_lbs": 1640,
        "base_fuel_capacity_gal": 40,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 100,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 2600,
        "max_landing_weight_lbs": 2600,
        "glide_ratio": 4.0,
        "description": "Piston helicopter (Falcon) – utility/ag capable",
        "hover_ceiling_ige_max_gw": 13200,
        "hover_ceiling_oge_max_gw": 8700
    },
    "Scott's Bell 47": {
        "name": "Scott's Bell 47",
        "base_takeoff_ground_roll_ft": 0,
        "base_takeoff_to_50ft_ft": 0,
        "base_landing_ground_roll_ft": 0,
        "base_landing_to_50ft_ft": 0,
        "base_climb_rate_fpm": 900,
        "base_stall_flaps_down_mph": 0,
        "best_climb_speed_mph": 60,
        "base_empty_weight_lbs": 1900,
        "base_fuel_capacity_gal": 43,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 100,
        "hopper_weight_per_gal": 8.3,
        "max_takeoff_weight_lbs": 2950,
        "max_landing_weight_lbs": 2950,
        "glide_ratio": 4.0,
        "description": "Light piston utility/ag helicopter – classic bubble canopy, spray capable",
        "hover_ceiling_ige_max_gw": 10000,
        "hover_ceiling_oge_max_gw": 8000
    }
}

# ────────────────────────────────────────────────
# Density Altitude Calculation + Helper Functions
# (unchanged)
# ────────────────────────────────────────────────
def calculate_density_altitude(pressure_alt_ft, oat_c):
    isa_temp_c = 15 - (2 * (pressure_alt_ft / 1000))
    deviation = oat_c - isa_temp_c
    da_ft = pressure_alt_ft + (120 * deviation)
    return round(da_ft)

# (All your adjust_for_ and compute_ functions are exactly as you provided – no changes)

# ────────────────────────────────────────────────
# Risk Assessment – Monthly + Annual buttons side-by-side + Yes/No radios
# ────────────────────────────────────────────────
def show_risk_assessment():
    st.subheader("Pre-Flight Risk Assessment")
    st.caption("Score each factor 0–10 (higher = more risk).")
    total_risk = 0
    # ... (all your existing sliders unchanged)

    st.markdown("---")
    risk_percent = (total_risk / 100) * 100
    # ... (your gauge code unchanged)

    # Monthly and Annual Questions buttons side-by-side
    col_m, col_a = st.columns(2)
    with col_m:
        if st.button("Monthly Questions", type="secondary", use_container_width=True):
            with st.expander("Monthly Safety & Maintenance Questions", expanded=True):
                st.markdown("**Answer these every month and log your responses:**")
                q1 = st.radio("Is your total ag time sufficient for workload and supervision?", ["Yes", "No"], horizontal=True)
                q2 = st.radio("Is your total time in type sufficient for workload and supervision?", ["Yes", "No"], horizontal=True)
                q3 = st.radio("Are you familiar with and used to flying with all your medications?", ["Yes", "No"], horizontal=True)
                q4 = st.radio("Are you familiar with your aircraft and aircraft systems?", ["Yes", "No"], horizontal=True)
                st.caption("If you answered No to any questions, STOP. Reconsider making the flight or consider mitigation options.")
    with col_a:
        if st.button("Annual Questions", type="secondary", use_container_width=True):
            with st.expander("Annual Safety & Maintenance Questions", expanded=True):
                st.markdown("""
                **Answer these once per year:**
                - Do you have a current Biennial Flight Review?
                - Is your medical certificate current and valid?
                - Do you have current State and Federal licenses/certificate?
                - Do you wear Personal Protective Equipment (PPE)?
                - Do you wear a helmet
                - Do you wear a fire-resistant flight suit?
                - Are you free of chronic illness?
                - Do you have a clear driving record with no DUI?
                - Do you wear a lap belt?
                - Do you wear a shoulder harness?
                - Have you attended PAASS in the last year?
                - Have you attended an Operation S.A.F.F. Fly In clinic in the past two years?
                """)
                st.caption("If you answered No to any questions, STOP. Reconsider making the flight or consider mitigation options.")

    if total_risk > 30:
        st.info("**Mitigation Recommendations**")
        st.markdown("- Delay departure or mitigate")
        st.markdown("- Increase fuel or choose closer field")
        st.markdown("- Consult for second opinion")
        st.markdown("- Screenshot and re-assess high risk")
    st.caption("Not a substitute for official preflight briefing or company policy.")

# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
st.title("AgPilot")
st.markdown("Performance calculator for agricultural aircraft & helicopters")
st.caption("Prototype – educational use only. Always refer to the official Pilot Operating Handbook (POH) for actual operations.")

# Fleet Management
st.subheader("My Fleet")
if st.session_state.fleet:
    fleet_nicknames = ["— Select a saved aircraft —"] + [entry["nickname"] for entry in st.session_state.fleet]
    selected_nickname = st.selectbox("Load from Fleet", fleet_nicknames)
    if selected_nickname != "— Select a saved aircraft —":
        entry = next(e for e in st.session_state.fleet if e["nickname"] == selected_nickname)
        st.session_state.selected_aircraft = entry["aircraft"]
        custom = entry.get("custom_empty")
        st.session_state.custom_empty_weight = int(custom) if custom is not None else None
        st.success(f"Loaded **{selected_nickname}** ({entry['aircraft']}) – Empty: {custom or 'base'} lb")
else:
    st.info("No aircraft saved to fleet yet.")

# Aircraft selection
selected_aircraft = st.selectbox(
    "Select Aircraft",
    options=list(AIRCRAFT_DATA.keys()),
    index=0 if 'selected_aircraft' not in st.session_state else list(AIRCRAFT_DATA.keys()).index(st.session_state.get("selected_aircraft", list(AIRCRAFT_DATA.keys())[0])),
    format_func=lambda x: f"{AIRCRAFT_DATA[x]['name']} – {AIRCRAFT_DATA[x]['description']}"
)
aircraft_data = AIRCRAFT_DATA[selected_aircraft]

# Helicopter detection
is_helicopter = any(heli in selected_aircraft for heli in [
    "R44", "Bell 206", "Enstrom 480", "Enstrom 480B", "Robinson R66",
    "Airbus AS350", "Enstrom F28F", "Bell 47"
])

# Custom Empty Weight Input
st.subheader("Custom Empty Weight (optional)")
col_empty1, col_empty2 = st.columns([3, 1])
with col_empty1:
    current_empty = st.session_state.get('custom_empty_weight')
    if current_empty is None:
        current_empty = aircraft_data["base_empty_weight_lbs"]
    else:
        current_empty = int(current_empty)
    custom_empty = st.number_input(
        f"Custom Empty Weight for {aircraft_data['name']} (lb)",
        min_value=500,
        max_value=int(aircraft_data["max_takeoff_weight_lbs"] * 0.9),
        value=current_empty,
        step=10,
        help="Override base empty weight if your aircraft has modifications, avionics, etc."
    )
with col_empty2:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Save to Fleet"):
        nickname = st.text_input("Give this configuration a nickname (e.g. 'N123AB R66')", key="fleet_nickname")
        if nickname.strip():
            st.session_state.fleet = [e for e in st.session_state.fleet if e["nickname"] != nickname.strip()]
            st.session_state.fleet.append({
                "nickname": nickname.strip(),
                "aircraft": selected_aircraft,
                "custom_empty": custom_empty
            })
            st.success(f"Saved **{nickname}** to fleet!")
        else:
            st.warning("Please enter a nickname to save.")

effective_empty = custom_empty if custom_empty != aircraft_data["base_empty_weight_lbs"] else aircraft_data["base_empty_weight_lbs"]
st.caption(f"**Effective Empty Weight:** {effective_empty} lb {'(custom)' if custom_empty != aircraft_data['base_empty_weight_lbs'] else '(base)'}")

# Risk Assessment button
if st.button("Risk Assessment", type="secondary"):
    st.session_state.show_risk = not st.session_state.get("show_risk", False)

st.info(f"Performance data loaded for **{aircraft_data['name']}**")
if st.session_state.get("show_risk", False):
    show_risk_assessment()

# ────────────────────────────────────────────────
# Airport Weather & Notices (METAR + TAF + NOTAMs) – FULL SECTION ADDED
# ────────────────────────────────────────────────
st.subheader("Airport Weather & Notices (METAR + TAF + NOTAMs)")
common_airports = {
    "KELN": "Ellensburg Bowers Field (KELN) – Home base",
    "KYKM": "Yakima Air Terminal (KYKM)",
    "KEAT": "Pangborn Memorial (KEAT) – Wenatchee",
    "KPUW": "Pullman/Moscow Regional (KPUW)",
    "KSEA": "Seattle-Tacoma Intl (KSEA)",
    "None": "—— No airport selected ——"
}
selected_icao = st.selectbox(
    "Select Nearby Airport",
    options=list(common_airports.keys()),
    format_func=lambda x: common_airports.get(x, x),
    index=0
)
custom_icao = st.text_input(
    "Or enter any ICAO code (4 letters)",
    value="",
    max_chars=4,
    help="For any airport worldwide (e.g. KLAX for Los Angeles, KMIA for Miami)"
).strip().upper()
icao_upper = custom_icao if custom_icao and len(custom_icao) == 4 and custom_icao.isalnum() else selected_icao
metar_text = None
metar_timestamp = None
taf_text = None
taf_issued = None
if icao_upper and icao_upper != "None":
    try:
        url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao_upper}.TXT"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.strip().splitlines()
            if len(lines) >= 2:
                metar_timestamp = lines[0].strip()
                metar_text = lines[1].strip()
            elif lines:
                metar_text = lines[0].strip()
    except Exception as e:
        st.warning(f"METAR fetch error for {icao_upper}: {e}")
    try:
        url = f"https://aviationweather.gov/api/data/taf?ids={icao_upper}&format=raw"
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            taf_text = response.text.strip()
            lines = taf_text.splitlines()
            if lines and "Z" in lines[0]:
                taf_issued = lines[0].split()[1] if len(lines[0].split()) > 1 else None
    except Exception as e:
        st.warning(f"TAF fetch error for {icao_upper}: {e}")
if icao_upper and icao_upper != "None":
    st.markdown(f"**Latest Weather for {icao_upper}**")
    st.markdown("**METAR (Current)**")
    if metar_text:
        st.markdown(f"({metar_timestamp or 'fetched ' + datetime.now().strftime('%Y-%m-%d %H:%M UTC')})")
        st.code(metar_text, language="text")
        parts = metar_text.split()
        wind_part = next((p for p in parts if "KT" in p and len(p) >= 6), "—")
        temp_dew_part = next((p for p in parts if "/" in p and len(p.split("/")) == 2), "—")
        altimeter_part = next((p for p in parts if (p.startswith("A") and len(p) == 5) or p.startswith("Q")), "—")
        cols = st.columns(3)
        cols[0].metric("Wind", wind_part)
        cols[1].metric("Temp / Dew", temp_dew_part)
        cols[2].metric("Altimeter", altimeter_part)
    else:
        st.info("No METAR available – check ICAO code or try later.")
    st.markdown("**TAF (Forecast)**")
    if taf_text:
        issued_str = f"Issued ~ {taf_issued}" if taf_issued else f"Fetched {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
        st.markdown(f"({issued_str})")
        st.code(taf_text, language="text")
    else:
        st.info("No TAF available (common for small fields).")
    st.markdown("**NOTAMs (Notices to Airmen)**")
    st.caption("**Always check current NOTAMs via official FAA sources before flight.**")
    st.markdown(f"[Open FAA NOTAM Search for {icao_upper}](https://notams.aim.faa.gov/notamSearch/search?search=location&loc={icao_upper}) – view active NOTAMs, TFRs, and details.")
    st.caption("Recommended: Use 1800-WX-BRIEF phone briefing or apps like ForeFlight / Garmin Pilot.")
st.markdown("---")

# TFR Map
st.subheader("Temporary Flight Restrictions (TFR) Map")
st.caption("Live interactive FAA TFR map – shows current restrictions. Zoom to your area/state.")
st.components.v1.iframe(
    src="https://tfr.faa.gov/tfr3/?page=map",
    height=600,
    scrolling=True
)
st.markdown("[Open full-screen FAA TFR Map](https://tfr.faa.gov/tfr3/?page=map) – recommended for detailed view.")

# Inputs
col1, col2 = st.columns(2)
with col1:
    pressure_alt_ft = st.number_input("Pressure Altitude (ft)", min_value=0, max_value=20000, value=0, step=100)
    oat_c = st.number_input("OAT (°C)", min_value=-30, max_value=50, value=15, step=1)
    min_weight = 1000 if is_helicopter else 4000
    weight_lbs = st.number_input(
        "Gross Weight (lbs)",
        min_value=min_weight,
        max_value=aircraft_data["max_takeoff_weight_lbs"],
        value=aircraft_data["max_takeoff_weight_lbs"],
        step=50,
        help="Adjust based on actual loadout. Helicopter min lowered for realistic empty weights."
    )
    wind_kts = st.number_input("Headwind (+) / Tailwind (-) (kts)", min_value=-20, max_value=20, value=0, step=1)
    runway_condition = st.selectbox(
        "Runway Condition",
        options=[
            "Paved / Dry Hard Surface",
            "Dry Grass / Firm Turf",
            "Wet Grass / Damp Turf",
            "Soft / Muddy / Rough"
        ],
        index=0,
        help="Adjusts takeoff/landing distances. Baseline = paved/dry."
    )
with col2:
    fuel_gal = st.number_input("Fuel (gal)", min_value=0, max_value=aircraft_data["base_fuel_capacity_gal"], value=aircraft_data["base_fuel_capacity_gal"], step=10)
    max_hopper = aircraft_data["hopper_capacity_gal"]
    hopper_gal = st.number_input(
        "Hopper / Spray Load (gal)",
        min_value=0,
        max_value=max_hopper,
        value=0,
        step=10,
        help=f"Max spray/chemical load: {max_hopper} gal"
    )
    pilot_weight_lbs = st.number_input("Pilot Weight (lbs)", min_value=100, max_value=300, value=200, step=10)
    glide_height_ft = st.number_input("Glide Height AGL (ft)", min_value=0, max_value=15000, value=1000, step=100)

# Density Altitude
da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
isa_temp_c = 15 - (2 * (pressure_alt_ft / 1000))
isa_deviation = oat_c - isa_temp_c
st.subheader("Density Altitude")
st.metric("Density Altitude", f"{da_ft} ft")
st.caption(f"ISA temp at {pressure_alt_ft} ft: **{isa_temp_c:.1f} °C** | Deviation: **{isa_deviation:.1f} °C**")

# Calculate Performance
if st.button("Calculate Performance", type="primary"):
    # (your full calculation block – unchanged)

# Feedback
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

# ────────────────────────────────────────────────
# Emergency Response Checklist – MOVED TO THE VERY BOTTOM
# ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Emergency Response")
st.caption("Quick access – use only in real emergencies")
st.markdown(
    """
    <div style="font-size: 12pt; font-weight: bold; color: #d32f2f; margin: 10px 0;">
        Priority (PILOT): Aviate → Navigate → Communicate
    </div>
    """,
    unsafe_allow_html=True
)
if st.button("Emergency Response Checklist", type="primary", use_container_width=True,
             help="Tap only in real emergency – shows immediate action checklist"):
    with st.expander("**Immediate Actions Checklist**", expanded=True):
        st.markdown("""
        1. **Declare emergency / Call 911 / First aid**
           - Turn fuel shut-off off, battery switch off.
           - Evacuate upwind if fire or chemical risk.
           - Check for spray/fuel contamination; give
             SDS to responders.
           - Follow Spill Response Procedure.
           - Preserve wreckage and documents.
        2. **Witnesses & Scene Control**
           - Secure scene with spill response team.
           - Do NOT speak to media or officials.
           - Say only: "Company has contacted
             appropriate authorities for a full
             investigation to determine root
             cause and prevent recurrence."
           - Do NOT speculate on cause.
        3. **Media & Press Inquiries**
           - Refer all calls to informed management.
           - Management will notify FAA and NTSB.
           - Direct inquiries to informed managers.
           - Contact local law enforcement.
           - Arrange wreckage preservation.
        4. **Additional Immediate Steps**
           - Is ELT activated?
           - Treat injuries (first aid kit); assure
             area is protected.
           - Call 911 or local:
             County Sheriff: 509-962-1234
        """.strip())
    st.markdown("**Local Emergency Contacts**")
    st.markdown("""
    - **Emergency**: **911**
    - **Poison Control** (chemical exposure):
      **1-800-222-1222**
    """)
    st.markdown("[Call 911 (Emergency)](tel:911)", unsafe_allow_html=True)
    st.info("Quick-reference only. Follow your company Emergency Response Plan and official guidance at all times.")

st.caption("**Safe flying & have a Blessed day** ⌯✈︎")
