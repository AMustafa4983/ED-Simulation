import time
from datetime import datetime, timedelta
from utils.utils import generate_id, generate_random_between_two


class ArrivalRoom:
    def __init__(self):
        self.queue = []
        self.triage_categories = [
        "Level 1: Resuscitation (Critical)",
        "Level 2: Emergent (Very Urgent)",
        "Level 3: Urgent",
        "Level 4: Less Urgent",
        "Level 5: Non-Urgent"
    ]
        self.transition_log = []
        return None
    
    def getQueue(self):
        return self.queue

    def registerPatient(self, patientObject):
        patientObject.setID(generate_id(6))
        patientObject.setStatus("Arrival")
        patientObject.setCheckpoint(datetime.now())
        
        self.transition_log.append({
            "Patient ID": patientObject.getID(),
            "From Room": "None",
            "To Room": self.__class__.__name__,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Action": "Entered"
        })

        self.assignTriage(patientObject)
        self.assignPriority(patientObject)

        self.queue.append(patientObject)
        return f"Patient {patientObject.getID()} registered!"

    
    def assignPriority(self, patientObject):
        category = patientObject.getTriageCategory()

        if category == "Level 5: Non-Urgent":
            priority_level = "Very Low"
        elif category == "Level 4: Less Urgent":
            priority_level = "Low"
        elif category == "Level 3: Urgent":
            priority_level = "Medium"
        elif  category == "Level 2: Emergent (Very Urgent)":
            priority_level = "High"
        elif category == "Level 1: Resuscitation (Critical)":
            priority_level = "Very High"
        
        patientObject.setPriorityLevel(priority_level)
    
    def assignTriage(self, patientObject):
        index = generate_random_between_two(0, 4)
        patientObject.setTriageCategory(self.triage_categories[index])
    
    def sendToWaitingRoom(self, waitingRoomObject):
        waiting_capacity_flag = waitingRoomObject.checkCapacity()

        if waiting_capacity_flag:
            if self.queue != []:
                patient = self.queue.pop(0)
                waitingRoomObject.registerPatient(patient)

                # Log the transition
                self.transition_log.append({
                    "Patient ID": patient.getID(),
                    "From Room": self.__class__.__name__,
                    "To Room": waitingRoomObject.__class__.__name__,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Action": "Moved"
                })
            else:
                return "No More Patients in Arrival Room!"
        else:
            return "No space in waiting room!"
        


        return None
    
    def getTransitions(self):
        # Return and clear the transition log for this room
        log = self.transition_log[:]
        self.transition_log.clear()
        return log