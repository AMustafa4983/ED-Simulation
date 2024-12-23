import time
from datetime import datetime, timedelta
from utils.utils import sort_by_priority, generate_random_between_two

class WaitingRoom:
    def __init__(self, capacity):
        self.queue = []
        self.capacity = capacity
        self.transition_log = []
        return None
    
    def getQueue(self):
        return self.queue
    
    def setQueue(self, new_queue):
        self.queue = new_queue
    
    def checkCapacity(self):
        return len(self.queue) < self.capacity
    
    def registerPatient(self, patientObject):
        if len(self.queue) < self.capacity: 
            self.queue.append(patientObject)
            
            self.setQueue(sort_by_priority(self.getQueue()))
        
            self.transition_log.append({
                "Patient ID": patientObject.getID(),
                "From Room": "None",
                "To Room": self.__class__.__name__,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Action": "Entered"
            })
        
            patientObject.setStatus("Waiting")
            patientObject.setCheckpoint(datetime.now())
            
            return f"Patient {patientObject.getID()} waiting"

    def escalate(self, patientObject):
        priority_level = patientObject.getPriorityLevel()

        if priority_level == "Very Low":
            priority_level = "Low"
        
        elif priority_level == "Low":
            priority_level = "Medium"
        
        elif priority_level == "Medium":
            priority_level = "High"
        
        elif priority_level == "High":
            priority_level = "Very High"
        
        else:
            return "Patient Priority Already Very High!"
    
        patientObject.setPriorityLevel(priority_level)
    
    def sendToTreatmentRoom(self, treatmentRoomObject):
        flag, bed_id = treatmentRoomObject.isBedAvailable()

        if flag:
            if self.queue != []:
                patient = self.queue.pop(0)
                treatmentRoomObject.registerPatient(patient)

                # Log the transition
                self.transition_log.append({
                    "Patient ID": patient.getID(),
                    "From Room": self.__class__.__name__,
                    "To Room": treatmentRoomObject.__class__.__name__,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Action": "Moved"
                })
            else:
                return "No More Patients in Waiting Room!"
            return f"Patient {patient.getID()} assigned to bed {bed_id}"
        else:
            return f"No Bed Available!"
        
    def getTransitions(self):
        # Return and clear the transition log for this room
        log = self.transition_log[:]
        self.transition_log.clear()
        return log