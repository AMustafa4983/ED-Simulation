import time
from EnvironmentElements.Bed import Bed
from datetime import datetime, timedelta
from utils.utils import generate_random_between_two

class TreatmentRoom:
    def __init__(self, capacity):
        self.patients = {}
        self.capacity = capacity
        beds = [Bed() for _ in range(capacity)]
        self.beds = {bed.getID(): bed for bed in beds}
        self.transition_log = []
        return None
    
    def getBeds(self):
        return self.beds
    
    def isBedAvailable(self):
        flag = False
        bed_id = None
        for bed in self.beds.values():
            if not bed.occupied:
                flag = True
                bed_id = bed.getID()
                break
        return flag, bed_id
    
    def getCapacity(self):
        return self.capacity

    def registerPatient(self, patientObject):
        flag, bed_id = self.isBedAvailable()
        if flag:
            self.patients[patientObject.getID()] = patientObject
            patientObject.setStatus("Under Treatment")
            patientObject.setCheckpoint(datetime.now())
            
            self.transition_log.append({
                "Patient ID": patientObject.getID(),
                "From Room": "None",
                "To Room": self.__class__.__name__,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Action": "Entered"
            })
                            
            bed = self.beds[bed_id]
            bed.setPatientAssiend(patientObject.getID())
            bed.setReleaseTime(self.calculateTreatmentDuration(patientObject))
            bed.setOccupiedStatus(True)
            return f"Patient {patientObject.getID()} under treatment"
        else:
            return "No Beds Availabe!"
    
    def calculateTreatmentDuration(self, patientObject):
        category = patientObject.getTriageCategory()
        if category == "Level 1: Resuscitation (Critical)":
            treatment_duration = generate_random_between_two(25, 29)
        elif category == "Level 2: Emergent (Very Urgent)":
            treatment_duration = generate_random_between_two(20, 24)
        elif category == "Level 3: Urgent":
            treatment_duration = generate_random_between_two(15, 19)
        elif category == "Level 4: Less Urgent":
            treatment_duration = generate_random_between_two(10, 14)
        elif category == "Level 5: Non-Urgent":
            treatment_duration = generate_random_between_two(5, 9)
        
        return datetime.now() + timedelta(seconds=treatment_duration)
    
    def checkTreatmentProcess(self):
        beds = self.beds.values()
        patients_to_release = []
        for bed in beds:
            if bed.getOccupiedStatus():
                if datetime.now() >= bed.getReleaseTime():
                    patientAssigned = bed.getPatientAssigned()
                    bed.releasePatient()
                    patients_to_release.append(self.patients[patientAssigned])
                    self.patients.pop(patientAssigned, None)
                else:
                    continue

        return patients_to_release
    
    def sendToExitRoom(self, exitRoomObject):
        patienrs_to_release = self.checkTreatmentProcess()

        if patienrs_to_release:
            for patient in patienrs_to_release:
                exitRoomObject.releasePatient(patient)

                # Log the transition
                self.transition_log.append({
                    "Patient ID": patient.getID(),
                    "From Room": self.__class__.__name__,
                    "To Room": exitRoomObject.__class__.__name__,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Action": "Moved"
                })
        return None
    
    def getTransitions(self):
        # Return and clear the transition log for this room
        log = self.transition_log[:]
        self.transition_log.clear()
        return log