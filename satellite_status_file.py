from audioop import avg


class SatelliteStatusJudge:
    
    def __init__(self, minAltitudeForFlightAssumption, consecutiveNeeded, minAltitudeForLandAssumption,detachmentCoefficent):
        self.status = 0
        self.altitudeList = [0, 0, 0]
        self.minAltitudeForFlightAssumption = minAltitudeForFlightAssumption
        self.consecutiveNeeded = consecutiveNeeded
        self.minAltitudeForLandAssumption = minAltitudeForLandAssumption
        self.detachmentCoefficent = detachmentCoefficent;
        self.avgDiff = 0;
        self.avgCounter = 1;
        
        # TODO: calculate real values
        self.attachedAngle = 15
        self.detachedAngle = 45        
    
    def updateAltDiffAvg(self,stAlt,shellAlt):
        
        self.avgDiff = ((self.avgDiff + abs(stAlt-shellAlt))/self.avgCounter);       
        print("avgdiff: ");
        print(self.avgDiff);
        self.avgCounter+=1;

    def checkForDetachment(self,stAlt,shellAlt):
        altDifference = stAlt-shellAlt
        print(altDifference);
       
        minDifferenceNeeded = self.avgDiff*self.detachmentCoefficent;        
        print(minDifferenceNeeded);
        if altDifference >= minDifferenceNeeded:
            return True;
        else:
            return False;

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
            if self.checkForDetachment == True:
                self.status = 4;            

        elif self.status == 4:
            if self.altitudeList[-1] < self.minAltitudeForLandAssumption:
                self.status = 5

    #TODO: servo function uncomment
    def detach(self, servo):
        #servo.angle(self.detachedAngle)
        pass;

    def statusAction(self, servo, buzzerPack):
        if self.status == 3:
            self.detach(servo)
            
        elif self.status == 5:
            buzzerPack.melody()
