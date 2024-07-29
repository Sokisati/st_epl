
class MissionParameters:
    def __init__(self):
        
        #comm.   
        self.shellIp = '192.168.138.23'
        self.groundStationIp = '192.168.138.243'
        self.cameraFilterIp = '127.0.0.1'
        
        self.shellPort = 12345
        self.groundStationPort = 12346
        self.cameraFilterPort = 12347
        
        self.shellTimeout=4
        self.groundStationTimeout=6
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
        
        self.buzzerPin=4
        self.buzzerWakeFor=1
        self.buzzerSleepFor=1
        
 
        #servo
        self.servoPWMPin = 13
        self.servoDefaultAngle = 0
        self.servoDetachmentAngle = 65
        
        self.servoDetachOperator = -6

        self.servoDetachResetPeriod = 5
        self.servoDetachAwaitSecond = 5
        

        #OLED
        self.logoActionSecond = 1
        
        self.fontSize = 11
        self.errorFontSize = 10;
        self.sensorPage0ActionSecond = 5
        self.sensorPage1ActionSecond = 8
     
        
mp = MissionParameters();