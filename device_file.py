from alarm_file import *
from parameter_file import *

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory


class Servo:
    def __init__(self):
        self.mp = MissionParameters()
        factory = PiGPIOFactory();
        self.servo = AngularServo(self.mp.servoPWMPin, min_pulse_width=0.0006, max_pulse_width=0.0023, pin_factory=factory);
        self.servo.angle = self.mp.servoDefaultAngle;
        self.failedAttemptCounter=1;
    
    def detach(self):
        if (not self.failedAttemptCounter==1) and (self.failedAttemptCounter%mp.servoDetachResetPeriod==0):
            self.servo.angle = self.mp.servoDefaultAngle
            
        self.servo.angle = self.mp.servoDetachmentAngle + (self.failedAttemptCounter*self.mp.servoDetachOperator);
        self.failedAttemptCounter+=1;
           
class DistantDevice:
    def __init__(self, ipAddress, port, timeoutDuration):
        self.ip = ipAddress
        self.port = port
        self.timeoutDuration = timeoutDuration



        
        

