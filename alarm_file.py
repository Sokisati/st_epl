from satellite_status_file import SatelliteStatusJudge

class AlarmSystem:
    
    def __init__(self,minAltitudeForFlightAssumption,consecutiveAscentNeeded,minAltitudeForLandAssumption,minValueForDetachmentAssumption):
       self.errorCodeList = [0,0,0,0,0];
       self.statusJudge = SatelliteStatusJudge(minAltitudeForFlightAssumption, consecutiveAscentNeeded, minAltitudeForLandAssumption, minValueForDetachmentAssumption)
        
        
    def satelliteSpeedAbnormal(self):
        self.errorCodeList[0]=1;  
    
    def missionPayloadSpeedAbnormal(self):
        self.errorCodeList[1]=1; 

    def shellNotResponding(self):
           self.errorCodeList[2]=1;
    
    def missionPayloadGpsDataError(self):
        self.errorCodeList[3]=1; 
       
    def seperationFailed(self):
           self.errorCodeList[4]=1;
    
        
    def resetList(self):
        for i in range (5):
            self.errorCodeList[i]==0; 

    
        
        