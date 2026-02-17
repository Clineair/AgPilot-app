import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ────────────────────────────────────────────────
# Session State Initialization
# ────────────────────────────────────────────────
if 'fleet' not in st.session_state:
    st.session_state.fleet = []  # [{'nickname': str, 'aircraft': str, 'empty_weight': int}]
if 'custom_empty_weight' not in st.session_state:
    st.session_state.custom_empty_weight = None
if 'show_empty_weight_input' not in st.session_state:
    st.session_state.show_empty_weight_input = False

# ────────────────────────────────────────────────
# Aircraft Database (updated with all requested models)
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
    # Add Bell 206 if desired...
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
# Risk Assessment (Bonanza-style, with runway & hover)
# ────────────────────────────────────────────────
def show_risk_assessment(da_ft, weight_lbs, wind_kts, ground_roll_to, runway_length_ft, runway_condition, aircraft, ige_ceiling=None):
    st.subheader("Risk Indicator")
    total_risk = 0
    max_risk = 100
    factors = {}

    da_risk = min(20, max(0, int((da_ft - 1500)/1000)*5))
    total_risk += da_risk
    factors["Density Altitude"] = da_risk

    weight_pct = weight_lbs / AIRCRAFT_DATA[aircraft]["max_takeoff_weight_lbs"]
    weight_risk = min(15, int((weight_pct - 0.75)*100)) if weight_pct > 0.75 else 0
    total_risk += weight_risk
    factors["Gross Weight"] = weight_risk

    if runway_length_ft:
        margin_pct = (runway_length_ft - ground_roll_to) / runway_length_ft if runway_length_ft > 0 else 0
        runway_length_risk = 0 if margin_pct >= 0.5 else 8 if margin_pct >= 0.25 else 18
    else:
        runway_length_risk = 12
    total_risk += runway_length_risk
    factors["Runway Margin"] = runway_length_risk

    surface_risk = RUNWAY_CONDITIONS[runway_condition]["risk"]
    total_risk += surface_risk
    factors["Runway Surface"] = surface_risk

    fatigue = st.slider("Fatigue level", 0, 10, 4)
    total_risk += fatigue * 1.5

    pressure = st.slider("Schedule pressure", 0, 10, 3)
    total_risk += pressure * 1.2

    if ige_ceiling is not None:
        hover_risk = 20 if ige_ceiling < 2000 else 12 if ige_ceiling < 5000 else 0
        total_risk += hover_risk
        factors["IGE Hover"] = hover_risk

    total_risk = min(total_risk, max_risk)
    risk_percent = total_risk

    if risk_percent <= 35:
        level, color = "Low", "#4CAF50"
    elif risk_percent <= 65:
        level, color = "Medium", "#FF9800"
    else:
        level, color = "High", "#F44336"

    gauge_html = f"""
    <div style="text-align:center; margin:25px 0;">
        <div style="width:220px;height:220px;border-radius:50%;background:conic-gradient({color} {risk_percent}%,#e0e0e0 {risk_percent}% 100%);margin:0 auto;position:relative;">
            <div style="width:160px;height:160px;background:white;border-radius:50%;position:absolute;top:30px;left:30px;display:flex;align-items:center;justify-content:center;flex-direction:column;">
                <div style="font-size:46px;font-weight:bold;color:{color};">{risk_percent:.0f}%</div>
                <div style="font-size:18px;">{level} Risk</div>
            </div>
        </div>
    </div>
    """
    st.markdown(gauge_html, unsafe_allow_html=True)

    if runway_length_ft:
        margin_text = f"{(runway_length_ft - ground_roll_to):+.0f} ft ({margin_pct:.0%})"
        if margin_pct >= 0.5:
            st.success(f"Runway adequate – {margin_text}")
        elif margin_pct >= 0.25:
            st.warning(f"Tight margin – {margin_text}")
        else:
            st.error(f"Insufficient – {margin_text}")

# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
st.set_page_config(page_title="AgPilot", layout="wide")
st.title("AgPilot – Aerial Application Performance Tool")
st.caption("Prototype – educational use. Always refer to official POH.")

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

# Aircraft Selection + Empty Weight Button
col1, col2 = st.columns([5, 1])
with col1:
    selected_aircraft = st.selectbox("Select Aircraft", list(AIRCRAFT_DATA.keys()),
                                     format_func=lambda x: f"{AIRCRAFT_DATA[x]['name']} – {AIRCRAFT_DATA[x]['description']}")
with col2:
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

# Inputs
col_left, col_right = st.columns(2)
with col_left:
    pressure_alt_ft = st.number_input("Pressure Altitude (ft)", 0, 20000, 0, 100)
    oat_c = st.number_input("OAT (°C)", -30, 50, 15, 1)
    weight_lbs = st.number_input("Gross Weight (lbs)", 1000, data["max_takeoff_weight_lbs"], data["max_takeoff_weight_lbs"], 50)
    wind_kts = st.number_input("Headwind (+) / Tailwind (-) (kts)", -20, 20, 0, 1)

with col_right:
    fuel_gal = st.number_input("Fuel (gal)", 0, data["base_fuel_capacity_gal"], data["base_fuel_capacity_gal"] // 2, 10)
    hopper_gal = st.number_input("Hopper Load (gal)", 0, data["hopper_capacity_gal"], 0, 10)
    pilot_weight_lbs = st.number_input("Pilot Weight (lbs)", 100, 300, 200, 10)
    runway_condition = st.selectbox("Runway Condition", list(RUNWAY_CONDITIONS.keys()))
    runway_length_ft = st.number_input("Available Runway (ft)", 1000, 8000, 3000, 100)
    carb_heat = st.checkbox("Carb Heat ON (R44 only – reduces ceiling)", value=False) if "R44" in selected_aircraft else False

if st.button("Calculate Performance", type="primary"):
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)

    if "R44" in selected_aircraft:
        ige_ceiling = compute_ige_hover_ceiling(da_ft, weight_lbs, carb_heat)
        st.subheader("R44 Raven II IGE Hover Performance")
        st.metric("IGE Hover Ceiling", f"{ige_ceiling:.0f} ft")
        if ige_ceiling < 1000:
            st.error("Marginal/no IGE hover – reduce weight or DA.")
        elif da_ft > 9600:
            st.warning("DA > substantiated limit – hover unreliable in wind.")
        # Plot
        das = np.linspace(0, 14000, 60)
        ceilings = [compute_ige_hover_ceiling(da, weight_lbs, carb_heat) for da in das]
        fig, ax = plt.subplots()
        ax.plot(das, ceilings, color="green")
        ax.axvline(da_ft, color="red", linestyle="--")
        ax.set_xlabel("Density Altitude (ft)")
        ax.set_ylabel("IGE Ceiling (ft)")
        st.pyplot(fig)
        st.info("Vertical ops – no ground roll.")
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

    show_risk_assessment(da_ft, weight_lbs, wind_kts, gr_to if 'gr_to' in locals() else 0,
                         runway_length_ft, runway_condition, selected_aircraft,
                         ige_ceiling if 'ige_ceiling' in locals() else None)

st.markdown("---")
st.caption("Prototype – use official POH. Feedback welcome!")
