from satellite_status_file import SatelliteStatusJudge
import RPi.GPIO as GPIO
from parameter_file import *
import time

class Buzzer:
    def __init__(self):
        self.mp = MissionParameters();
        
        GPIO.setmode(GPIO.BCM);
        GPIO.setup(self.mp.buzzerPin, GPIO.OUT);
        self.counter = 0;
        
        self.onState = False;
        self.triggered = False;
        self.off();
        
    def on(self):
        GPIO.output(self.mp.buzzerPin, GPIO.HIGH);
        self.onState = True;

    def off(self):
        GPIO.output(self.mp.buzzerPin, GPIO.LOW);
        self.onState = False;

    def onOffProcedure(self):
        
        self.counter+=1;

        if self.onState:
            if self.counter==self.mp.buzzerWakeFor:
                self.counter=0;
                self.off();
        
        else:
            if self.counter==self.mp.buzzerSleepFor:
                self.counter=0;
                self.on();

    def onOffLoop(self):
        while True:
            self.on();
            time.sleep(self.mp.buzzerWakeFor);
            self.off();
            time.sleep(self.mp.buzzerSleepFor)
            
class AlarmSystem:
    
    def __init__(self):
       self.mp = MissionParameters()
       self.modelSatelliteNormalSpeedRange = [12,14];
       self.missionPayloadNormalSpeedRange = [6,8];
       self.buzzer = Buzzer();

       self.errorCodeList = [0,0,0,0,0];
       self.statusJudge = SatelliteStatusJudge()
           
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
        for i in range(len(self.errorCodeList)):
            self.errorCodeList[i]=0; 
    
    def checkForSpeedAnomalyModelSatellite(self):
        descentSpeed = self.statusJudge.getDescentSpeed();
        
        if descentSpeed>max(self.modelSatelliteNormalSpeedRange) or descentSpeed<min(self.modelSatelliteNormalSpeedRange):
            return True;
        else:
            return False;
    
    def checkForSpeedAnomalyMissionPayload(self):
        descentSpeed = self.statusJudge.getDescentSpeed();
        if descentSpeed>max(self.missionPayloadNormalSpeedRange) or descentSpeed<min(self.missionPayloadNormalSpeedRange):
            return True;
        else:
            return False;

    def getErrorCodeList(self,stAlt,shellAlt,gpsLat):
         
         self.resetList();
  
         self.statusJudge.updateStatus(stAlt,shellAlt);
         status = self.statusJudge.status;

         #2 and 3 for every status
         if shellAlt==-666:
            self.shellNotResponding(); 
         if gpsLat < 30 or gpsLat > 44:
            self.missionPayloadGpsDataError();

         if status==0 or status==1 or status==5:
             return self.errorCodeList;
          
         elif status==2:
             if self.checkForSpeedAnomalyModelSatellite()==True:
                 self.satelliteDescentSpeedAbnormal();
             
             return self.errorCodeList;   
            
         elif status==3:
             if self.checkForSpeedAnomalyModelSatellite()==True:
                 self.satelliteDescentSpeedAbnormal();
             
             detached = self.statusJudge.checkForDetachment(stAlt,shellAlt);   
             if detached==False:
                self.detachmentFailed();
             return self.errorCodeList;   

         elif status==4:
             if self.checkForSpeedAnomalyMissionPayload()==True:
                 self.missionPayloadDescentSpeedAbnormal();
             return self.errorCodeList;

            
         
        
    
        
        