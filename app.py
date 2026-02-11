import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ────────────────────────────────────────────────
# Aircraft Database
# AT-502B is first (default), AT-802 added third
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
        "base_takeoff_ground_roll_ft": 1800,      # approximate – higher due to larger size/weight
        "base_takeoff_to_50ft_ft": 3400,
        "base_landing_ground_roll_ft": 1100,
        "base_landing_to_50ft_ft": 2200,
        "base_climb_rate_fpm": 1050,
        "base_stall_flaps_down_mph": 78,
        "best_climb_speed_mph": 120,
        "base_empty_weight_lbs": 6750,
        "base_fuel_capacity_gal": 380,
        "fuel_weight_per_gal": 6.7,               # Jet-A / turbine fuel is slightly heavier
        "hopper_capacity_gal": 800,
        "hopper_weight_per_gal": 8.0,
        "max_takeoff_weight_lbs": 16000,
        "max_landing_weight_lbs": 14000,
        "glide_ratio": 7.0,
        "description": "Large turbine ag aircraft – high payload & range"
    },
    # Add more aircraft here as needed
}

# ────────────────────────────────────────────────
# Helper Functions (unchanged – they pull from selected aircraft)
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

@st.cache_data
def compute_takeoff(pressure_alt_ft, oat_c, weight_lbs, wind_kts, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    ground_roll = adjust_for_weight(data["base_takeoff_ground_roll_ft"], weight_lbs, data["max_takeoff_weight_lbs"])
    ground_roll = adjust_for_da(ground_roll, da_ft)
    ground_roll = adjust_for_wind(ground_roll, wind_kts)
    to_50ft = adjust_for_weight(data["base_takeoff_to_50ft_ft"], weight_lbs, data["max_takeoff_weight_lbs"])
    to_50ft = adjust_for_da(to_50ft, da_ft)
    to_50ft = adjust_for_wind(to_50ft, wind_kts)
    return ground_roll, to_50ft

@st.cache_data
def compute_landing(pressure_alt_ft, oat_c, weight_lbs, wind_kts, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    weight_lbs = min(weight_lbs, data["max_landing_weight_lbs"])
    da_ft = calculate_density_altitude(pressure_alt_ft, oat_c)
    ground_roll = adjust_for_weight(data["base_landing_ground_roll_ft"], weight_lbs, data["max_landing_weight_lbs"], exponent=1.0)
    ground_roll = adjust_for_da(ground_roll, da_ft)
    ground_roll = adjust_for_wind(ground_roll, wind_kts)
    from_50ft = adjust_for_weight(data["base_landing_to_50ft_ft"], weight_lbs, data["max_landing_weight_lbs"], exponent=1.0)
    from_50ft = adjust_for_da(from_50ft, da_ft)
    from_50ft = adjust_for_wind(from_50ft, wind_kts)
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
    ground_speed_mph = 100 + wind_kts
    glide_distance_nm = (height_ft / 6076) * data["glide_ratio"] * (ground_speed_mph / 60)
    return glide_distance_nm

@st.cache_data
def compute_weight_balance(fuel_gal, hopper_gal, pilot_weight_lbs, aircraft):
    data = AIRCRAFT_DATA[aircraft]
    fuel_weight = fuel_gal * data["fuel_weight_per_gal"]
    hopper_weight = hopper_gal * data["hopper_weight_per_gal"]
    total_weight = data["base_empty_weight_lbs"] + fuel_weight + hopper_weight + pilot_weight_lbs
    status = "Within limits" if total_weight <= data["max_takeoff_weight_lbs"] else "Overweight!"
    if total_weight > data["max_landing_weight_lbs"]:
        status += " (Exceeds max landing weight)"
    return total_weight, status

# ────────────────────────────────────────────────
# Main App – AgPilot
# ────────────────────────────────────────────────

st.set_page_config(page_title="AgPilot – Aerial Application Performance Tool", layout="wide")

st.title("AgPilot")
st.markdown("Performance calculator for agricultural aircraft")
st.caption("Prototype – educational use only. Always refer to the official Pilot Operating Handbook (POH) for actual operations.")

# Aircraft selection – AT-502B is first (default)
selected_aircraft = st.selectbox(
    "Select Aircraft",
    options=list(AIRCRAFT_DATA.keys()),
    index=0,  # 0 = first item = AT-502B
    format_func=lambda x: f"{AIRCRAFT_DATA[x]['name']} – {AIRCRAFT_DATA[x]['description']}"
)

# Show selected aircraft info
aircraft_data = AIRCRAFT_DATA[selected_aircraft]
st.info(f"Performance data loaded for **{aircraft_data['name']}**")

# Inputs – limits adjusted to selected aircraft
col1, col2 = st.columns(2)
with col1:
    pressure_alt_ft = st.number_input("Pressure Altitude (ft)", 0, 20000, 0, step=100)
    oat_c           = st.number_input("OAT (°C)", -30, 50, 15, step=1)
    weight_lbs      = st.number_input(
        "Gross Weight (lbs)",
        4000,
        aircraft_data["max_takeoff_weight_lbs"],
        aircraft_data["max_takeoff_weight_lbs"],
        step=50
    )
    wind_kts        = st.number_input("Headwind (+) / Tailwind (-) (kts)", -20, 20, 0, step=1)

with col2:
    fuel_gal         = st.number_input("Fuel (gal)", 0, aircraft_data["base_fuel_capacity_gal"], aircraft_data["base_fuel_capacity_gal"], step=10)
    hopper_gal       = st.number_input("Hopper / Load (gal)", 0, aircraft_data["hopper_capacity_gal"], 0, step=50)
    pilot_weight_lbs = st.number_input("Pilot Weight (lbs)", 100, 300, 200, step=10)
    glide_height_ft  = st.number_input("Glide Height AGL (ft)", 0, 15000, 1000, step=100)

# Calculate
if st.button("Calculate Performance", type="primary"):
    ground_roll_to, to_50ft     = compute_takeoff(pressure_alt_ft, oat_c, weight_lbs, wind_kts, selected_aircraft)
    ground_roll_land, from_50ft = compute_landing(pressure_alt_ft, oat_c, weight_lbs, wind_kts, selected_aircraft)
    climb_rate                  = compute_climb_rate(pressure_alt_ft, oat_c, weight_lbs, selected_aircraft)
    stall_speed                 = compute_stall_speed(weight_lbs, selected_aircraft)
    glide_dist                  = compute_glide_distance(glide_height_ft, wind_kts, selected_aircraft)
    total_weight, cg_status     = compute_weight_balance(fuel_gal, hopper_gal, pilot_weight_lbs, selected_aircraft)

    st.subheader("Results")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Takeoff Ground Roll", f"{ground_roll_to:.0f} ft")
        st.metric("Takeoff to 50 ft", f"{to_50ft:.0f} ft")
        st.metric("Landing Ground Roll", f"{ground_roll_land:.0f} ft")
        st.metric("Landing from 50 ft", f"{from_50ft:.0f} ft")
    with col_b:
        st.metric("Climb Rate", f"{climb_rate:.0f} fpm")
        st.metric("Best Rate Climb", f"{aircraft_data['best_climb_speed_mph']} mph IAS")
        st.metric("Stall Speed (flaps down)", f"{stall_speed:.1f} mph")
        st.metric("Glide Distance", f"{glide_dist:.1f} nm")

    st.markdown(f"**Total Weight:** {total_weight:.0f} lbs  –  **{cg_status}**")

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

# Feedback section
st.markdown("---")
st.subheader("Your Feedback – Help Improve AgPilot")

rating = st.feedback("stars")

comment = st.text_area(
    "Comments, suggestions, or issues",
    height=120,
    placeholder="Ideas? Comments? Suggestions?..."
)

if st.button("Submit Rating & Comment"):
    if rating is not None:
        stars = rating + 1
        st.success(f"Thank you! You rated **{stars} stars**.")
        if comment.strip():
            st.caption(f"Comment: {comment}")
    else:
        st.warning("Please select a star rating.")
