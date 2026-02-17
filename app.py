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
        "description": "Classic radial biplane ag aircraft – low stall, rugged"
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
# Risk Assessment – 14 sliders + IMSAFE
# ────────────────────────────────────────────────
def show_risk_assessment(da_ft=None, weight_lbs=None, wind_kts=None, ground_roll_to=None, runway_length_ft=None, runway_condition=None, aircraft=None, ige_ceiling=None):
    st.subheader("Risk Assessment – FAA PAVE/IMSAFE")

    st.caption("Begin with IMSAFE (FAA personal fitness), then score each factor 0–10 (higher = more risk).")

    total_risk = 0

    # IMSAFE Checkboxes – unique keys
    st.markdown("**IMSAFE – Illness, Medication, Stress, Alcohol, Fatigue, Emotion** (FAA personal fitness check)")
    ims_points = 0
    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("Illness / feeling unwell today?", value=False, key="ims_illness"):
            ims_points += 10
        if st.checkbox("Taking any medication?", value=False, key="ims_med"):
            ims_points += 10
        if st.checkbox("High stress / emotional state?", value=False, key="ims_stress"):
            ims_points += 8
    with col2:
        if st.checkbox("Alcohol in last 8–24 hours?", value=False, key="ims_alcohol"):
            ims_points += 12
        if st.checkbox("Fatigue / poor sleep?", value=False, key="ims_fatigue"):
            ims_points += 12
        if st.checkbox("Get-there-itis / strong external pressure?", value=False, key="ims_egt"):
            ims_points += 10

    total_risk += ims_points
    if ims_points > 0:
        st.warning(f"IMSAFE flags detected ({ims_points} risk points). Consider delaying flight.")

    # NOTAMs / TFRs – unique key
    if not st.checkbox("Checked current NOTAMs / TFRs / airspace restrictions?", value=True, key="notams_tfrs_checked"):
        total_risk += 15

    # 14 Sliders – unique keys
    st.markdown("**Detailed PAVE Checklist Scoring** (0–10, higher = more risk)")

    st.markdown("**Pilot Factors** (beyond IMSAFE)")
    pilot_exp = st.slider("Recent experience/currency (hours last 30 days)", 0, 10, 5, step=1, key="pilot_exp")
    total_risk += pilot_exp
    pilot_fatigue = st.slider("Fatigue/sleep last 24 hours", 0, 10, 5, step=1, key="pilot_fatigue")
    total_risk += pilot_fatigue
    pilot_health = st.slider("Physical/mental health today", 0, 10, 2, step=1, key="pilot_health")
    total_risk += pilot_health

    st.markdown("**Aircraft Factors**")
    ac_maintenance = st.slider("Maintenance status/known squawks", 0, 10, 3, step=1, key="ac_maintenance")
    total_risk += ac_maintenance
    ac_fuel = st.slider("Fuel planning/reserves", 0, 10, 2, step=1, key="ac_fuel")
    total_risk += ac_fuel
    ac_weight = st.slider("Weight & balance/CG within limits", 0, 10, 2, step=1, key="ac_weight")
    total_risk += ac_weight

    st.markdown("**Environment / Weather**")
    weather_ceiling = st.slider("Ceiling/visibility (VFR/IFR conditions)", 0, 10, 4, step=1, key="weather_ceiling")
    total_risk += weather_ceiling
    weather_turb = st.slider("Turbulence/icing/wind forecast", 0, 10, 3, step=1, key="weather_turb")
    total_risk += weather_turb
    weather_notams = st.slider("NOTAMs/TFRs/airspace restrictions", 0, 10, 3, step=1, key="weather_notams")
    total_risk += weather_notams

    st.markdown("**Operations / Flight Plan**")
    flight_complexity = st.slider("Flight complexity (obstructions/towers/wires)", 0, 10, 4, step=1, key="flight_complexity")
    total_risk += flight_complexity
    alternate_plan = st.slider("Alternate/emergency options planned", 0, 10, 2, step=1, key="alternate_plan")
    total_risk += alternate_plan
    night_ops = st.slider("Night or low-light operations", 0, 10, 0, step=1, key="night_ops")
    total_risk += night_ops

    st.markdown("**External Pressures**")
    get_there_itis = st.slider("Get-there-itis/schedule pressure", 0, 10, 2, step=1, key="get_there_itis")
    total_risk += get_there_itis
    customer_pressure = st.slider("Customer/family/operational pressure", 0, 10, 2, step=1, key="customer_pressure")
    total_risk += customer_pressure

    # Normalize to 0–100%
    risk_percent = min(total_risk / 1.8, 100)

    # Level & color
    if risk_percent <= 35:
        level = "Low Risk – Go"
        color = "#4CAF50"
        emoji = "🟢"
    elif risk_percent <= 65:
        level = "Medium Risk – Mitigate"
        color = "#FF9800"
        emoji = "🟡"
    else:
        level = "High Risk – No-Go / Replan"
        color = "#F44336"
        emoji = "🔴"

    # Animated gauge with needle
    gauge_html = f"""
    <style>
        @keyframes needle-sweep {{
            from {{ transform: translate(-50%, -100%) rotate(-90deg); }}
            to {{ transform: translate(-50%, -100%) rotate({risk_percent * 1.8 - 90}deg); }}
        }}
        .gauge-container {{ text-align: center; margin: 40px auto; width: 320px; }}
        .gauge {{
            width: 300px; height: 300px; border-radius: 50%;
            background: radial-gradient(circle at 50% 120%, #444 0%, #111 70%, #000 100%),
                        conic-gradient(#00ff00 0% 35%, #ffcc00 35% 65%, #ff0000 65% 100%);
            position: relative; box-shadow: 0 12px 40px rgba(0,0,0,0.7); border: 10px solid #222;
        }}
        .needle {{
            position: absolute; top: 50%; left: 50%;
            width: 6px; height: 135px; background: linear-gradient(to top, #fff, #eee);
            border-radius: 3px 3px 0 0; transform-origin: bottom;
            transform: translate(-50%, -100%) rotate(-90deg);
            animation: needle-sweep 1.4s ease-out forwards;
            box-shadow: 0 0 15px rgba(255,255,255,0.9); z-index: 5;
        }}
        .hub {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 120px; height: 120px; background: #1a1a1a; border-radius: 50%;
            border: 8px solid #444; box-shadow: inset 0 0 25px #000;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            color: white; z-index: 10;
        }}
        .percent {{ font-size: 58px; font-weight: bold; color: {color}; }}
        .label {{ font-size: 18px; color: #aaa; }}
    </style>

    <div class="gauge-container">
        <div class="gauge">
            <div class="needle"></div>
            <div class="hub">
                <div class="percent">{risk_percent:.0f}</div>
                <div class="label">%</div>
            </div>
        </div>
        <div style="margin-top: 25px; font-size: 28px; font-weight: bold; color: {color};">
            {emoji} {level}
        </div>
    </div>
    """

    st.markdown(gauge_html, unsafe_allow_html=True)

    if risk_percent > 35:
        st.info("**Mitigation Recommendations (FAA Guidance)**")
        st.markdown("""
        - Address any IMSAFE items before flight
        - Re-check weather, NOTAMs/TFRs, personal minimums
        - Reduce load / wait for better DA / runway
        - Consult another pilot
        - Document decisions and re-assess
        """)

    st.caption("FAA PAVE/IMSAFE-inspired • Bonanza-style animated gauge • Not a substitute for official briefing/POH.")

# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
st.set_page_config(page_title="AgPilot", layout="wide")
st.title("AgPilot – Aerial Application Performance Tool")
st.caption("Prototype – educational use only. Always refer to official POH.")

# Fleet Section
st.subheader("My Fleet")
if st.session_state.fleet:
    fleet_options = ["— Select —"] + [e['nickname'] for e in st.session_state.fleet]
    selected_fleet = st.selectbox("Load saved aircraft", fleet_options)
    if selected_fleet != "— Select —":
        entry = next(e for e in st.session_state.fleet if e['nickname'] == selected_fleet)
        selected_aircraft = entry['aircraft']
        st.session_state.custom_empty_weight = entry['empty_weight']
        st.success(f"Loaded **{selected_fleet}** – Empty: {entry['empty_weight']} lbs")
else:
    st.info("No saved aircraft yet.")

# Aircraft Selection + Empty Weight
col_select, col_button = st.columns([5, 1])
with col_select:
    selected_aircraft = st.selectbox("Select Aircraft", list(AIRCRAFT_DATA.keys()),
                                     format_func=lambda x: f"{AIRCRAFT_DATA[x]['name']} – {AIRCRAFT_DATA[x]['description']}")
with col_button:
    if st.button("✏️ Empty Weight", type="secondary"):
        st.session_state.show_empty_weight_input = not st.session_state.show_empty_weight_input

data = AIRCRAFT_DATA[selected_aircraft]
base_empty = data["base_empty_weight_lbs"]

if st.session_state.show_empty_weight_input:
    custom_empty = st.number_input(f"Custom Empty Weight (lbs) for {data['name']}",
                                   min_value=1000, max_value=int(base_empty * 1.5),
                                   value=base_empty, step=10)
    st.session_state.custom_empty_weight = custom_empty

    nickname = st.text_input("Nickname for Fleet (required to save)")
    if st.button("💾 Save to Fleet", type="primary", disabled=not nickname.strip()):
        new_entry = {'nickname': nickname.strip(), 'aircraft': selected_aircraft, 'empty_weight': custom_empty}
        st.session_state.fleet = [e for e in st.session_state.fleet if e['nickname'] != nickname.strip()]
        st.session_state.fleet.append(new_entry)
        st.success(f"Saved **{nickname}**!")
        st.rerun()

effective_empty = st.session_state.custom_empty_weight if st.session_state.custom_empty_weight else base_empty
st.caption(f"Empty weight: **{effective_empty} lbs** {'(custom)' if st.session_state.custom_empty_weight else '(base)'}")

# Risk Assessment Button (under Empty Weight)
st.markdown("### Safety Check")
if st.button("Risk Assessment", type="secondary"):
    st.session_state.show_risk = not st.session_state.show_risk

if st.session_state.show_risk:
    show_risk_assessment()

# Inputs
col1, col2 = st.columns(2)
with col1:
    pressure_alt_ft = st.number_input("Pressure Altitude (ft)", 0, 20000, 0, step=100)
    oat_c = st.number_input("OAT (°C)", -30, 50, 15, step=1)
    weight_lbs = st.number_input("Gross Weight (lbs)", 1000, data["max_takeoff_weight_lbs"], data["max_takeoff_weight_lbs"], step=50)
    wind_kts = st.number_input("Headwind (+) / Tailwind (-) (kts)", -20, 20, 0, step=1)

with col2:
    fuel_gal = st.number_input("Fuel (gal)", 0, data["base_fuel_capacity_gal"], data["base_fuel_capacity_gal"], step=10)
    hopper_gal = st.number_input("Hopper Load (gal)", 0, data["hopper_capacity_gal"], 0, step=10)
    pilot_weight_lbs = st.number_input("Pilot Weight (lbs)", 100, 300, 200, step=10)
    runway_condition = st.selectbox("Runway Condition", list(RUNWAY_CONDITIONS.keys()))
    runway_length_ft = st.number_input("Available Runway (ft)", 1000, 8000, 3000, step=100)
    if "R44" in selected_aircraft:
        carb_heat = st.checkbox("Carb Heat ON (reduces ceilings)", value=False)

# Calculate Button
if st.button("Calculate Performance", type="primary"):
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    
    if "R44" in selected_aircraft:
        ige_ceiling = compute_ige_hover_ceiling(da_ft, weight_lbs, carb_heat if 'carb_heat' in locals() else False)
        st.subheader("R44 Raven II IGE Hover Performance")
        st.metric("IGE Hover Ceiling", f"{ige_ceiling:.0f} ft")
        if ige_ceiling < 1000:
            st.error("Marginal/no IGE hover – reduce weight or DA.")
    else:
        gr_to, to_50 = compute_takeoff(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, selected_aircraft)
        gr_land, from_50 = compute_landing(pressure_alt_ft, oat_c, weight_lbs, wind_kts, runway_condition, selected_aircraft)
        climb = compute_climb_rate(pressure_alt_ft, oat_c, weight_lbs, selected_aircraft)

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Takeoff Ground Roll", f"{gr_to:.0f} ft")
            st.metric("Takeoff to 50 ft", f"{to_50:.0f} ft")
        with col_b:
            st.metric("Landing Ground Roll", f"{gr_land:.0f} ft")
            st.metric("Landing from 50 ft", f"{from_50:.0f} ft")
            st.metric("Climb Rate", f"{climb:.0f} fpm")

    total_weight, status = compute_weight_balance(fuel_gal, hopper_gal, pilot_weight_lbs, selected_aircraft, st.session_state.custom_empty_weight)
    st.markdown(f"**Total Weight:** {total_weight:.0f} lbs – **{status}**")

    # Optional: Show risk with real values after calculation
    show_risk_assessment(
        da_ft=da_ft,
        weight_lbs=weight_lbs,
        wind_kts=wind_kts,
        ground_roll_to=gr_to if 'gr_to' in locals() else 0,
        runway_length_ft=runway_length_ft,
        runway_condition=runway_condition,
        aircraft=selected_aircraft,
        ige_ceiling=ige_ceiling if 'ige_ceiling' in locals() else None
    )

st.markdown("---")
st.caption("Prototype – always use official POH. Feedback welcome!")
