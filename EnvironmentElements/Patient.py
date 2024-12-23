class Patient:
    def __init__(self):
        self.paitent_id = None
        self.status = None
        self.priority_level = None
        self.triage_category = None
        self.checkpoints = {}
        self.entry_time = None
        self.exit_time = None

    def setEntryTime(self, current_time):
        self.entry_time = current_time
        return None
    
    def getEntryTime(self):
        return self.entry_time
    
    def setExitTime(self, current_time):
        self.exit_time = current_time
        return None
    
    def getExitTime(self):
        return self.exit_time
    
    def getID(self):
        return self.paitent_id
    
    def setID(self, id):
        self.paitent_id = id

    def getStatus(self):
        return self.status
    
    def setStatus(self, new_status):
        self.status = new_status

    def getPriorityLevel(self):
        return self.priority_level
    
    def setPriorityLevel(self, new_priority_level):
        self.priority_level = new_priority_level

    def getTriageCategory(self):
        return self.triage_category
    
    def setTriageCategory(self, new_triage_category):
        self.triage_category = new_triage_category

    def getCheckpoint(self):
        return self.checkpoints
    
    def setCheckpoint(self, checkpoint_time):
        self.checkpoints[self.status] = checkpoint_time