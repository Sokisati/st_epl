class SatelliteStatusJudge:
    
    def __init__(self, minAltitudeForFlightAssumption, consecutiveNeeded, minAltitudeForLandAssumption, minValueForDetachmentAssumption):
        self.status = 0
        self.altitudeList = [0, 0, 0]
        self.minAltitudeForFlightAssumption = minAltitudeForFlightAssumption
        self.consecutiveNeeded = consecutiveNeeded
        self.minAltitudeForLandAssumption = minAltitudeForLandAssumption
        self.minValueForDetachmentAssumption = minValueForDetachmentAssumption
        
        # TODO: calculate real values
        self.attachedAngle = 15
        self.detachedAngle = 45
        
    def checkForAscent(self):
        if len(self.altitudeList) <= self.consecutiveNeeded:
            return False
        else:
            lastElements = self.altitudeList[-self.consecutiveNeeded:]
            for i in range(len(lastElements) - 1):
                if lastElements[i] >= lastElements[i + 1]:
                    return False
        return True         
    
    def checkForDescent(self):
        if len(self.altitudeList) <= self.consecutiveNeeded:
            return False
        else:
            lastElements = self.altitudeList[-self.consecutiveNeeded:]
            for i in range(len(lastElements) - 1):
                if lastElements[i] <= lastElements[i + 1]:
                    return False
        return True

    
    def updateAltitude(self, altitude):
        self.altitudeList.append(altitude)

    def updateStatus(self):
        
        if self.status == 0:
            if self.altitudeList[-1] >= self.minAltitudeForFlightAssumption:
                self.status = 1
        
        elif self.status == 1:
            if self.checkForDescent():
                self.status = 2
        
        elif self.status == 2:
            if self.altitudeList[-1] < 400:
                self.status = 3
        
        elif self.status == 3:
            self.status = 4;

        elif self.status == 4:
            if self.altitudeList[-1] < self.minAltitudeForLandAssumption:
                self.status = 5

    def detach(self, servo):
        servo.angle(self.detachedAngle)

    def statusAction(self, servo, buzzerPack):
        if self.status == 3:
            self.detach(servo)
            
        elif self.status == 5:
            buzzerPack.melody()
