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
    }
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

@st.cache_data
def compute_landing(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    weight_lbs = min(weight_lbs, data["max_landing_weight_lbs"])
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    ground_roll = adjust_for_weight(data["base_landing_ground_roll_ft"], weight_lbs, data["max_landing_weight_lbs"], exponent=1.0)
    ground_roll = adjust_for_da(ground_roll, da_ft)
    ground_roll = adjust_for_wind(ground_roll, wind_kts)
    ground_roll = adjust_for_runway_condition(ground_roll, runway_condition)
    from_50ft = adjust_for_weight(data["base_landing_to_50ft_ft"], weight_lbs, data["max_landing_weight_lbs"], exponent=1.0)
    from_50ft = adjust_for_da(from_50ft, da_ft)
    from_50ft = adjust_for_wind(from_50ft, wind_kts)
    from_50ft = adjust_for_runway_condition(from_50ft, runway_condition) * 1.15
    return ground_roll, from_50ft

@st.cache_data
def compute_climb_rate(pressure_alt_ft, oat_c, weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    climb = adjust_for_weight(data["base_climb_rate_fpm"], weight_lbs, data["max_takeoff_weight_lbs"], exponent=-1)
    climb *= (1 - (0.05 * da_ft / 1000))
    return max(climb, 0)

@st.cache_data
def compute_stall_speed(weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    return data["base_stall_flaps_down_mph"] * np.sqrt(weight_lbs / data["max_landing_weight_lbs"])

@st.cache_data
def compute_glide_distance(height_ft, wind_kts, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    if is_helicopter:
        # Helicopter autorotation approximation (best range config)
        base_distance_nm = height_ft / 1300  # ~4.5:1 ratio → 1 nm per ~1,300 ft
        wind_factor = 1 + (wind_kts / 20)   # rough wind adjustment
        return base_distance_nm * wind_factor
    else:
        # Fixed-wing airplane glide
        ground_speed_mph = 100 + wind_kts
        return (height_ft / 6076) * data["glide_ratio"] * (ground_speed_mph / 60)

@st.cache_data
def compute_weight_balance(fuel_gal, hopper_gal, pilot_weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    empty_weight = st.session_state.get('custom_empty_weight')
    if empty_weight is None:
        empty_weight = data["base_empty_weight_lbs"]
    else:
        empty_weight = int(empty_weight)
    fuel_weight = fuel_gal * data["fuel_weight_per_gal"]
    hopper_weight = hopper_gal * data["hopper_weight_per_gal"]
    total_weight = empty_weight + fuel_weight + hopper_weight + pilot_weight_lbs
    status = "Within limits" if total_weight <= data["max_takeoff_weight_lbs"] else "Overweight!"
    if total_weight > data["max_landing_weight_lbs"]:
        status += " (Exceeds max landing weight)"
    return total_weight, status

def compute_hover_ceiling(da_ft, weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    base_ceiling_ige = data.get("hover_ceiling_ige_max_gw", 0)
    base_ceiling_oge = data.get("hover_ceiling_oge_max_gw", 0)
    weight_factor = (data["max_takeoff_weight_lbs"] - weight_lbs) / 500.0
    ige_ceiling = base_ceiling_ige + (weight_factor * 1000)
    oge_ceiling = base_ceiling_oge + (weight_factor * 800)
    da_loss = da_ft / 1000 * 1000
    ige_ceiling -= da_loss
    oge_ceiling -= da_loss
    ige_ceiling = max(0, ige_ceiling)
    oge_ceiling = max(0, oge_ceiling)
    return ige_ceiling, oge_ceiling

# ────────────────────────────────────────────────
# Risk Assessment
# ────────────────────────────────────────────────
def show_risk_assessment():
    st.subheader("Risk Assessment")
    st.caption("Score each factor 0–10 (higher = more risk).")
    total_risk = 0
    st.markdown("**Pilot Factors**")
    pilot_exp = st.slider("Recent experience/currency (hours last 30 days)", min_value=0, max_value=10, value=5, step=1)
    total_risk += pilot_exp
    pilot_fatigue = st.slider("Fatigue/sleep last 24 hours", min_value=0, max_value=10, value=5, step=1)
    total_risk += pilot_fatigue
    pilot_health = st.slider("Physical/mental health today", min_value=0, max_value=10, value=2, step=1)
    total_risk += pilot_health
    st.markdown("**Aircraft Factors**")
    ac_maintenance = st.slider("Maintenance status/known squawks", min_value=0, max_value=10, value=3, step=1)
    total_risk += ac_maintenance
    ac_fuel = st.slider("Fuel planning/reserves", min_value=0, max_value=10, value=2, step=1)
    total_risk += ac_fuel
    ac_weight = st.slider("Weight & balance/CG within limits", min_value=0, max_value=10, value=2, step=1)
    total_risk += ac_weight
    st.markdown("**Environment / Weather**")
    weather_ceiling = st.slider("Ceiling/visibility (VFR/IFR conditions)", min_value=0, max_value=10, value=4, step=1)
    total_risk += weather_ceiling
    weather_turb = st.slider("Turbulence/icing/wind forecast", min_value=0, max_value=10, value=3, step=1)
    total_risk += weather_turb
    weather_notams = st.slider("NOTAMs/TFRs/airspace restrictions", min_value=0, max_value=10, value=3, step=1)
    total_risk += weather_notams
    st.markdown("**Operations / Flight Plan**")
    flight_complexity = st.slider("Flight complexity (obstructions/towers/wires/tracklines/birds)", min_value=0, max_value=10, value=4, step=1)
    total_risk += flight_complexity
    alternate_plan = st.slider("Alternate/emergency options planned", min_value=0, max_value=10, value=2, step=1)
    total_risk += alternate_plan
    night_ops = st.slider("Night or low-light operations", min_value=0, max_value=10, value=0, step=1)
    total_risk += night_ops
    st.markdown("**External Pressures**")
    get_there_itis = st.slider("Get-there-itis/schedule pressure", min_value=0, max_value=10, value=2, step=1)
    total_risk += get_there_itis
    customer_pressure = st.slider("Customer/family/operational pressure", min_value=0, max_value=10, value=2, step=1)
    total_risk += customer_pressure
    st.markdown("---")
    risk_percent = (total_risk / 100) * 100
    if total_risk <= 30:
        level = "Low Risk"
        color = "#4CAF50"
        emoji = "🟢"
    elif total_risk <= 60:
        level = "Medium Risk"
        color = "#FF9800"
        emoji = "🟡"
    else:
        level = "High Risk"
        color = "#F44336"
        emoji = "🔴"
    gauge_html = f"""
    <div style="text-align:center; margin: 30px 0;">
        <div style="
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: conic-gradient(
                {color} {risk_percent}%,
                #e0e0e0 {risk_percent}% 100%
            );
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            position: relative;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        ">
            <div style="
                width: 170px;
                height: 170px;
                background: white;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                box-shadow: inset 0 4px 10px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 48px; font-weight: bold; color: {color};">{risk_percent:.0f}%</div>
                <div style="font-size: 18px; color: #555;">{level}</div>
            </div>
        </div>
        <div style="margin-top: 15px; font-size: 22px; font-weight: bold; color: {color};">
            {emoji} {level}
        </div>
    </div>
    """
    st.markdown(gauge_html, unsafe_allow_html=True)
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

# Helicopter detection (moved here after selected_aircraft is defined)
is_helicopter = any(heli in selected_aircraft for heli in [
    "R44", "Bell 206", "Enstrom 480", "Enstrom 480B", "Robinson R66",
    "Airbus AS350", "Enstrom F28F"
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

# Airport Weather & Notices
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
    ground_roll_to, to_50ft = compute_takeoff(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, selected_aircraft)
    ground_roll_land, from_50ft = compute_landing(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, selected_aircraft)
    climb_rate = compute_climb_rate(pressure_alt_ft, oat_c, weight_lbs, selected_aircraft)
    stall_speed = compute_stall_speed(weight_lbs, selected_aircraft)
    glide_dist = compute_glide_distance(glide_height_ft, wind_kts, selected_aircraft)
    total_weight, cg_status = compute_weight_balance(fuel_gal, hopper_gal, pilot_weight_lbs, selected_aircraft)

    st.subheader("Results")
    col_a, col_b = st.columns(2)
    with col_a:
        if is_helicopter:
            st.metric("Takeoff Ground Roll", "Vertical (hover)")
            st.metric("Takeoff to 50 ft", "Vertical performance")
            st.metric("Landing Ground Roll", "Vertical landing")
            st.metric("Landing from 50 ft", "Vertical performance")
        else:
            st.metric("Takeoff Ground Roll", f"{ground_roll_to:.0f} ft")
            st.metric("Takeoff to 50 ft", f"{to_50ft:.0f} ft")
            st.metric("Landing Ground Roll", f"{ground_roll_land:.0f} ft")
            st.metric("Landing from 50 ft", f"{from_50ft:.0f} ft")
    with col_b:
        st.metric("Climb Rate", f"{climb_rate:.0f} fpm")
        st.metric("Best Rate Climb", f"{aircraft_data['best_climb_speed_mph']} mph IAS")
        st.metric("Stall Speed (flaps down)", f"{stall_speed:.1f} mph" if stall_speed > 0 else "N/A (helicopter)")
        st.metric("Glide Distance", f"{glide_dist:.1f} nm")
        if is_helicopter:
            st.caption("Helicopter value = approximate autorotation distance (best range config). "
                       "Actual performance depends on entry airspeed, rotor RPM, flare technique, "
                       "and conditions. Always refer to your aircraft POH.")
        else:
            st.caption("Fixed-wing glide estimate (best glide speed config). Adjust for actual conditions.")

    st.markdown(f"**Total Weight:** {total_weight:.0f} lbs – **{cg_status}**")

    if is_helicopter:
        ige_ceiling, oge_ceiling = compute_hover_ceiling(da_ft, total_weight, selected_aircraft)
        st.subheader("Hover Performance")
        st.metric("Estimated IGE Hover Ceiling", f"{ige_ceiling:.0f} ft")
        st.metric("Estimated OGE Hover Ceiling", f"{oge_ceiling:.0f} ft")
        if total_weight > 2300:
            st.warning("Note: OGE hover at high gross weight may be limited — check POH chart.")
        if da_ft > 8000:
            st.warning("High density altitude — hover performance reduced. Consult POH.")

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

# Feedback
st.markdown("---")
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
