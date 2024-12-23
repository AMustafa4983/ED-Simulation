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
last_escalation_time = simulation_start_time

placeholder = st.empty()
cumulative_transitions = []  # Store cumulative transitions over time
cumulative_time = []
room_viscosity = {"Waiting Room": [], "Treatment Room": []}


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
            patient.setEntryTime(current_time)  # Set entry time when patient enters the room
            patients.append(patient)
            last_patient_arrival_time = current_time

        # Step 2: Move patients between rooms
        arrival_room.sendToWaitingRoom(waiting_room)
        
        # Escalate every 5 seconds
        if (current_time - last_escalation_time).total_seconds() >= 5:
            queue = waiting_room.getQueue()
            if queue:
                for patient in queue:
                    waiting_room.escalate(patient)
                    patient.setExitTime(current_time)  # Set exit time when patient leaves the room
                    room_viscosity["Waiting Room"].append(
                        (patient.getExitTime() - patient.getEntryTime()).total_seconds() / 60  # Residence time in minutes
                    )
                last_escalation_time = current_time
        
        waiting_room.sendToTreatmentRoom(treatment_room)
        treatment_room.sendToExitRoom(exit_room)


        # Waiting Room
        for patient in waiting_room.getQueue():
            if patient.getExitTime() and patient.getEntryTime():
                time_in_room = (patient.getExitTime() - patient.getEntryTime()).total_seconds()# in minutes
                room_viscosity["Waiting Room"].append(time_in_room)

        # Treatment Room
        for patient in treatment_room.patients.values():
            if patient.getExitTime() and patient.getEntryTime():
                time_in_room = (patient.getExitTime() - patient.getEntryTime()).total_seconds()# in minutes
                room_viscosity["Treatment Room"].append(time_in_room)


        # Collect transitions from all rooms
        all_transitions = []
        all_transitions.extend(arrival_room.getTransitions())
        all_transitions.extend(waiting_room.getTransitions())
        all_transitions.extend(treatment_room.getTransitions())
        all_transitions.extend(exit_room.getTransitions())


        # Calculate the flow (transitions per second)
        elapsed_time = (current_time - simulation_start_time).total_seconds()
        flow_rate = len(all_transitions) / elapsed_time if elapsed_time > 0 else 0

        # Update cumulative data
        cumulative_transitions.append(len(all_transitions))
        cumulative_time.append(elapsed_time / 60)  # Convert to minutes

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
                st.plotly_chart(fig, use_container_width=True, key=f"Patient_Room_{current_time.timestamp()}")
                
                # Plot cumulative flow
                if len(cumulative_transitions) > 1:
                    flow_data = pd.DataFrame({
                        "Time (minutes)": cumulative_time,
                        "Cumulative Transitions": cumulative_transitions
                    })

                    flow_fig = px.line(
                        flow_data,
                        x="Time (minutes)",
                        y="Cumulative Transitions",
                        title="Cumulative Flow Over Time",
                        labels={"Time (minutes)": "Time (minutes)", "Cumulative Transitions": "Transitions"}
                    )
                    st.plotly_chart(flow_fig, use_container_width=True, key=f"patient_flow_{current_time.timestamp()}")

                # Plot viscosity for each room
                viscosity_data = pd.DataFrame({
                    "Room": list(room_viscosity.keys()),
                    "Average Viscosity (minutes)": [sum(times) / len(times) if times else 0 for times in room_viscosity.values()]
                })

                viscosity_fig = px.bar(
                    viscosity_data,
                    x="Room",
                    y="Average Viscosity (minutes)",
                    title="Average Viscosity (Time Spent) per Room",
                    labels={"Average Viscosity (minutes)": "Average Time Spent (Seconds)"},
                    text="Average Viscosity (minutes)"
                )
                st.plotly_chart(viscosity_fig, use_container_width=True, key=f"viscosity_room_{current_time.timestamp()}")

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
                st.plotly_chart(fig3, use_container_width=True, key=f"Bed_Status_{current_time.timestamp()}")

            # Tab 3: Patient Reports
            with tab3:
                patient_reports = exit_room.getTreatedPatientsReports()
                if patient_reports:
                    df = pd.DataFrame(patient_reports)
                    if not df.empty:
                        st.subheader("Patient Summary Overview")
                        
                        # Time chart
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

                        with st.expander("View Detailed Reports"):
                            st.dataframe(df)

    st.success("Simulation Finished Successfully")
