import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ────────────────────────────────────────────────
# Session State Initialization
# ────────────────────────────────────────────────
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'custom_empty_weight' not in st.session_state:
    st.session_state.custom_empty_weight = None
if 'show_empty_weight_input' not in st.session_state:
    st.session_state.show_empty_weight_input = False
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
        "hopper_weight_per_gal": 8.0,
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
        "hopper_weight_per_gal": 8.0,
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
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 16000,
        "max_landing_weight_lbs": 14000,
        "glide_ratio": 7.0,
        "description": "Large turbine ag aircraft – high payload & range"
    },
    "Air Tractor AT-602": {
        "name": "Air Tractor AT-602",
        "base_takeoff_ground_roll_ft": 1830,
        "base_takeoff_to_50ft_ft": 3500,
        "base_landing_ground_roll_ft": 1300,
        "base_landing_to_50ft_ft": 2200,
        "base_climb_rate_fpm": 650,
        "base_stall_flaps_down_mph": 82,
        "best_climb_speed_mph": 125,
        "base_empty_weight_lbs": 5829,
        "base_fuel_capacity_gal": 216,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 630,
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 12500,
        "max_landing_weight_lbs": 12000,
        "glide_ratio": 7.5,
        "description": "Mid-size turbine ag aircraft – 630 gal hopper, high productivity"
    },
    "Air Tractor AT-402": {
        "name": "Air Tractor AT-402",
        "base_takeoff_ground_roll_ft": 1200,
        "base_takeoff_to_50ft_ft": 2500,
        "base_landing_ground_roll_ft": 800,
        "base_landing_to_50ft_ft": 1800,
        "base_climb_rate_fpm": 1100,
        "base_stall_flaps_down_mph": 73,
        "best_climb_speed_mph": 110,
        "base_empty_weight_lbs": 4135,
        "base_fuel_capacity_gal": 170,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 400,
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 7860,
        "max_landing_weight_lbs": 7000,
        "glide_ratio": 7.8,
        "description": "Early turbine ag aircraft – PT6A-15AG, compact & efficient"
    },
    "Air Tractor AT-402B": {
        "name": "Air Tractor AT-402B",
        "base_takeoff_ground_roll_ft": 975,
        "base_takeoff_to_50ft_ft": 2200,
        "base_landing_ground_roll_ft": 900,
        "base_landing_to_50ft_ft": 2000,
        "base_climb_rate_fpm": 800,
        "base_stall_flaps_down_mph": 53,
        "best_climb_speed_mph": 105,
        "base_empty_weight_lbs": 4299,
        "base_fuel_capacity_gal": 170,
        "fuel_weight_per_gal": 6.7,
        "hopper_capacity_gal": 400,
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 9170,
        "max_landing_weight_lbs": 7000,
        "glide_ratio": 7.8,
        "description": "Upgraded turbine ag aircraft – PT6A-15AG, higher useful load"
    },
    "Air Tractor AT-401": {
        "name": "Air Tractor AT-401",
        "base_takeoff_ground_roll_ft": 1318,
        "base_takeoff_to_50ft_ft": 2500,
        "base_landing_ground_roll_ft": 900,
        "base_landing_to_50ft_ft": 1800,
        "base_climb_rate_fpm": 1100,
        "base_stall_flaps_down_mph": 61,
        "best_climb_speed_mph": 110,
        "base_empty_weight_lbs": 4135,
        "base_fuel_capacity_gal": 170,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 400,
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 7860,
        "max_landing_weight_lbs": 7000,
        "glide_ratio": 7.8,
        "description": "Radial piston ag aircraft (R-1340 600 hp) – reliable workhorse"
    },
    "Grumman G-164B Ag-Cat": {
        "name": "Grumman G-164B Ag-Cat",
        "base_takeoff_ground_roll_ft": 1300,
        "base_takeoff_to_50ft_ft": 2500,
        "base_landing_ground_roll_ft": 950,
        "base_landing_to_50ft_ft": 1800,
        "base_climb_rate_fpm": 1000,
        "base_stall_flaps_down_mph": 60,
        "best_climb_speed_mph": 105,
        "base_empty_weight_lbs": 3150,
        "base_fuel_capacity_gal": 170,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 400,
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 7020,
        "max_landing_weight_lbs": 6500,
        "glide_ratio": 8.0,
        "description": "Classic radial biplane ag aircraft – rugged, low stall speed, excellent for low-level work"
    },
    "Piper PA-36 Pawnee Brave": {
        "name": "Piper PA-36 Pawnee Brave",
        "base_takeoff_ground_roll_ft": 1470,
        "base_takeoff_to_50ft_ft": 2225,
        "base_landing_ground_roll_ft": 1100,
        "base_landing_to_50ft_ft": 2000,
        "base_climb_rate_fpm": 920,
        "base_stall_flaps_down_mph": 60,
        "best_climb_speed_mph": 105,
        "base_empty_weight_lbs": 2465,
        "base_fuel_capacity_gal": 86,
        "fuel_weight_per_gal": 6.0,
        "hopper_capacity_gal": 275,
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 4800,
        "max_landing_weight_lbs": 4400,
        "glide_ratio": 8.0,
        "description": "Piston-powered ag aircraft – reliable, low stall, good short-field performer"
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
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 2500,
        "max_landing_weight_lbs": 2500,
        "glide_ratio": 4.0,
        "description": "Light utility helicopter – IGE hover performance only (non-linear POH approx.)"
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
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 3200,
        "max_landing_weight_lbs": 3200,
        "glide_ratio": 4.0,
        "description": "Light utility helicopter (spray capable but under construction)",
        "hover_ceiling_ige_max_gw": 12800,
        "hover_ceiling_oge_max_gw": 8800
    },
}

# ────────────────────────────────────────────────
# Runway Condition Factors
# ────────────────────────────────────────────────
RUNWAY_CONDITIONS = {
    "Paved - Dry": {"takeoff": 1.00, "landing": 1.00, "risk": 0},
    "Paved - Wet": {"takeoff": 1.15, "landing": 1.30, "risk": 4},
    "Grass - Firm/Dry": {"takeoff": 1.10, "landing": 1.15, "risk": 3},
    "Grass - Soft/Wet": {"takeoff": 1.40, "landing": 1.60, "risk": 10},
    "Dirt - Firm/Dry": {"takeoff": 1.20, "landing": 1.25, "risk": 5},
    "Dirt - Soft/Muddy": {"takeoff": 1.60, "landing": 1.80, "risk": 14},
    "Short/Uneven/Unimproved": {"takeoff": 1.45, "landing": 1.55, "risk": 12},
}

# ────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────
def calculate_density_altitude(pressure_alt_ft, oat_c):
    isa_temp_c = 15 - (2 * pressure_alt_ft / 1000)
    da = pressure_alt_ft + (120 * (oat_c - isa_temp_c))
    return da

def adjust_for_weight(value, current_weight, base_weight, exponent=1.5):
    return value * (current_weight / base_weight) ** exponent

def adjust_for_wind(value, wind_kts):
    factor = 1 - (0.1 * wind_kts / 9)
    return value * max(factor, 0.5)

def adjust_for_da(value, da_ft):
    factor = 1 + (0.07 * da_ft / 1000)
    return value * factor

def adjust_for_runway(value, condition, phase="takeoff"):
    return value * RUNWAY_CONDITIONS[condition][phase]

@st.cache_data
def compute_takeoff(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    
    ground_roll = adjust_for_weight(data["base_takeoff_ground_roll_ft"], weight_lbs, data["max_takeoff_weight_lbs"])
    ground_roll = adjust_for_da(ground_roll, da_ft)
    ground_roll = adjust_for_wind(ground_roll, wind_kts)
    ground_roll = adjust_for_runway(ground_roll, runway_condition, "takeoff")
    
    to_50ft = adjust_for_weight(data["base_takeoff_to_50ft_ft"], weight_lbs, data["max_takeoff_weight_lbs"])
    to_50ft = adjust_for_da(to_50ft, da_ft)
    to_50ft = adjust_for_wind(to_50ft, wind_kts)
    to_50ft = adjust_for_runway(to_50ft, runway_condition, "takeoff")
    
    return ground_roll, to_50ft

@st.cache_data
def compute_landing(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    weight_lbs = min(weight_lbs, data["max_landing_weight_lbs"])
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    
    ground_roll = adjust_for_weight(data["base_landing_ground_roll_ft"], weight_lbs, data["max_landing_weight_lbs"], exponent=1.0)
    ground_roll = adjust_for_da(ground_roll, da_ft)
    ground_roll = adjust_for_wind(ground_roll, wind_kts)
    ground_roll = adjust_for_runway(ground_roll, runway_condition, "landing")
    
    from_50ft = adjust_for_weight(data["base_landing_to_50ft_ft"], weight_lbs, data["max_landing_weight_lbs"], exponent=1.0)
    from_50ft = adjust_for_da(from_50ft, da_ft)
    from_50ft = adjust_for_wind(from_50ft, wind_kts)
    from_50ft = adjust_for_runway(from_50ft, runway_condition, "landing")
    
    return ground_roll, from_50ft

@st.cache_data
def compute_climb_rate(pressure_alt_ft, oat_c, weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    climb = adjust_for_weight(data["base_climb_rate_fpm"], weight_lbs, data["max_takeoff_weight_lbs"], exponent=-1)
    climb *= (1 - (0.05 * da_ft / 1000))
    return max(climb, 0)

@st.cache_data
def compute_ige_hover_ceiling(da_ft, weight_lbs, carb_heat_on=False):
    base_ceiling = 11600
    ref_weight = 1800
    weight_excess = max(0, weight_lbs - ref_weight)
    weight_penalty = 0.00012 * weight_excess ** 1.8 + 3.5 * weight_excess
    da_penalty = 0.00008 * da_ft ** 1.9 + 0.07 * da_ft
    ceiling = base_ceiling - weight_penalty - da_penalty
    if carb_heat_on:
        ceiling -= 2400
    if da_ft > 9600:
        ceiling *= 0.75
    return max(0, min(ceiling, 11600))

@st.cache_data
def compute_weight_balance(fuel_gal, hopper_gal, pilot_weight_lbs, aircraft, custom_empty=None):
    data = AIRCRAFT_DATA[aircraft]
    empty_weight = custom_empty if custom_empty is not None else data["base_empty_weight_lbs"]
    fuel_weight = fuel_gal * data["fuel_weight_per_gal"]
    hopper_weight = hopper_gal * data["hopper_weight_per_gal"]
    total_weight = empty_weight + fuel_weight + hopper_weight + pilot_weight_lbs
    status = "Within limits" if total_weight <= data["max_takeoff_weight_lbs"] else "Overweight!"
    if total_weight > data["max_landing_weight_lbs"]:
        status += " (Exceeds max landing weight)"
    return total_weight, status

# ────────────────────────────────────────────────
# Risk Assessment with Animated Gauge
# ────────────────────────────────────────────────
def show_risk_assessment(da_ft, weight_lbs, wind_kts, ground_roll_to, runway_length_ft, runway_condition, aircraft, ige_ceiling=None):
    st.subheader("Risk Indicator – Bonanza Performance Style")

    total_risk = 0
    max_risk = 100

    da_risk = min(20, max(0, int((da_ft - 1500)/1000)*5))
    total_risk += da_risk

    weight_pct = weight_lbs / AIRCRAFT_DATA[aircraft]["max_takeoff_weight_lbs"]
    weight_risk = min(15, int((weight_pct - 0.75)*100)) if weight_pct > 0.75 else 0
    total_risk += weight_risk

    runway_length_risk = 12
    if runway_length_ft:
        margin_pct = (runway_length_ft - ground_roll_to) / runway_length_ft if runway_length_ft > 0 else 0
        runway_length_risk = 0 if margin_pct >= 0.5 else 8 if margin_pct >= 0.25 else 18
    total_risk += runway_length_risk

    surface_risk = RUNWAY_CONDITIONS[runway_condition]["risk"]
    total_risk += surface_risk

    fatigue = st.slider("Fatigue level (long day)", 0, 10, 4, key="fatigue_risk")
    total_risk += fatigue * 1.5

    pressure = st.slider("Get-it-done pressure", 0, 10, 3, key="pressure_risk")
    total_risk += pressure * 1.2

    if ige_ceiling is not None:
        hover_risk = 20 if ige_ceiling < 2000 else 12 if ige_ceiling < 5000 else 0
        total_risk += hover_risk

    total_risk = min(total_risk, max_risk)
    risk_percent = total_risk

    if risk_percent <= 35:
        level = "Low Risk"
        color = "#4CAF50"
        emoji = "🟢"
    elif risk_percent <= 65:
        level = "Medium Risk"
        color = "#FF9800"
        emoji = "🟡"
    else:
        level = "High Risk"
        color = "#F44336"
        emoji = "🔴"

    gauge_html = f"""
    <style>
        @keyframes needle-sweep {{
            from {{ transform: translate(-50%, -100%) rotate(-90deg); }}
            to {{ transform: translate(-50%, -100%) rotate({risk_percent * 1.8 - 90}deg); }}
        }}
        .gauge-container {{
            text-align: center;
            margin: 40px 0;
        }}
        .gauge {{
            width: 280px; height: 280px; border-radius: 50%;
            background: radial-gradient(circle at 50% 120%, #333 0%, #111 70%, #000 100%),
                        conic-gradient(#00ff00 0% 35%, #ffcc00 35% 65%, #ff0000 65% 100%);
            position: relative; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        }}
        .needle {{
            position: absolute; top: 50%; left: 50%;
            width: 4px; height: 120px; background: white; border-radius: 2px;
            transform-origin: bottom; box-shadow: 0 0 10px white;
            animation: needle-sweep 1.2s ease-out forwards;
        }}
        .hub {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 100px; height: 100px; background: #222; border-radius: 50%;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }}
        .percent {{ font-size: 48px; font-weight: bold; color: {color}; }}
        .label {{ font-size: 16px; color: #555; }}
    </style>
    <div class="gauge-container">
        <div class="gauge">
            <div class="needle"></div>
            <div class="hub">
                <div class="percent">{risk_percent:.0f}</div>
                <div class="label">%</div>
            </div>
        </div>
        <div style="margin-top: 20px; font-size: 24px; font-weight: bold; color: {color};">
            {emoji} {level}
        </div>
    </div>
    """
    st.markdown(gauge_html, unsafe_allow_html=True)

    if risk_percent > 35:
        st.info("**Mitigation Suggestions**")
        st.markdown("- Reduce load or wait for better conditions")
        st.markdown("- Improve runway or choose alternate")
        st.markdown("- Address fatigue/pressures")
        st.markdown("- Re-evaluate high factors")

    st.caption("Bonanza-style animated gauge – not a substitute for POH or judgment.")

# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
st.set_page_config(page_title="AgPilot – Aerial Application Performance Tool", layout="wide")
st.title("AgPilot")
st.markdown("Performance calculator for agricultural fixed-wing & helicopters")
st.caption("Prototype – educational use only. Always refer to the official Pilot Operating Handbook (POH) for actual operations.")

# Fleet
st.subheader("My Fleet – Saved Configurations")
if st.session_state.fleet:
    fleet_options = ["— Select from Fleet —"] + [entry['nickname'] for entry in st.session_state.fleet]
    selected_fleet = st.selectbox("Load saved aircraft", fleet_options, index=0)
    if selected_fleet != "— Select from Fleet —":
        entry = next(e for e in st.session_state.fleet if e['nickname'] == selected_fleet)
        selected_aircraft = entry['aircraft']
        st.session_state.custom_empty_weight = entry['empty_weight']
        st.success(f"Loaded {selected_fleet} – Empty Weight: {entry['empty_weight']} lbs")
else:
    st.info("No saved aircraft yet. Adjust empty weight below and save.")

# Aircraft Selection
col_select, col_button = st.columns([4, 1])
with col_select:
    selected_aircraft = st.selectbox(
        "Select Aircraft",
        options=list(AIRCRAFT_DATA.keys()),
        format_func=lambda x: f"{AIRCRAFT_DATA[x]['name']} – {AIRCRAFT_DATA[x]['description']}"
    )
with col_button:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("✏️ Adjust Empty Weight", type="secondary"):
        st.session_state.show_empty_weight_input = not st.session_state.show_empty_weight_input

aircraft_data = AIRCRAFT_DATA[selected_aircraft]
base_empty = aircraft_data["base_empty_weight_lbs"]

if st.session_state.show_empty_weight_input:
    custom_empty = st.number_input(
        f"Custom Empty Weight for {aircraft_data['name']} (lbs)",
        min_value=1000,
        max_value=int(base_empty * 1.5),
        value=base_empty,
        step=10
    )
    st.session_state.custom_empty_weight = custom_empty

    nickname_col, save_col = st.columns([3, 1])
    with nickname_col:
        nickname = st.text_input("Nickname for saving to fleet (e.g., 'My R44')")
    with save_col:
        st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Save to Fleet", disabled=not nickname.strip()):
            new_entry = {'nickname': nickname.strip(), 'aircraft': selected_aircraft, 'empty_weight': custom_empty}
            st.session_state.fleet = [e for e in st.session_state.fleet if e['nickname'] != nickname.strip()]
            st.session_state.fleet.append(new_entry)
            st.success(f"Saved {nickname} to fleet!")
            st.rerun()

effective_empty = st.session_state.custom_empty_weight if st.session_state.custom_empty_weight else base_empty
st.caption(f"Effective empty weight: {effective_empty} lbs {'(custom)' if st.session_state.custom_empty_weight else '(base)'}")

# Risk Button Under Empty Weight
if st.button("Risk Assessment", type="secondary"):
    st.session_state.show_risk = not st.session_state.show_risk

if st.session_state.show_risk:
    show_risk_assessment(da_ft=0, weight_lbs=weight_lbs if 'weight_lbs' in locals() else 5000,
                         wind_kts=0, ground_roll_to=0, runway_length_ft=3000, runway_condition="Paved - Dry",
                         aircraft=selected_aircraft, ige_ceiling=None)

# Inputs
col1, col2 = st.columns(2)
with col1:
    pressure_alt_ft = st.number_input("Pressure Altitude (ft)", 0, 20000, 0, step=100)
    oat_c = st.number_input("OAT (°C)", -30, 50, 15, step=1)
    weight_lbs = st.number_input("Gross Weight (lbs)", 1000, aircraft_data["max_takeoff_weight_lbs"], aircraft_data["max_takeoff_weight_lbs"], step=50)
    wind_kts = st.number_input("Headwind (+) / Tailwind (-) (kts)", -20, 20, 0, step=1)

with col2:
    fuel_gal = st.number_input("Fuel (gal)", 0, aircraft_data["base_fuel_capacity_gal"], aircraft_data["base_fuel_capacity_gal"], step=10)
    hopper_gal = st.number_input("Hopper / Spray Load (gal)", 0, aircraft_data["hopper_capacity_gal"], 0, step=10)
    pilot_weight_lbs = st.number_input("Pilot Weight (lbs)", 100, 300, 200, step=10)
    glide_height_ft = st.number_input("Glide Height AGL (ft)", 0, 15000, 1000, step=100)
    runway_condition = st.selectbox("Runway Condition", list(RUNWAY_CONDITIONS.keys()))
    runway_length_ft = st.number_input("Available Runway (ft)", 1000, 8000, 3000, step=100)
    if "R44" in selected_aircraft:
        carb_heat = st.checkbox("Carb Heat ON (reduces ceilings)", value=False)

# Calculate
if st.button("Calculate Performance", type="primary"):
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    ground_roll_to, to_50ft = compute_takeoff(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, selected_aircraft)
    ground_roll_land, from_50ft = compute_landing(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, selected_aircraft)
    climb_rate = compute_climb_rate(pressure_alt_ft, oat_c, weight_lbs, selected_aircraft)
    stall_speed = compute_stall_speed(weight_lbs, selected_aircraft)
    glide_dist = compute_glide_distance(glide_height_ft, wind_kts, selected_aircraft)
    total_weight, cg_status = compute_weight_balance(fuel_gal, hopper_gal, pilot_weight_lbs, selected_aircraft, st.session_state.custom_empty_weight)

    st.subheader("Results")
    col_a, col_b = st.columns(2)
    with col_a:
        if "R44" in selected_aircraft or "Bell 206" in selected_aircraft:
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

    # Hover for helicopters
    if "R44" in selected_aircraft or "Bell 206" in selected_aircraft:
        ige_ceiling = compute_ige_hover_ceiling(da_ft, total_weight, carb_heat if 'carb_heat' in locals() else False) if "R44" in selected_aircraft else compute_hover_ceiling(da_ft, total_weight, selected_aircraft)[0]
        st.subheader("Hover Performance")
        st.metric("Estimated IGE Hover Ceiling", f"{ige_ceiling:.0f} ft")
        if total_weight > 2300:
            st.warning("Note: Hover at high gross weight may be limited — check POH chart.")
        if da_ft > 8000:
            st.warning("High density altitude — hover performance reduced. Consult POH.")

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

    # Full risk after calc
    show_risk_assessment(da_ft, weight_lbs, wind_kts, ground_roll_to, runway_length_ft, runway_condition, selected_aircraft, ige_ceiling if 'ige_ceiling' in locals() else None)

# Feedback
st.markdown("---")
st.subheader("Your Feedback – Help Improve AgPilot")
rating = st.feedback("stars")
comment = st.text_area("Comments, suggestions, or issues", height=120, placeholder="Ideas? Suggestions? Comments?...")
if st.button("Submit Rating & Comment"):
    if rating is not None:
        stars = rating + 1
        st.success(f"Thank you! You rated **{stars} stars**.")
        if comment.strip():
            st.caption(f"Comment: {comment}")
    else:
        st.warning("Please select a star rating.")
