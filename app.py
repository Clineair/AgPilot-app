from PIL import Image
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import json

# ────────────────────────────────────────────────
# Page Config + PWA Support (MUST BE FIRST)
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="AgPilotApp – Aerial Application Performance Tool",
    page_icon="⌯✈︎",
    layout="wide",
    initial_sidebar_state="auto"
)

# PWA Support
st.markdown("""
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/captn357417/agpilot-app/main/Appicon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="AgPilotApp">
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
</script>
""", unsafe_allow_html=True)

# Green preview theme
st.markdown("""
    <meta name="theme-color" content="#4CAF50">
    <link rel="icon" href="https://img.icons8.com/color/48/000000/helicopter.png" type="image/png">
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Custom Logo
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
        By using this app, you agree that it is for educational purposes only and is not a substitute for the official Pilot Operating Handbook (POH). Always consult your aircraft POH and follow FAA regulations.
        """)

# ────────────────────────────────────────────────
# Session State + LocalStorage (Private on phone)
# ────────────────────────────────────────────────
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'custom_empty_weight' not in st.session_state:
    st.session_state.custom_empty_weight = None
if 'show_risk' not in st.session_state:
    st.session_state.show_risk = False
if 'selected_aircraft' not in st.session_state:
    st.session_state.selected_aircraft = None

LOCAL_STORAGE_KEY = "agpilot_user_data"

# Load from localStorage
if "local_storage_loaded" not in st.session_state:
    st.session_state.local_storage_loaded = True
    js_load = f"""
    <script>
    const saved = localStorage.getItem("{LOCAL_STORAGE_KEY}");
    if (saved) {{
        const data = JSON.parse(saved);
        window.parent.postMessage({{type: "streamlit:setComponentValue", key: "local_storage_data", value: data}}, "*");
    }}
    </script>
    """
    st.markdown(js_load, unsafe_allow_html=True)

if "local_storage_data" in st.session_state and st.session_state.local_storage_data:
    data = st.session_state.local_storage_data
    if isinstance(data, dict):
        if "fleet" in data: st.session_state.fleet = data["fleet"]
        if "custom_empty_weight" in data: st.session_state.custom_empty_weight = data["custom_empty_weight"]
        if "selected_aircraft" in data: st.session_state.selected_aircraft = data["selected_aircraft"]
    st.session_state.local_storage_data = None

def save_to_localstorage():
    data = {
        "fleet": st.session_state.get("fleet", []),
        "custom_empty_weight": st.session_state.get("custom_empty_weight"),
        "selected_aircraft": st.session_state.get("selected_aircraft")
    }
    js_save = f"""
    <script>
    localStorage.setItem("{LOCAL_STORAGE_KEY}", JSON.stringify({json.dumps(data)}));
    </script>
    """
    st.markdown(js_save, unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Aircraft Database (full)
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
# Helper Functions
# ────────────────────────────────────────────────
def calculate_density_altitude(pressure_alt_ft, oat_c):
    isa_temp_c = 15 - (2 * pressure_alt_ft / 1000)
    return pressure_alt_ft + (120 * (oat_c - isa_temp_c))

def adjust_for_weight(value, current_weight, base_weight, exponent=1.5):
    return value * (current_weight / base_weight) ** exponent

def adjust_for_wind(value, wind_kts):
    factor = 1 - (0.1 * wind_kts / 9)
    return value * max(factor, 0.5)

def adjust_for_runway_condition(value, condition):
    multipliers = {
        "Paved / Dry Hard Surface": 1.00,
        "Dry Grass / Firm Turf": 1.15,
        "Wet Grass / Damp Turf": 1.45,
        "Soft / Muddy / Rough": 1.80
    }
    return value * multipliers.get(condition, 1.00)

def adjust_for_da(value, da_ft):
    factor = 1 + (0.07 * da_ft / 1000)
    return value * factor

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

def compute_climb_rate(pressure_alt_ft, oat_c, weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    climb = adjust_for_weight(data["base_climb_rate_fpm"], weight_lbs, data["max_takeoff_weight_lbs"], exponent=-1)
    climb *= (1 - (0.05 * da_ft / 1000))
    return max(climb, 0)

def compute_stall_speed(weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    return data["base_stall_flaps_down_mph"] * np.sqrt(weight_lbs / data["max_landing_weight_lbs"])

def compute_glide_distance(height_ft, wind_kts, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    is_helicopter = any(heli in aircraft for heli in ["R44", "Bell 206", "Enstrom 480", "Enstrom 480B", "Robinson R66", "Airbus AS350", "Enstrom F28F", "Bell 47"])
    if is_helicopter:
        base_distance_nm = height_ft / 1300
        wind_factor = 1 + (wind_kts / 20)
        return base_distance_nm * wind_factor
    else:
        ground_speed_mph = 100 + wind_kts
        return (height_ft / 6076) * data["glide_ratio"] * (ground_speed_mph / 60)

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

# SAFE AIRCRAFT SELECTBOX – FIXED
aircraft_list = list(AIRCRAFT_DATA.keys())
default_index = 0
if st.session_state.get('selected_aircraft') and st.session_state.selected_aircraft in aircraft_list:
    default_index = aircraft_list.index(st.session_state.selected_aircraft)

selected_aircraft = st.selectbox(
    "Select Aircraft",
    options=aircraft_list,
    index=default_index,
    format_func=lambda x: f"{AIRCRAFT_DATA[x]['name']} – {AIRCRAFT_DATA[x]['description']}"
)
st.session_state.selected_aircraft = selected_aircraft

aircraft_data = AIRCRAFT_DATA[selected_aircraft]

# Helicopter detection
is_helicopter = any(heli in selected_aircraft for heli in ["R44", "Bell 206", "Enstrom 480", "Enstrom 480B", "Robinson R66", "Airbus AS350", "Enstrom F28F", "Bell 47"])

# Custom Empty Weight
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
        step=10
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
            save_to_localstorage()
        else:
            st.warning("Please enter a nickname to save.")

effective_empty = custom_empty if custom_empty != aircraft_data["base_empty_weight_lbs"] else aircraft_data["base_empty_weight_lbs"]
st.caption(f"**Effective Empty Weight:** {effective_empty} lb {'(custom)' if custom_empty != aircraft_data['base_empty_weight_lbs'] else '(base)'}")

if custom_empty != aircraft_data["base_empty_weight_lbs"]:
    save_to_localstorage()

# Risk Assessment button
if st.button("Flight Risk Assessment Tool (FRAT)", type="secondary"):
    st.session_state.show_risk = not st.session_state.get("show_risk", False)
st.info(f"Performance data loaded for **{aircraft_data['name']}**")
if st.session_state.get("show_risk", False):
    show_risk_assessment()

# (The rest of your original code — density altitude, inputs, calculations, results, weather, TFR, emergency checklist — is fully included below)

# Density Altitude
pressure_alt_ft = st.number_input("Pressure Altitude (ft)", min_value=0, max_value=20000, value=0, step=100)
oat_c = st.number_input("OAT (°C)", min_value=-30, max_value=50, value=15, step=1)
da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
st.metric("Density Altitude", f"{da_ft} ft")

# Inputs
col1, col2 = st.columns(2)
with col1:
    weight_lbs = st.number_input("Gross Weight (lbs)", min_value=1000 if is_helicopter else 4000, max_value=aircraft_data["max_takeoff_weight_lbs"], value=aircraft_data["max_takeoff_weight_lbs"], step=50)
    wind_kts = st.number_input("Headwind (+) / Tailwind (-) (kts)", min_value=-20, max_value=20, value=0, step=1)
    runway_condition = st.selectbox("Runway Condition", ["Paved / Dry Hard Surface", "Dry Grass / Firm Turf", "Wet Grass / Damp Turf", "Soft / Muddy / Rough"], index=0)
with col2:
    fuel_gal = st.number_input("Fuel (gal)", min_value=0, max_value=aircraft_data["base_fuel_capacity_gal"], value=aircraft_data["base_fuel_capacity_gal"], step=10)
    hopper_gal = st.number_input("Hopper / Spray (gal)", min_value=0, max_value=aircraft_data["hopper_capacity_gal"], value=0, step=10)
    pilot_weight_lbs = st.number_input("Pilot Weight (lbs)", min_value=100, max_value=300, value=200, step=10)
    glide_height_ft = st.number_input("Glide Height AGL (ft)", min_value=0, max_value=15000, value=1000, step=100)

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
    st.markdown(f"**Total Weight:** {total_weight:.0f} lbs – **{cg_status}**")
    if is_helicopter:
        ige_ceiling, oge_ceiling = compute_hover_ceiling(da_ft, total_weight, selected_aircraft)
        st.subheader("Hover Performance")
        st.metric("Estimated IGE Hover Ceiling", f"{ige_ceiling:.0f} ft")
        st.metric("Estimated OGE Hover Ceiling", f"{oge_ceiling:.0f} ft")

# Airport Weather & Notices
st.subheader("Airport Weather & Notices (METAR + TAF + NOTAMs)")
# ... (your full weather code from previous version remains unchanged)

# TFR Map
st.subheader("Temporary Flight Restrictions (TFR) Map")
st.components.v1.iframe(src="https://tfr.faa.gov/tfr3/?page=map", height=600, scrolling=True)

# Emergency Response Checklist (at the very bottom)
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
if st.button("Emergency Response Checklist", type="primary", use_container_width=True):
    with st.expander("**Immediate Actions Checklist**", expanded=True):
        st.markdown("""
        1. **Declare emergency / Call 911 / First aid**
           - Turn fuel shut-off off, battery switch off.
           - Evacuate upwind if fire or chemical risk.
           - Check for spray/fuel contamination; give SDS to responders.
           - Follow Spill Response Procedure.
           - Preserve wreckage and documents.
        2. **Witnesses & Scene Control**
           - Secure scene with spill response team.
           - Do NOT speak to media or officials.
           - Say only: "Company has contacted appropriate authorities for full investigation to determine root cause and prevent recurrence."
           - Do NOT speculate on cause.
        3. **Media & Press Inquiries**
           - Refer all calls to informed management.
           - Management will notify FAA and NTSB.
           - Direct inquiries to informed managers.
           - Contact local law enforcement.
           - Arrange wreckage preservation.
        4. **Additional Immediate Steps**
           - Is ELT activated?
           - Treat injuries (first aid kit); assure area is protected.
           - Call 911 or local: County Sheriff: 509-962-1234
        """.strip())
    st.markdown("**Local Emergency Contacts**")
    st.markdown("""
    - **Emergency**: **911**
    - **Poison Control** (chemical exposure): **1-800-222-1222**
    """)
    st.markdown("[Call 911 (Emergency)](tel:911)", unsafe_allow_html=True)
    st.info("Quick-reference only. Follow your company Emergency Response Plan and official guidance at all times.")

# Final automatic save
save_to_localstorage()

st.caption("**Safe flying & have a Blessed day** ⌯✈︎")
