# -*- coding: utf-8 -*-

from datetime import date
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
        self.failedAttemptCounter=0;
    
    def detach(self):
        if (self.failedAttemptCounter != 0) and (self.failedAttemptCounter % self.mp.servoDetachResetPeriod == 0):
            self.failedAttemptCounter=0;
            self.servo.angle = self.mp.servoDefaultAngle
            return

        try:
            self.servo.angle = self.mp.servoDetachmentAngle + (self.failedAttemptCounter * self.mp.servoDetachOperator)
            self.failedAttemptCounter+=1;
        except ValueError:
            self.failedAttemptCounter=0;
            self.servo.angle = self.mp.servoDefaultAngle
            pass
           
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
class SensorPage0(TextPage):
    def __init__(self, fontSize, actionSecond):
        super().__init__(fontSize, [], actionSecond)
        self.temperature = 0;
        self.pressure = 0;
        self.altitude = 0;
        self.batteryVoltage = 0;
        self.shellAltitude = 0;
    
    def updateSensorInfo(self,temperature, pressure, altitude, batteryVoltage, shellAltitude):
        self.temperature = temperature;
        self.pressure = pressure;
        self.altitude = altitude;
        self.batteryVoltage = batteryVoltage;
        self.shellAltitude = shellAltitude;
        
        
    def getSensorImage(self):
        self.pressure /= 100  
        line0 = "Sıcaklık: " + str(self.temperature) + " C"
        line1 = "Basınç: " + str(self.pressure) + " kPa"
        line2 = "İrtifa: " + str(int(self.altitude)) + " m"
        line3 = "Batarya voltajı: " + str(self.batteryVoltage) + " V"
        line4 = "Tasıyıcı irtifa: "+str(self.shellAltitude)+" m"
        
        sensorText = [line0, line1, line2, line3,line4]
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
class SensorPage1(TextPage):
    def __init__(self, fontSize, actionSecond):
        super().__init__(fontSize, [], actionSecond)
        self.roll = 0;
        self.pitch = 0;
        self.yaw = 0;
        self.iot = 0;
        self.shellAltitude = 0
        self.dateAndTime = 0;
        self.batteryCurrent = 0;
    
    def updateSensorInfo(self,roll, pitch, yaw, iot, dateAndTime,errorCodeList,batteryCurrent):
        self.roll = roll;
        self.pitch = pitch;
        self.yaw = yaw;
        self.iot = iot;
        self.dateAndTime = dateAndTime;
        self.errorCodeList = errorCodeList;
        self.batteryCurrent = batteryCurrent;
        
    def getSensorImage(self):
        dateAndTimePart = self.dateAndTime.split('-')[1] if '-' in self.dateAndTime else self.dateAndTime
     
        line0 = "R: " + str(int(self.roll)) + " P: " + str(int(self.pitch)) + " Y: "+ str(int(self.yaw))
        line1 = "IoT: " + str(self.iot)
        line2 = "Saat: " + dateAndTimePart
        line3 = "Hata kodu: " + "x,x,"+str(self.errorCodeList[2])+","+str(self.errorCodeList[3])+",x"
        line4 = "Batarya akımı: " + str(self.batteryCurrent)
        
        sensorText = [line0, line1, line2, line3,line4]
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
class ErrorPage(TextPage):
    def __init__(self, fontSize, actionSecond):
        super().__init__(fontSize, [], actionSecond)

        
    def getErrorImage(self):
      
        textLine = ["Yer istasyonu baglantısı","kesildi."," ","Yeniden baglanılmaya","calısılıyor..."]

        image = Image.new('1', (128, 64))
        draw = ImageDraw.Draw(image)
        
        y = self.fontSize

        for line in textLine:
            draw.text((0, y), line, font=self.font, fill=255)
            y += self.fontSize

        return image

    def display(self, disp):
        image = self.getErrorImage()
        disp.image(image)
        disp.display()

       
class OLED:
    def __init__(self):
        self.mp = MissionParameters();
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        self.off = False;        

        self.logoPage = BMPPage('logo.bmp',self.mp.logoActionSecond)
        
        self.shellAwait = BMPPage('logo_shell_await.bmp',1);
        self.gsAwait = BMPPage('logo_gs_await.bmp',1);
        self.gsSucces = BMPPage('logo_gs_succes.bmp',1);
        self.gsError = ErrorPage(self.mp.errorFontSize,1);
        
        self.sensorPage0 = SensorPage0(self.mp.fontSize,self.mp.sensorPage0ActionSecond)
        self.sensorPage1 = SensorPage1(self.mp.fontSize,self.mp.sensorPage1ActionSecond);
        
        self.pageList = [self.sensorPage0,self.sensorPage1];
        self.counter = 0
        self.index = 0
    
    def updateDisplayProcedure(self, temperature, pressure, altitude, batteryVoltage, dateAndTime,roll,pitch,yaw,
                               iot,shellAltitude,errorCodeList,batteryCurrent,gsConnectionError):
        if not self.off:
            if gsConnectionError==False:            

                self.sensorPage0.updateSensorInfo(temperature,pressure,altitude,batteryVoltage,shellAltitude);
                self.sensorPage1.updateSensorInfo(roll,pitch,yaw,iot,dateAndTime,errorCodeList,batteryCurrent);
        
                self.display(self.pageList[self.index])
        
                self.counter += 1

                if self.counter >= self.pageList[self.index].actionSecond:
                    self.counter = 0
                    if self.index + 1 == len(self.pageList):
                        self.index = 0
                    else:
                        self.index += 1;
        
            else:
                self.display(self.gsError);
        else:
            pass
       
    def display(self, page):
        if not self.off:
            page.display(self.disp)
        else:
            pass

    def shutOff(self):
        self.off = True
        self.disp.clear()
        self.disp.display()
        
    def turnOn(self):
        self.disp.begin()
        self.disp.clear()
        self.disp.display()
        self.off = False;



        
        

