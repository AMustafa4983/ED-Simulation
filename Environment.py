import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from Rooms.ArrivalRoom import ArrivalRoom
from Rooms.WaitingRoom import WaitingRoom
from EnvironmentElements.Patient import Patient
from Rooms.TreatmentRoom import TreatmentRoom
from Rooms.ExitRoom import ExitRoom
import altair as alt
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

# Placeholders for dynamic updates
status_placeholder = st.empty()
reports_placeholder = st.empty()
chart_placeholder = st.empty()
triage_chart_placeholder = st.empty()

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

        # Step 2: Move patients from arrival to waiting room
        arrival_room.sendToWaitingRoom(waiting_room)

        # Step 3: Move patients from waiting room to treatment room
        waiting_room.sendToTreatmentRoom(treatment_room)

        # Step 4: Treat patients and move them to the exit room
        treatment_room.sendToExitRoom(exit_room)

        # Update dynamic placeholders
        with status_placeholder.container():
            st.subheader("Current Simulation Status")
            st.write("Time:", current_time.strftime("%H:%M:%S"))
            st.write("Patients in Arrival Room:", len(arrival_room.getQueue()))
            st.write("Patients in Waiting Room:", len(waiting_room.getQueue()))
            st.write("Patients in Treatment Room:", len(treatment_room.patients))
            st.write("Treated Patients in Exit Room:", len(exit_room.getTreatedPatients()))

        # Get and display patient reports
        patient_reports = exit_room.getTreatedPatientsReports()

        if patient_reports:
            with reports_placeholder.container():
                st.subheader("Patient Reports (Treated Patients Only)")
                st.json(patient_reports)

            # Convert to DataFrame for visualization
            df = pd.DataFrame(patient_reports)

            if not df.empty:
                # Interactive Patient Times Overview
                with chart_placeholder.container():
                    st.subheader("Patient Summary Overview (Treated Patients Only)")

                    # Melt data for Altair chart
                    chart_data = pd.melt(
                        df, id_vars=['patient_id'], 
                        value_vars=['waiting_time', 'treatment_time', 'total_time'], 
                        var_name='Metric', value_name='Time'
                    )

                    # Create Altair line chart for time metrics
                    time_chart = alt.Chart(chart_data).mark_line().encode(
                        x=alt.X('patient_id:N', title="Patient ID"),
                        y=alt.Y('Time:Q', title="Time (minutes)"),
                        color='Metric:N',
                        tooltip=['patient_id', 'Metric', 'Time']
                    ).properties(
                        width=700,
                        height=400,
                        title="Patient Times Overview"
                    )

                    st.altair_chart(time_chart, use_container_width=True)


                # Triage Level Report
                triage_data = pd.DataFrame({
                    'Patient ID': [p.getID() for p in patients],
                    'Triage Category': [p.getTriageCategory() for p in patients]
                })

                triage_summary = triage_data['Triage Category'].value_counts().reset_index()
                triage_summary.columns = ['Triage Category', 'Count']

                with triage_chart_placeholder.container():
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


        # Pause for visualization
        time.sleep(1)

    st.success("Simulation Finished Successfully")
    # Add a table for detailed patient triage information
    st.subheader("Detailed Patient Triage Information")
    st.dataframe(triage_data)

    st.subheader("Patient Summary Reports (Treated Patients Only)")
    st.dataframe(df)
