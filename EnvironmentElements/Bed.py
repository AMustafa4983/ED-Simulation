from utils.utils import generate_id

class Bed:
    def __init__(self):
        self.bed_id = generate_id(6)
        self.occupied = False
        self.patient_assigned = None
        self.release_time = None
        return None
    
    def getID(self):
        return self.bed_id
    
    def getOccupiedStatus(self):
        return self.occupied
    
    def setOccupiedStatus(self, new_status):
        self.occupied = new_status
    
    def  getPatientAssigned(self):
        return self.patient_assigned
    
    def setPatientAssiend(self, new_patient_assigned):
        self.patient_assigned = new_patient_assigned

    def getReleaseTime(self):
        return self.release_time
    
    def setReleaseTime(self, new_release_time):
        self.release_time = new_release_time
    
    def releasePatient(self):
        self.setOccupiedStatus(False)
        self.setPatientAssiend(None)
        self.setReleaseTime(None)