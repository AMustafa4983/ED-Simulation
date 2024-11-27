class Patient:
    def __init__(self):
        self.paitent_id = None
        self.status = None
        self.priority_level = None
        self.triage_category = None
        self.checkpoints = {}

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