from re import S
from satellite_status_file import SatelliteStatusJudge
import RPi.GPIO as GPIO

class Buzzer:
    def __init__(self,pinNumber,wakeFor,sleepFor):
        self.pinNumber = pinNumber;
        self.wakeFor = wakeFor;
        self.sleepFor = sleepFor;
        GPIO.setmode(GPIO.BCM);
        GPIO.setup(self.pinNumber, GPIO.OUT);
        self.counter = 0;
        self.onState = False;
        self.triggered = False;
        
    def on(self):
        GPIO.output(self.pinNumber, GPIO.HIGH);
        self.onState = True;

    def off(self):
        GPIO.output(self.pinNumber, GPIO.LOW);
        self.offState = False;

    def onOffProcedure(self):
        
        self.counter+=1;
        
        #DELETE THIS WHEN YOU ARE DONE
        if self.counter==30:
            self.off();
            GPIO.cleanup();

        if not self.triggered:
            self.triggered = True;
            self.on();
            return;

        if self.onState:
            print("wow39");
            if self.counter>self.wakeFor:
                self.counter=0;
                self.off();
        
        else:
            print("wow45");
            if self.counter==self.sleepFor:
                self.counter=0;
                self.on();
            

class AlarmSystem:
    
    def __init__(self,minAltitudeForFlightAssumption,consecutiveAscentNeeded,minAltitudeForLandAssumption,
                 detachmentCoefficent,maxLandDifference,buzzerPin,buzzerWakeFor,buzzerSleepFor):
       
       self.modelSatelliteNormalSpeedRange = [12,14];
       self.missionPayloadNormalSpeedRange = [6,8];
       self.buzzer = Buzzer(buzzerPin,buzzerWakeFor,buzzerSleepFor);

       self.errorCodeList = [0,0,0,0,0];
       self.statusJudge = SatelliteStatusJudge(minAltitudeForFlightAssumption, consecutiveAscentNeeded,
                                               minAltitudeForLandAssumption,detachmentCoefficent,maxLandDifference)
           
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

            
         
        
    
        
        