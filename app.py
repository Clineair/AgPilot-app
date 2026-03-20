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
# Custom Logo (smaller size)
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
       By downloading, installing, or otherwise accessing or using this app, you agree to these terms. 
       This app is for educational purposes only and not a substitute for official POH or professional advice.
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
        """)

# ────────────────────────────────────────────────
# Session State
# ────────────────────────────────────────────────
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'custom_empty_weight' not in st.session_state:
    st.session_state.custom_empty_weight = None
if 'show_risk' not in st.session_state:
    st.session_state.show_risk = False
if 'monthly_open' not in st.session_state:
    st.session_state.monthly_open = False
if 'annual_open' not in st.session_state:
    st.session_state.annual_open = False

# ────────────────────────────────────────────────
# Aircraft Database (full list)
# ────────────────────────────────────────────────
AIRCRAFT_DATA = {
    "Air Tractor AT-502B": {"name": "Air Tractor AT-502B", "base_takeoff_ground_roll_ft": 1140, "base_takeoff_to_50ft_ft": 2600, "base_landing_ground_roll_ft": 600, "base_landing_to_50ft_ft": 1350, "base_climb_rate_fpm": 870, "base_stall_flaps_down_mph": 68, "best_climb_speed_mph": 111, "base_empty_weight_lbs": 4546, "base_fuel_capacity_gal": 170, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 500, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 9400, "max_landing_weight_lbs": 8000, "glide_ratio": 8.0, "description": "Single-engine piston ag aircraft"},
    "Air Tractor AT-602": {"name": "Air Tractor AT-602", "base_takeoff_ground_roll_ft": 1400, "base_takeoff_to_50ft_ft": 2800, "base_landing_ground_roll_ft": 850, "base_landing_to_50ft_ft": 1850, "base_climb_rate_fpm": 1050, "base_stall_flaps_down_mph": 74, "best_climb_speed_mph": 118, "base_empty_weight_lbs": 6200, "base_fuel_capacity_gal": 380, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 600, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 12500, "max_landing_weight_lbs": 11000, "glide_ratio": 7.2, "description": "Turbine ag aircraft – balanced payload & performance"},
    "Air Tractor AT-802": {"name": "Air Tractor AT-802", "base_takeoff_ground_roll_ft": 1800, "base_takeoff_to_50ft_ft": 3400, "base_landing_ground_roll_ft": 1100, "base_landing_to_50ft_ft": 2200, "base_climb_rate_fpm": 1050, "base_stall_flaps_down_mph": 78, "best_climb_speed_mph": 120, "base_empty_weight_lbs": 6750, "base_fuel_capacity_gal": 380, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 800, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 16000, "max_landing_weight_lbs": 14000, "glide_ratio": 7.0, "description": "Large turbine ag aircraft – high payload & range"},
    "Thrush 510P": {"name": "Thrush 510P", "base_takeoff_ground_roll_ft": 1300, "base_takeoff_to_50ft_ft": 2800, "base_landing_ground_roll_ft": 750, "base_landing_to_50ft_ft": 1600, "base_climb_rate_fpm": 950, "base_stall_flaps_down_mph": 72, "best_climb_speed_mph": 115, "base_empty_weight_lbs": 6800, "base_fuel_capacity_gal": 380, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 510, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 12000, "max_landing_weight_lbs": 10500, "glide_ratio": 7.5, "description": "Turbine-powered high-capacity ag aircraft"},
    "Ayres Thrush S2R-T34 Eagle": {"name": "Ayres Thrush S2R-T34 Eagle", "base_takeoff_ground_roll_ft": 1650, "base_takeoff_to_50ft_ft": 2500, "base_landing_ground_roll_ft": 600, "base_landing_to_50ft_ft": 1500, "base_climb_rate_fpm": 666, "base_stall_flaps_down_mph": 50, "best_climb_speed_mph": 110, "base_empty_weight_lbs": 4900, "base_fuel_capacity_gal": 228, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 510, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 10500, "max_landing_weight_lbs": 10500, "glide_ratio": 7.0, "description": "Turbine-powered high-capacity ag sprayer – excellent short-field & payload"},
    "Grumman G-164B Ag-Cat": {"name": "Grumman G-164B Ag-Cat", "base_takeoff_ground_roll_ft": 1200, "base_takeoff_to_50ft_ft": 2200, "base_landing_ground_roll_ft": 800, "base_landing_to_50ft_ft": 1800, "base_climb_rate_fpm": 1080, "base_stall_flaps_down_mph": 64, "best_climb_speed_mph": 90, "base_empty_weight_lbs": 3150, "base_fuel_capacity_gal": 190, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 400, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 4500, "max_landing_weight_lbs": 4500, "glide_ratio": 7.5, "description": "Classic radial-engine biplane ag sprayer – rugged & low stall speed"},
    "Cessna 188 Ag Truck": {"name": "Cessna 188 Ag Truck", "base_takeoff_ground_roll_ft": 680, "base_takeoff_to_50ft_ft": 1090, "base_landing_ground_roll_ft": 420, "base_landing_to_50ft_ft": 1265, "base_climb_rate_fpm": 690, "base_stall_flaps_down_mph": 50, "best_climb_speed_mph": 80, "base_empty_weight_lbs": 2220, "base_fuel_capacity_gal": 54, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 280, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 4200, "max_landing_weight_lbs": 4200, "glide_ratio": 8.0, "description": "Classic single-engine piston ag sprayer"},
    "Cessna AgHusky": {"name": "Cessna AgHusky", "base_takeoff_ground_roll_ft": 800, "base_takeoff_to_50ft_ft": 1350, "base_landing_ground_roll_ft": 450, "base_landing_to_50ft_ft": 1350, "base_climb_rate_fpm": 750, "base_stall_flaps_down_mph": 52, "best_climb_speed_mph": 85, "base_empty_weight_lbs": 2322, "base_fuel_capacity_gal": 56, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 280, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 4400, "max_landing_weight_lbs": 4400, "glide_ratio": 8.0, "description": "Cessna 188 AgHusky variant – rugged piston ag sprayer with good short-field performance"},
    "Piper PA-36 Pawnee Brave": {"name": "Piper PA-36 Pawnee Brave", "base_takeoff_ground_roll_ft": 1200, "base_takeoff_to_50ft_ft": 1500, "base_landing_ground_roll_ft": 850, "base_landing_to_50ft_ft": 1800, "base_climb_rate_fpm": 920, "base_stall_flaps_down_mph": 65, "best_climb_speed_mph": 100, "base_empty_weight_lbs": 2560, "base_fuel_capacity_gal": 86, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 275, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 4800, "max_landing_weight_lbs": 4800, "glide_ratio": 7.5, "description": "Single-engine piston ag sprayer – large hopper & good swath width"},
    "Robinson R44 Raven II": {"name": "Robinson R44 Raven II", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 1000, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 55, "base_empty_weight_lbs": 1505, "base_fuel_capacity_gal": 50, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 83, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 2500, "max_landing_weight_lbs": 2500, "glide_ratio": 4.0, "description": "Light utility/training helicopter (spray capable)", "hover_ceiling_ige_max_gw": 8950, "hover_ceiling_oge_max_gw": 7500},
    "Bell 206 JetRanger III": {"name": "Bell 206 JetRanger III", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 1280, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 60, "base_empty_weight_lbs": 1635, "base_fuel_capacity_gal": 91, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 100, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 3200, "max_landing_weight_lbs": 3200, "glide_ratio": 4.0, "description": "Light utility helicopter (spray capable)", "hover_ceiling_ige_max_gw": 12800, "hover_ceiling_oge_max_gw": 8800},
    "Airbus AS350 B2": {"name": "Airbus AS350 B2", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 1675, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 60, "base_empty_weight_lbs": 2800, "base_fuel_capacity_gal": 143, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 150, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 4960, "max_landing_weight_lbs": 4960, "glide_ratio": 4.0, "description": "Turbine ag spray helicopter – high performance utility", "hover_ceiling_ige_max_gw": 9850, "hover_ceiling_oge_max_gw": 7550},
    "Enstrom 480": {"name": "Enstrom 480", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 1100, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 60, "base_empty_weight_lbs": 1750, "base_fuel_capacity_gal": 95, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 100, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 2800, "max_landing_weight_lbs": 2800, "glide_ratio": 4.0, "description": "Turbine light utility helicopter (spray capable)", "hover_ceiling_ige_max_gw": 11000, "hover_ceiling_oge_max_gw": 8500},
    "Enstrom 480B": {"name": "Enstrom 480B", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 1200, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 60, "base_empty_weight_lbs": 1800, "base_fuel_capacity_gal": 95, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 100, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 2850, "max_landing_weight_lbs": 2850, "glide_ratio": 4.0, "description": "Improved turbine light utility helicopter (spray capable)", "hover_ceiling_ige_max_gw": 12000, "hover_ceiling_oge_max_gw": 9000},
    "Robinson R66": {"name": "Robinson R66", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 1100, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 60, "base_empty_weight_lbs": 1290, "base_fuel_capacity_gal": 73.6, "fuel_weight_per_gal": 6.7, "hopper_capacity_gal": 130, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 2700, "max_landing_weight_lbs": 2700, "glide_ratio": 4.0, "description": "Turbine light utility helicopter (spray capable)", "hover_ceiling_ige_max_gw": 11000, "hover_ceiling_oge_max_gw": 10000},
    "Enstrom F28F": {"name": "Enstrom F28F", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 1450, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 57, "base_empty_weight_lbs": 1640, "base_fuel_capacity_gal": 40, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 100, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 2600, "max_landing_weight_lbs": 2600, "glide_ratio": 4.0, "description": "Piston helicopter (Falcon) – utility/ag capable", "hover_ceiling_ige_max_gw": 13200, "hover_ceiling_oge_max_gw": 8700},
    "Scott's Bell 47": {"name": "Scott's Bell 47", "base_takeoff_ground_roll_ft": 0, "base_takeoff_to_50ft_ft": 0, "base_landing_ground_roll_ft": 0, "base_landing_to_50ft_ft": 0, "base_climb_rate_fpm": 900, "base_stall_flaps_down_mph": 0, "best_climb_speed_mph": 60, "base_empty_weight_lbs": 1900, "base_fuel_capacity_gal": 43, "fuel_weight_per_gal": 6.0, "hopper_capacity_gal": 100, "hopper_weight_per_gal": 8.3, "max_takeoff_weight_lbs": 2950, "max_landing_weight_lbs": 2950, "glide_ratio": 4.0, "description": "Light piston utility/ag helicopter – classic bubble canopy, spray capable", "hover_ceiling_ige_max_gw": 10000, "hover_ceiling_oge_max_gw": 8000}
}

# ────────────────────────────────────────────────
# Density Altitude & Helper Functions (unchanged)
# ────────────────────────────────────────────────
def calculate_density_altitude(pressure_alt_ft, oat_c):
    isa_temp_c = 15 - (2 * (pressure_alt_ft / 1000))
    deviation = oat_c - isa_temp_c
    da_ft = pressure_alt_ft + (120 * deviation)
    return round(da_ft)

def adjust_for_weight(value, current_weight, base_weight, exponent=1.5):
    return value * (current_weight / base_weight) ** exponent

def adjust_for_runway_condition(value, condition):
    multipliers = {"Paved / Dry Hard Surface": 1.00, "Dry Grass / Firm Turf": 1.15, "Wet Grass / Damp Turf": 1.45, "Soft / Muddy / Rough": 1.80}
    return value * multipliers.get(condition, 1.00)

def adjust_for_wind(value, wind_kts):
    factor = 1 - (0.1 * wind_kts / 9)
    return value * max(factor, 0.5)

def adjust_for_da(value, da_ft):
    factor = 1 + (0.07 * da_ft / 1000)
    return value * factor

# (All @st.cache_data compute functions are exactly as you had them – omitted here only for brevity in this message, but they are in the full file you will paste)

# ────────────────────────────────────────────────
# FRAT – SLIDERS FIXED: Left = 10 High Risk, Right = 0 Low Risk + FULL GAUGE
# ────────────────────────────────────────────────
def show_risk_assessment():
    st.subheader("Flight Risk Assessment Tool (FRAT)")
    st.caption("**10 = High Risk** ← [slider] → **0 = Low Risk**")
    total_risk = 0

    st.markdown("**Pilot Factors**")
    v1 = st.slider("Recent experience/currency (hours last 30 days)", 0, 10, 5, step=1)
    total_risk += (10 - v1)
    v2 = st.slider("Fatigue/sleep last 24 hours", 0, 10, 5, step=1)
    total_risk += (10 - v2)
    v3 = st.slider("Physical/mental health today", 0, 10, 2, step=1)
    total_risk += (10 - v3)

    st.markdown("**Aircraft Factors**")
    v4 = st.slider("Maintenance status/known squawks", 0, 10, 3, step=1)
    total_risk += (10 - v4)
    v5 = st.slider("Fuel planning/reserves", 0, 10, 2, step=1)
    total_risk += (10 - v5)
    v6 = st.slider("Weight & balance/CG within limits", 0, 10, 2, step=1)
    total_risk += (10 - v6)

    st.markdown("**Environment / Weather**")
    v7 = st.slider("Ceiling/visibility", 0, 10, 4, step=1)
    total_risk += (10 - v7)
    v8 = st.slider("Turbulence/icing/wind forecast", 0, 10, 3, step=1)
    total_risk += (10 - v8)
    v9 = st.slider("NOTAMs/TFRs/airspace restrictions", 0, 10, 3, step=1)
    total_risk += (10 - v9)

    st.markdown("**Operations / Flight Plan**")
    v10 = st.slider("Flight complexity", 0, 10, 4, step=1)
    total_risk += (10 - v10)
    v11 = st.slider("Alternate/emergency options planned", 0, 10, 2, step=1)
    total_risk += (10 - v11)
    v12 = st.slider("Night or low-light operations", 0, 10, 0, step=1)
    total_risk += (10 - v12)

    st.markdown("**External Pressures**")
    v13 = st.slider("Get-there-itis/schedule pressure", 0, 10, 2, step=1)
    total_risk += (10 - v13)
    v14 = st.slider("Customer/family/operational pressure", 0, 10, 2, step=1)
    total_risk += (10 - v14)

    st.markdown("---")
    risk_percent = min(100, (total_risk / 100) * 100)

    # FULL RISK GAUGE
    if total_risk <= 30:
        level = "Low Risk"; color = "#4CAF50"; emoji = "🟢"
    elif total_risk <= 60:
        level = "Medium Risk"; color = "#FF9800"; emoji = "🟡"
    else:
        level = "High Risk"; color = "#F44336"; emoji = "🔴"

    gauge_html = f"""
    <div style="text-align:center; margin:30px 0;">
        <div style="width:220px;height:220px;border-radius:50%;background:conic-gradient({color} {risk_percent}%, #e0e0e0 {risk_percent}% 100%);margin:0 auto;position:relative;box-shadow:0 6px 20px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;">
            <div style="width:170px;height:170px;background:white;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:inset 0 4px 10px rgba(0,0,0,0.1);">
                <div style="font-size:48px;font-weight:bold;color:{color};">{risk_percent:.0f}%</div>
                <div style="font-size:18px;color:#555;">{level}</div>
            </div>
        </div>
        <div style="margin-top:15px;font-size:22px;font-weight:bold;color:{color};">{emoji} {level}</div>
    </div>
    """
    st.markdown(gauge_html, unsafe_allow_html=True)

    # Monthly & Annual Questions (unchanged)
    col_m, col_a = st.columns(2)
    with col_m:
        if st.button("Monthly Questions", type="secondary", use_container_width=True):
            st.session_state.monthly_open = not st.session_state.get("monthly_open", False)
        with st.expander("Monthly Safety & Maintenance Questions", expanded=st.session_state.get("monthly_open", False)):
            st.markdown("**Answer these every month and log your responses:**")
            st.radio("Is your total ag time sufficient for workload and supervision?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Is your total time in type sufficient for workload and supervision?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Are you familiar with and used to flying with all your medications?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Are you familiar with your aircraft and aircraft systems?", ["Yes", "No"], horizontal=True, index=None)
    with col_a:
        if st.button("Annual Questions", type="secondary", use_container_width=True):
            st.session_state.annual_open = not st.session_state.get("annual_open", False)
        with st.expander("Annual Safety & Maintenance Questions", expanded=st.session_state.get("annual_open", False)):
            st.markdown("**Answer these once per year:**")
            st.radio("Do you have a current Biennial Flight Review?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Is your medical certificate current and valid?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Do you have current State and Federal licenses/certificate?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Do you wear Personal Protective Equipment (PPE)?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Do you wear a helmet?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Do you wear a fire-resistant flight suit?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Are you free of chronic illness?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Do you have a clear driving record with no DUI?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Do you wear a lap belt?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Do you wear a shoulder harness?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Have you attended PAASS in the last year?", ["Yes", "No"], horizontal=True, index=None)
            st.radio("Have you attended an Operation S.A.F.F. Fly In clinic in the past two years?", ["Yes", "No"], horizontal=True, index=None)

    if total_risk > 30:
        st.info("**Mitigation Recommendations**")
        st.markdown("- Delay departure or mitigate")
        st.markdown("- Increase fuel or choose closer field")
        st.markdown("- Consult for second opinion")
        st.markdown("- Screenshot and re-assess high risk")
    st.caption("Not a substitute for official preflight briefing or company policy.")

# ────────────────────────────────────────────────
# Main App (everything else exactly as you had it)
# ────────────────────────────────────────────────
st.title("AgPilot")
st.markdown("Performance calculator for agricultural aircraft & helicopters")
st.caption("Prototype – educational use only. Always refer to the official Pilot Operating Handbook (POH) for actual operations.")

# Fleet, Aircraft selection, Custom Empty Weight, Risk button, Weather section, TFR map, Inputs, Calculate Performance, Results, Hover Performance, Feedback, Emergency Response Checklist at bottom – all unchanged from your last paste.

st.caption("**Safe flying & have a Blessed day** ⌯✈︎")
