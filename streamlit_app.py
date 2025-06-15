import streamlit as st
import pandas as pd
from datetime import datetime
import math
from db_utils import (
    log_entry,
    log_exit,
    get_active_swimmers,
    get_today_logs,
)

st.set_page_config(page_title="🏊 Swimming Pool Tracker", layout="centered")
st.title("🏊 Swimming Pool Entry Tracker")

st.markdown("### Log Entry/Exit")
action = st.radio("Select Action", ["Entry", "Exit"], horizontal=True)
name_input = st.text_input(f"Enter swimmer's name to log {action.lower()}")

if st.button(f"Submit {action}"):
    if name_input.strip():
        if action == "Entry":
            log_entry(name_input.strip())
            st.success(f"✅ Entry logged for {name_input}")
        else:
            result = log_exit(name_input.strip())
            if result:
                st.success(f"✅ Exit logged for {name_input}")
            else:
                st.warning(f"⚠️ {name_input} has no active entry!")
    else:
        st.warning("⚠️ Please enter a valid name.")

# 🟢 Active Swimmers
st.subheader("🟢 Active Swimmers")
active_swimmers = get_active_swimmers()
if active_swimmers:
    data = []
    for name, entry_time in active_swimmers:
        entry_dt = datetime.fromisoformat(entry_time)
        now = datetime.now()
        total_minutes = int((now - entry_dt).total_seconds() / 60)

        if total_minutes >= 60:
            hours = total_minutes // 60
            extra_minutes = total_minutes % 60
            duration_str = f"{hours} hr" + (f" + {extra_minutes} min" if extra_minutes else "")
            extended_str = f"{total_minutes - 60} min"
        else:
            duration_str = f"{total_minutes} min"
            extended_str = "0 min"

        formatted_time = entry_dt.strftime("%I:%M %p")
        data.append([
            name,
            formatted_time,
            duration_str,
            extended_str
        ])

    df_active = pd.DataFrame(data, columns=["Name", "Entry Time", "Duration", "Extended Time"])
    st.dataframe(df_active, use_container_width=True)
else:
    st.info("No active swimmers currently.")

# 📋 Today's Logs
st.subheader("📋 Today's Logs")
today_logs = get_today_logs()
if today_logs:
    df_today = pd.DataFrame(today_logs, columns=["Name", "Entry Time", "Exit Time", "Duration (hrs)", "Charge (₹)"])
    df_today["Entry Time"] = pd.to_datetime(df_today["Entry Time"]).dt.strftime("%I:%M %p")
    df_today["Exit Time"] = pd.to_datetime(df_today["Exit Time"]).dt.strftime("%I:%M %p")

    charges = []
    formatted_durations = []
    extended_times = []

    for dur in df_today["Duration (hrs)"]:
        total_minutes = int(dur * 60)
        hrs = total_minutes // 60
        mins = total_minutes % 60
        formatted_durations.append(f"{hrs} hr {mins} min")

        if total_minutes <= 60:
            charge = 100
            extended = "0 min"
        else:
            extra_minutes = total_minutes - 60
            if extra_minutes <= 5:
                charge = 100
            else:
                charge = 100 + (math.ceil(extra_minutes / 60) * 100)
            extended = f":red[{extra_minutes} min]" if extra_minutes > 0 else "0 min"

        charges.append(charge)
        extended_times.append(extended)

    df_today["Duration"] = formatted_durations
    df_today["Extended Time"] = extended_times
    df_today["Charge (₹)"] = charges
    df_today = df_today[["Name", "Entry Time", "Exit Time", "Duration", "Extended Time", "Charge (₹)"]]

    st.dataframe(df_today, use_container_width=True)
    st.success(f"👥 Swimmers Today: {len(df_today)} | 💰 Revenue: ₹{sum(charges)}")

    if st.button("💾 Save as CSV"):
        file_name = f"logs_{datetime.now().strftime('%Y-%m-%d')}.csv"
        df_today.to_csv(file_name, index=False)
        st.success(f"✅ Saved today's log to `{file_name}`")
else:
    st.warning("No completed logs today.")
