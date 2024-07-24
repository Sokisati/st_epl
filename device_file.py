# -*- coding: utf-8 -*-

from sys import setdlopenflags
from alarm_file import *
from parameter_file import *

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import time
from parameter_file import MissionParameters

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


class OLEDPage:
    def __init__(self, actionSecond):
        self.actionSecond = actionSecond
class BMPPage(OLEDPage):
    def __init__(self, path, actionSecond):
        super().__init__(actionSecond)
        self.bmp = Image.open(path).convert('1')

    def display(self, disp):
        disp.image(self.bmp)
        disp.display()
        time.sleep(self.actionSecond)
class TextPage(OLEDPage):
    def __init__(self, fontSize, textLines, actionSecond):
        super().__init__(actionSecond)
        self.fontSelection = 'DejaVuSans-Bold.ttf'
        self.fontSize = fontSize
        self.font = ImageFont.truetype(self.fontSelection, self.fontSize)
        self.textLines = textLines
        
    
    def drawText(self):
        image = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(image)
        
        y = 0
        for line in self.textLines:
            draw.text((0, y), line, font=self.font, fill=255)
            y += self.fontSize
        
        return image

    def display(self, disp):
        image = self.drawText()
        disp.image(image)
        disp.display()
        time.sleep(self.actionSecond)
class SensorPage(TextPage):
    def __init__(self, fontSize, actionSecond):
        super().__init__(fontSize, [], actionSecond)
        self.temperature = 0;
        self.pressure = 0;
        self.altitude = 0;
        self.batteryVoltage = 0;
        self.errorCodeList = [0,0,0,0,0];
    
    def updateSensorInfo(self,temperature, pressure, altitude, batteryVoltage, errorCodeList):
        self.temperature = temperature;
        self.pressure = pressure;
        self.altitude = altitude;
        self.batteryVoltage = batteryVoltage;
        self.errorCodeList = errorCodeList;
        
    def getSensorImage(self):
        self.pressure /= 100  
        line0 = "Sıcaklık: " + str(self.temperature) + "C"
        line1 = "Basınç: " + str(self.pressure) + "kPa"
        line2 = "İrtifa: " + str(self.altitude) + "m"
        line3 = "Batarya voltajı: " + str(self.batteryVoltage) + "V"
        line4 = "Hata kodu listesi: N/A , N/A , " + self.errorCodeList[2] + " , " + self.errorCodeList[3] + ", N/A"

        sensorText = [line0, line1, line2, line3, line4]
        image = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(image)
        y = 0

        for line in sensorText:
            draw.text((0, y), line, font=self.font, fill=255)
            y += self.fontSize

        return image

    def display(self, disp):
        image = self.getSensorImage()
        disp.image(image)
        disp.display()
        time.sleep(self.actionSecond)

class OLED:
    def __init__(self):
        self.mp = MissionParameters();
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        self.bmpPage = BMPPage(self.mp.logoPath,self.mp.bmpActionSecond)
        self.sensorPage = SensorPage(self.mp.fontSize,self.mp.sensorPageActionSecond)
        
        self.pageList = [self.bmpPage,self.sensorPage];
        self.counter = 0
        self.index = 0
    
    def updateDisplayProcedure(self,temperature,pressure,altitude,batteryVoltage,errorCodeList):
        
        self.sensorPage.updateSensorInfo(temperature,pressure,altitude,batteryVoltage,errorCodeList);
        
        if self.pageList[self.index].actionSecond==self.counter:            
            self.counter = 0
            
            if (self.index + 1) == len(self.pageList):
                self.index = 0
            else:
                self.index += 1
        
        self.counter+=1
        
        self.display(self.pageList[self.index])

    def display(self, page):
        page.display(self.disp)

    def cleanup(self):
        self.disp.clear()
        self.disp.display()



        
        

