
class MissionParameters:
    def __init__(self):
        
        #comm.   
        self.shellIp = '192.168.137.243'
        self.groundStationIp = '192.168.1.2'
        self.cameraFilterIp = '127.0.0.1'
        
        self.shellPort = 12345
        self.groundStationPort = 12346
        self.cameraFilterPort = 12347
        
        self.shellTimeout=3
        self.groundStationTimeout=4
        self.cameraFilterTimeout=2
        
        self.shellConnectionAttemptLimit = 12
        self.shellConnectionAttemptPeriod = 6
        self.cameraFilterAttemptLimit = 5
        

        #teknofest
        self.teamNumber = 666


        #sensor
        self.sensorInitialSleep = 2


        #alarm system (be very careful about these parameters!)
        self.measurementDeviation=2
        self.minAltitudeForFlightAssumption=25
        self.consecutiveNeeded=3

        self.detachmentDifference=10

        self.offsetSampleSize = 5
        
        self.maxLandDifference=5
        self.lastElementsForLandAssumption=5
        self.minAltitudeForLandAssumption=20
        
        self.buzzerPin=27
        self.buzzerWakeFor=1
        self.buzzerSleepFor=1
        
 
        #servo
        self.servoPWMPin = 13
        self.servoDefaultAngle = 80
        self.servoDetachmentAngle = 45
        

        #OLED
        self.logoActionSecond = 1
        
        self.fontSize = 11
        self.errorFontSize = 10;
        self.sensorPage0ActionSecond = 5
        self.sensorPage1ActionSecond = 8
     
        
mp = MissionParameters();