from parameter_file import *

class SatelliteStatusJudge:
    
    def __init__(self):
        
        self.mp = MissionParameters()
        self.status = 0
        self.altitudeList = []
        
        self.avgDiff = 0;

        self.avgCounter = 1;
        
    def checkForLand(self):
        lastElementsList = self.altitudeList[-self.mp.lastElementsForLandAssumption:]
        maxAlt = max(lastElementsList);
        minAlt = min(lastElementsList);
        
        if (maxAlt-minAlt)<=self.mp.maxLandDifference:
            return True;
        else:
            return False;

    def updateAltDiffAvg(self, stAlt, shellAlt):
        
        diff = abs(stAlt - shellAlt)
        self.avgDiff = (self.avgDiff * (self.avgCounter - 1) + diff) / self.avgCounter
        self.avgCounter += 1

    def checkForDetachment(self,stAlt,shellAlt):
        
        altDifference = abs(stAlt-shellAlt)

        if altDifference >= self.mp.detachmentDifference:
            return True;
        else:
            return False;

            
    def checkForAscent(self):
        if len(self.altitudeList) <= self.mp.consecutiveNeeded:
            return False
        else:
            lastElements = self.altitudeList[-self.mp.consecutiveNeeded:]
            for i in range(len(lastElements) - 1):
                if lastElements[i] + self.mp.measurementDeviation > lastElements[i + 1]:
                    return False
        return True         
    
    def checkForDescent(self):
        
        if len(self.altitudeList) <= self.mp.consecutiveNeeded:
            return False
        else:
            lastElements = self.altitudeList[-self.mp.consecutiveNeeded:]
            for i in range(len(lastElements) - 1):
                if lastElements[i] < lastElements[i + 1] + self.mp.measurementDeviation :
                    return False
        return True
    
    def getDescentSpeed(self): 
        if not self.checkForDescent():
            return 0;
        descentTime = self.mp.consecutiveNeeded - 1 
        descentDistance = self.altitudeList[-self.mp.consecutiveNeeded] - self.altitudeList[-1]
        descentSpeed = descentDistance / descentTime  
        return descentSpeed

    def updateAltitude(self, stAltitude):
        self.altitudeList.append(stAltitude)

    def updateStatus(self,stAlt,shellAlt):
        
        self.updateAltitude(stAlt);
        self.updateAltDiffAvg(stAlt,shellAlt);
        
        if self.status<3:
            self.updateAltDiffAvg(stAlt,shellAlt);
        
        if self.status == 0:
            if ((self.altitudeList[-1] >= self.mp.minAltitudeForFlightAssumption) and (self.checkForAscent()==True)):
                self.status = 1
        
        elif self.status == 1:
            if self.checkForDescent():
                self.status = 2
        
        elif self.status == 2:
            if self.altitudeList[-1] < 400:
                self.status = 3
        
        elif self.status == 3:
            detached = self.checkForDetachment(stAlt,shellAlt)
            if detached == True:
                self.status = 4; 
            elif self.checkForLand()==True:
                self.status = 5

        elif self.status == 4:
            if self.altitudeList[-1] < self.mp.minAltitudeForLandAssumption or self.checkForLand()==True:
                self.status = 5

