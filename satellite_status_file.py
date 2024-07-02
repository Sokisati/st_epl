
class SatelliteStatusJudge:
    def __init__(self,minAltitudeForFlightAssumption,consecutiveAscentNeeded,minAltitudeForLandAssumption):
        self.status = 0;
        self.altitudeList = [];
        self.minAltitudeForStatusFlight = minAltitudeForFlightAssumption;
        self.consecutiveAscentNeeded=consecutiveAscentNeeded;
        self.minAltitudeForLandAssumption = minAltitudeForLandAssumption;
    

    def checkForAscent(self):
        if len(self.altitudeList)<=self.consecutiveAscentNeeded:
            return False;
        else:
            
            lastElements = self.altitudeList[-self.consecutiveAscentNeeded:]
            for i in range(len(lastElements) - 1):
                if lastElements[i] >= lastElements[i + 1]:
                    return False
        return True           


    def updateAltitude(self,altitude):
        self.altitudeList.append(altitude);


    def updateStatus(self):
        if self.status==0:
            if max(self.altitudeList)>=self.minAltitudeForFlightAssumption:
                self.status = 1;
        
        elif self.status==1:
            if self.checkForAscent():
                self.status = 2;
        
        elif self.status==2:
            if min(self.altitudeList)<400:
                self.status = 3;
        
        #skip details for now, finish it when LDR or some other method is decided
        elif self.status==3:
            self.status = 4;

        elif self.status==4:
            if min(self.altitudeList)<self.minAltitudeForLandAssumption:
                self.status = 5;
"""
    def statusAction(self):
        if self.status==0:
           
        
        elif self.status==1:
            
        
        elif self.status==2:
            
        
        #skip details for now, finish it when LDR or some other method is decided
        elif self.status==3:
            

        elif self.status==4:
            """
            
        
        
            
       