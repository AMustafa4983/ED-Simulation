import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
from Rooms.ArrivalRoom import ArrivalRoom
from Rooms.WaitingRoom import WaitingRoom
from EnvironmentElements.Patient import Patient
from Rooms.TreatmentRoom import TreatmentRoom
from Rooms.ExitRoom import ExitRoom
import time

# Streamlit Page Configuration
st.set_page_config(page_title="Patient Flow Simulation", layout="wide")

# Sidebar for User Inputs
st.sidebar.title("Simulation Configuration")
arrival_rate = st.sidebar.slider("Arrival Rate (patients per minute)", min_value=1, max_value=60, value=10, step=1)
simulation_duration_minutes = st.sidebar.slider("Simulation Duration (minutes)", min_value=1, max_value=120, value=2, step=1)
waiting_room_capacity = st.sidebar.slider("Waiting Room Capacity", min_value=1, max_value=20, value=6, step=1)
treatment_room_capacity = st.sidebar.slider("Treatment Room Capacity", min_value=1, max_value=10, value=2, step=1)

# Initialize simulation components
arrival_room = ArrivalRoom()
waiting_room = WaitingRoom(waiting_room_capacity)
treatment_room = TreatmentRoom(treatment_room_capacity)
exit_room = ExitRoom()

# Simulation timing setup
time_between_patients_arrival = 1 / arrival_rate * 60  # Time in seconds
simulation_start_time = datetime.now()
end_time = simulation_start_time + timedelta(minutes=simulation_duration_minutes)
last_patient_arrival_time = simulation_start_time

placeholder = st.empty()
# UI to Start Simulation
if st.sidebar.button("Start Simulation"):
    patients = []
    current_time = simulation_start_time        

    while current_time <= end_time:
        current_time = datetime.now()
        
        # Step 1: Register a new patient in the arrival room
        if (current_time - last_patient_arrival_time).total_seconds() >= time_between_patients_arrival:
            patient = Patient()
            arrival_room.registerPatient(patient)
            patients.append(patient)
            last_patient_arrival_time = current_time

        # Step 2: Move patients between rooms
        arrival_room.sendToWaitingRoom(waiting_room)
        waiting_room.sendToTreatmentRoom(treatment_room)
        treatment_room.sendToExitRoom(exit_room)

        # Collect patient counts
        arrival_room_count = len(arrival_room.getQueue())
        waiting_room_count = len(waiting_room.getQueue())
        treatment_room_count = len(treatment_room.patients)
        exit_room_count = len(exit_room.getTreatedPatients())

        # Prepare data for visualization
        room_names = ["Arrival Room", "Waiting Room", "Treatment Room", "Exit Room"]
        patient_counts = [
            arrival_room_count,
            waiting_room_count,
            treatment_room_count,
            exit_room_count,
        ]
        
        with placeholder:

            # Tabs for organized display
            tab1, tab2, tab3 = st.tabs(["Room Overview", "Density and Beds Status", "Patient Reports"])
            
            # Tab 1: Room Overview
            with tab1:
                fig = px.bar(
                    x=room_names,
                    y=patient_counts,
                    labels={"x": "Room", "y": "Number of Patients"},
                    title="Patients in Each Room",
                    text=patient_counts,
                )
                # Add unique key using the timestamp
                st.plotly_chart(fig, use_container_width=True, key=f"Patient_Room_{current_time.timestamp()}")

            # Tab 2: Density and Beds Status
            with tab2:
                densities = [
                    round(arrival_room_count + waiting_room_count / waiting_room_capacity, 2),
                    round(
                        arrival_room_count
                        + waiting_room_count
                        + treatment_room_count / treatment_room_capacity,
                        2,
                    ),
                ]
                fig2 = px.bar(
                    x=["Waiting Room", "Treatment Room"],
                    y=densities,
                    labels={"x": "Room", "y": "Density"},
                    title="Density per Room",
                    text=densities,
                )
                # Add unique key using the timestamp
                st.plotly_chart(fig2, use_container_width=True, key=f"Density_{current_time.timestamp()}")

                # Beds status
                beds = treatment_room.getBeds()
                release_times = []
                bed_names = []
                colors = []
                for bed_id, bed_obj in beds.items():
                    bed_names.append(f"Bed {bed_id}")
                    if bed_obj.getOccupiedStatus():
                        remaining_time = bed_obj.getReleaseTime() - current_time
                        release_times.append(remaining_time.total_seconds())
                        colors.append(
                            "red" if remaining_time.total_seconds() < 3600 else
                            "yellow" if remaining_time.total_seconds() < 10800 else
                            "green"
                        )
                    else:
                        release_times.append(0)
                        colors.append("gray")

                data = pd.DataFrame({
                    "Beds": bed_names,
                    "Remaining Time (Seconds)": release_times,
                    "Remaining Time (HH:MM:SS)": [
                        str(timedelta(seconds=rt)) if rt > 0 else "0:00:00" for rt in release_times
                    ],
                    "Color": colors
                })

                fig3 = px.bar(
                    data,
                    x="Beds",
                    y="Remaining Time (Seconds)",
                    text="Remaining Time (HH:MM:SS)",
                    color="Color",
                    labels={"Remaining Time (Seconds)": "Remaining Time to Release (Seconds)"},
                    title=f"Beds Status (as of {current_time.strftime('%H:%M:%S')})",
                    color_discrete_map={"red": "red", "yellow": "yellow", "green": "green", "gray": "gray"},
                )
                # Add unique key using the timestamp
                st.plotly_chart(fig3, use_container_width=True, key=f"Bed_Status_{current_time.timestamp()}")


            # Tab 3: Patient Reports
            with tab3:
                patient_reports = exit_room.getTreatedPatientsReports()
                if patient_reports:
                    df = pd.DataFrame(patient_reports)
                    if not df.empty:
                        st.subheader("Patient Summary Overview")
                        
                        # Time chart (already existing code)
                        chart_data = pd.melt(
                            df, id_vars=["patient_id"],
                            value_vars=["waiting_time", "treatment_time", "total_time"],
                            var_name="Metric", value_name="Time"
                        )
                        time_chart = alt.Chart(chart_data).mark_line().encode(
                            x=alt.X("patient_id:N", title="Patient ID"),
                            y=alt.Y("Time:Q", title="Time (minutes)"),
                            color="Metric:N",
                            tooltip=["patient_id", "Metric", "Time"]
                        ).properties(width=700, height=400)
                        st.altair_chart(time_chart, use_container_width=True)

                        # Triage Level Report
                        triage_data = pd.DataFrame({
                            'Patient ID': [p.getID() for p in patients],
                            'Triage Category': [p.getTriageCategory() for p in patients]
                        })

                        triage_summary = triage_data['Triage Category'].value_counts().reset_index()
                        triage_summary.columns = ['Triage Category', 'Count']

                        st.subheader("Triage Level Distribution")

                        # Create Altair bar chart for triage levels
                        triage_chart = alt.Chart(triage_summary).mark_bar().encode(
                            x=alt.X('Triage Category:N', title="Triage Level"),
                            y=alt.Y('Count:Q', title="Number of Patients"),
                            color=alt.Color('Triage Category:N', legend=None),
                            tooltip=['Triage Category', 'Count']
                        ).properties(
                            width=700,
                            height=400,
                            title="Triage Level Distribution"
                        )

                        st.altair_chart(triage_chart, use_container_width=True)


                        # Detailed Reports
                        with st.expander("View Detailed Reports"):
                            st.dataframe(df)

                        
    st.success("Simulation Finished Successfully")
