from re import I
from satellite_status_file import SatelliteStatusJudge

class AlarmSystem:
    
    def __init__(self,minAltitudeForFlightAssumption,consecutiveAscentNeeded,minAltitudeForLandAssumption,detachmentCoefficent):
       
       self.modelSatelliteNormalSpeedRange = [12,14];
       self.missionPayloadNormalSpeedRange = [6,8];

       self.errorCodeList = [0,0,0,0,0];
       self.statusJudge = SatelliteStatusJudge(minAltitudeForFlightAssumption, consecutiveAscentNeeded, minAltitudeForLandAssumption,detachmentCoefficent)
           
    def satelliteDescentSpeedAbnormal(self):
        self.errorCodeList[0]=1;  
    
    def missionPayloadDescentSpeedAbnormal(self):
        self.errorCodeList[1]=1; 

    def shellNotResponding(self):
           self.errorCodeList[2]=1;
    
    def missionPayloadGpsDataError(self):
        self.errorCodeList[3]=1; 
       
    def detachmentFailed(self):
           self.errorCodeList[4]=1;
    
    def resetList(self):
        for i in range (5):
            self.errorCodeList[i]==0; 
    
    def checkForSpeedAnomaly(self):
        descentSpeed = self.statusJudge.getDescentSpeed();
             
        if descentSpeed>max(self.statusJudge.altitudeList) or descentSpeed<min(self.statusJudge.altitudeList):
            return True;
        else:
            return False;

    def getErrorCodeList(self,stAlt,shellAlt,shellNotResponding,missionPayloadGpsDataError):
         
         self.resetList();
         self.statusJudge.updateStatus(stAlt,shellAlt);
         status = self.statusJudge.status;
         
         #2 and 3 for every status
         if shellNotResponding==True:
            self.shellNotResponding(); 
         if missionPayloadGpsDataError==True:
            self.missionPayloadGpsDataError();


         if status==0 or status==1 or status==5:
             return self.errorCodeList;
    
         elif status==2:
             if self.checkForSpeedAnomaly()==True:
                 self.satelliteDescentSpeedAbnormal();
             return self.errorCodeList;   
            
         elif status==3:
             if self.checkForSpeedAnomaly()==True:
                 self.satelliteDescentSpeedAbnormal();
             
             detached = self.statusJudge.checkForDetachment();   
             if detached==False:
                self.detachmentFailed();
             return self.errorCodeList;   

         elif status==4:
             if self.checkForSpeedAnomaly()==True:
                 self.missionPayloadDescentSpeedAbnormal();
             return self.errorCodeList;

            
         
        
    
        
        