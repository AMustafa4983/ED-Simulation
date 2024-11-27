
from datetime import datetime, timedelta
import time
from utils.utils import generate_random_between_two

class ExitRoom:
    def __init__(self):
        self.treated_patients = []
        self.treated_patients_reports = []

    def getTreatedPatients(self):
        return self.treated_patients
    
    def getTreatedPatientsReports(self):
        return self.treated_patients_reports
    
    def calculateWaitingTime(self, patientObject):
        waiting_time_delta = patientObject.getCheckpoint()['Under Treatment'] - patientObject.getCheckpoint()['Waiting']
        waiting_time = waiting_time_delta.total_seconds()
        return waiting_time
    
    def calculateTreatmentTime(self, patientObject):
        treatment_time_delta = patientObject.getCheckpoint()['Exit'] - patientObject.getCheckpoint()['Under Treatment']
        treatment_time = treatment_time_delta.total_seconds()
        return treatment_time
        
    def calculateTotalTime(self, patientObject):
        total_time_delta = (patientObject.getCheckpoint()['Exit'] - patientObject.getCheckpoint()['Arrival'])
        total_time = total_time_delta.total_seconds()
        return total_time
        
    def releasePatient(self, patientObject): 
        self.treated_patients.append(patientObject)
        patientObject.setStatus("Exit")
        patientObject.setCheckpoint(datetime.now())
        
        waiting_time = self.calculateWaitingTime(patientObject)
        treatment_time = self.calculateTreatmentTime(patientObject)
        total_time = self.calculateTotalTime(patientObject)

        self.treated_patients_reports.append(
            {
                'patient_id': patientObject.getID(),
                'priority_level': patientObject.getPriorityLevel(),
                'triage_category': patientObject.getTriageCategory(),
                'waiting_time': waiting_time,
                'treatment_time': treatment_time,
                'total_time': total_time,
            }
        )
        return f"Patient {patientObject.getID()} exit the department"