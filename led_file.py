
"""
import RPi.GPIO as GPIO
import time


class Led:
    def __init__(self,pin,defaultMode):
        self.pin = pin;
         
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18,GPIO.OUT)
        
        if defaultMode==True:
            GPIO.output(18,GPIO.HIGH)
        else:
            GPIO.output(18,GPIO.LOW)
"""
        
        
        
       
        