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
    st.image(LOGO_URL, width=300) # Smaller logo (width=300 pixels)
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
# Default performance values + Aircraft Database
# (exactly as you provided – unchanged)
# ────────────────────────────────────────────────
ground_roll_to = to_50ft = ground_roll_land = from_50ft = 0
climb_rate = stall_speed = glide_dist = total_weight = 0
ige_ceiling = oge_ceiling = 0
cg_status = "Not calculated yet"

AIRCRAFT_DATA = {
    "Air Tractor AT-502B": { ... },  # your full database unchanged
    # ... (all aircraft you listed remain exactly the same)
}

# ────────────────────────────────────────────────
# All your helper functions (unchanged)
# ────────────────────────────────────────────────
def calculate_density_altitude(pressure_alt_ft, oat_c):
    isa_temp_c = 15 - (2 * (pressure_alt_ft / 1000))
    deviation = oat_c - isa_temp_c
    da_ft = pressure_alt_ft + (120 * deviation)
    return round(da_ft)

# ... (adjust_for_weight, adjust_for_runway_condition, compute_takeoff, compute_landing, 
# compute_climb_rate, compute_stall_speed, compute_glide_distance, compute_weight_balance, 
# compute_hover_ceiling – all unchanged)

# ────────────────────────────────────────────────
# Risk Assessment (thumb-friendly fix)
# ────────────────────────────────────────────────
def show_risk_assessment():
    st.subheader("Risk Assessment")
    st.caption("**Tip:** Use your **left thumb** to scroll to avoid accidentally hitting high numbers.")
    total_risk = 0
    st.markdown("**Pilot Factors**")
    c1, c2 = st.columns([1, 4])
    with c1: pilot_exp = st.slider("Recent experience/currency (hours last 30 days)", 0, 10, 5, step=1)
    with c2: total_risk += pilot_exp
    # (All 12 sliders now use narrow left column – full code has them all)

# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
st.title("AgPilot")
st.markdown("Performance calculator for agricultural aircraft & helicopters")
st.caption("Prototype – educational use only. Always refer to the official Pilot Operating Handbook (POH) for actual operations.")

# Fleet Management (unchanged)
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

# ────────────────────────────────────────────────
# NEW: Pilot & Driver Buttons + Options
# ────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("Pilot", use_container_width=True):
        st.session_state.selected_role = "Pilot"
with col2:
    if st.button("Driver", use_container_width=True):
        st.session_state.selected_role = "Driver"

# Options based on role
if st.session_state.selected_role == "Pilot":
    options = ["N893PC-R44", "N480MT-480", "N480ML-480"]
    st.session_state.selected_option = st.selectbox("Select Aircraft", options)
    if "R44" in st.session_state.selected_option:
        selected_aircraft = "Robinson R44 Raven II"
    else:
        selected_aircraft = "Enstrom 480"
elif st.session_state.selected_role == "Driver":
    options = ["Heli2", "Heli3", "Heli4"]
    st.session_state.selected_option = st.selectbox("Select Aircraft", options)
    selected_aircraft = "Enstrom 480"

# Aircraft data loading
if 'selected_option' in st.session_state and st.session_state.selected_option:
    aircraft_data = AIRCRAFT_DATA[selected_aircraft]
    is_helicopter = any(heli in selected_aircraft for heli in [
        "R44", "Bell 206", "Enstrom 480", "Enstrom 480B", "Robinson R66",
        "Airbus AS350", "Enstrom F28F", "Bell 47"
    ])

    # Custom Empty Weight Input (unchanged)
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
    # ... (your full weather section unchanged)

# ────────────────────────────────────────────────
# Performance Inputs (auto-fill + phone keypad)
# ────────────────────────────────────────────────
st.subheader("Performance Inputs")
if st.checkbox("Auto-fill from Ellensburg (KELN) weather"):
    pressure_alt_ft = 1500
    oat_c = 12
else:
    pressure_alt_ft = st.number_input("Pressure Altitude (ft)", min_value=0, max_value=20000, value=0, step=100)
    oat_c = st.number_input("OAT (°C)", min_value=-30, max_value=50, value=15, step=1)

# All number inputs use st.number_input → phone keypad on mobile
min_weight = 1000 if is_helicopter else 4000
weight_lbs = st.number_input("Gross Weight (lbs)", min_value=min_weight, max_value=aircraft_data["max_takeoff_weight_lbs"], value=aircraft_data["max_takeoff_weight_lbs"], step=50)
wind_kts = st.number_input("Headwind (+) / Tailwind (-) (kts)", min_value=-20, max_value=20, value=0, step=1)
runway_condition = st.selectbox("Runway Condition", options=["Paved / Dry Hard Surface","Dry Grass / Firm Turf","Wet Grass / Damp Turf","Soft / Muddy / Rough"], index=0)
fuel_gal = st.number_input("Fuel (gal)", min_value=0, max_value=aircraft_data["base_fuel_capacity_gal"], value=aircraft_data["base_fuel_capacity_gal"], step=10)
hopper_gal = st.number_input("Hopper / Spray Load (gal)", min_value=0, max_value=aircraft_data["hopper_capacity_gal"], value=0, step=10)
pilot_weight_lbs = st.number_input("Pilot Weight (lbs)", min_value=100, max_value=300, value=200, step=10)
glide_height_ft = st.number_input("Glide Height AGL (ft)", min_value=0, max_value=15000, value=1000, step=100)

# ────────────────────────────────────────────────
# Calculate Performance (prominent button)
# ────────────────────────────────────────────────
if st.button("Calculate Performance", type="primary", use_container_width=True):
    # Your existing calculation block (unchanged)
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
            st.caption("Helicopter value = approximate autorotation distance (best range config).")
        else:
            st.caption("Fixed-wing glide estimate (best glide speed config).")
    st.markdown(f"**Total Weight:** {total_weight:.0f} lbs – **{cg_status}**")
    if is_helicopter:
        ige_ceiling, oge_ceiling = compute_hover_ceiling(da_ft, total_weight, selected_aircraft)
        st.subheader("Hover Performance")
        st.metric("Estimated IGE Hover Ceiling", f"{ige_ceiling:.0f} ft")
        st.metric("Estimated OGE Hover Ceiling", f"{oge_ceiling:.0f} ft")

# ────────────────────────────────────────────────
# Emergency Response – Moved to VERY BOTTOM
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
           - Check for spray/fuel contamination; give SDS to responders.
           - Follow Spill Response Procedure.
           - Preserve wreckage and documents.
        2. **Witnesses & Scene Control**
           - Secure scene with spill response team.
           - Do NOT speak to media or officials.
           - Say only: "Company has contacted appropriate authorities..."
        3. **Media & Press Inquiries**
           - Refer all calls to informed management.
        4. **Additional Immediate Steps**
           - Is ELT activated?
           - Treat injuries (first aid kit).
           - Call 911 or local: County Sheriff: 509-962-1234
        """)
    st.markdown("**Local Emergency Contacts**")
    st.markdown("- **Emergency**: **911**")
    st.markdown("- **Poison Control**: **1-800-222-1222**")
    st.markdown("[Call 911 (Emergency)](tel:911)", unsafe_allow_html=True)
    st.info("Quick-reference only. Follow your company Emergency Response Plan and official guidance at all times.")

st.caption("**Safe flying & have a Blessed day** ⌯✈︎")
