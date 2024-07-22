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
        
        self.sleepBetweenPackage = 0.92
        
        self.shellConnectionAttemptLimit = 12
        self.shellConnectionAttemptPeriod = 2
        self.cameraFilterAttemptLimit = 5
        
        self.command = "SEND_DATA\n"
        

        #teknofest
        self.teamNumber = 666


        #alarm system
        self.minAltitudeForFlightAssumption=15
        self.consecutiveNeeded=3

        self.detachmentCoefficent=1.5
        
        self.maxLandDifference=5
        self.lastElementsForLandAssumption=5
        self.minAltitudeForLandAssumption=15
        
        self.buzzerPin=6
        self.buzzerWakeFor=1
        self.buzzerSleepFor=1
        
 
        #servo
        self.servoPWMPin = 12
        self.servoDefaultAngle = 90
        self.servoDetachmentAngle = 35
        
        self.servoDetachOperator = 6

        self.servoDetachResetPeriod = 5
        self.servoDetachAwaitSecond = 5
        
mp = MissionParameters();