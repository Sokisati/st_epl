class SatelliteStatusJudge:
    
    def getLDRData(self):
        # TODO: implement LDR value function here
        return 0
                   
    def __init__(self, minAltitudeForFlightAssumption, consecutiveAscentNeeded, minAltitudeForLandAssumption, minValueForDetachmentAssumption):
        self.status = 0
        self.altitudeList = [0, 0, 0]
        self.minAltitudeForFlightAssumption = minAltitudeForFlightAssumption
        self.consecutiveAscentNeeded = consecutiveAscentNeeded
        self.minAltitudeForLandAssumption = minAltitudeForLandAssumption
        self.minValueForDetachmentAssumption = minValueForDetachmentAssumption
        
        # TODO: calculate real values
        self.attachedAngle = 15
        self.detachedAngle = 45
        
    def checkForAscent(self):
        if len(self.altitudeList) <= self.consecutiveAscentNeeded:
            return False
        else:
            lastElements = self.altitudeList[-self.consecutiveAscentNeeded:]
            for i in range(len(lastElements) - 1):
                if lastElements[i] >= lastElements[i + 1]:
                    return False
        return True         
    
    def checkForDescent(self):
        if len(self.altitudeList) <= self.consecutiveDescentNeeded:
            return False
        else:
            lastElements = self.altitudeList[-self.consecutiveDescentNeeded:]
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
            if min(self.altitudeList) < 400:
                self.status = 3
        
        elif self.status == 3:
            ldrValue = self.getLDRData()
            if ldrValue <= self.minValueForDetachmentAssumption:
                self.status = 4

        elif self.status == 4:
            if min(self.altitudeList) < self.minAltitudeForLandAssumption:
                self.status = 5

    def detach(self, servo):
        servo.angle(self.detachedAngle)

    def statusAction(self, servo, buzzerPack):
        if self.status == 3:
            self.detach(servo)
            
        elif self.status == 5:
            buzzerPack.melody()
