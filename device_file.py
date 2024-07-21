from signal import alarm
import socket
import time
import json

from data_struct_file import DataPack
from alarm_file import *

class DistantDevice:
    def __init__(self, ipAddress, port, timeoutDuration):
        self.ip = ipAddress
        self.port = port
        self.timeoutDuration = timeoutDuration

class Satellite:
    
    def initialConnectionWithDevice(self,device,socket,deviceName):
        while(True):
            try:
                socket.connect((device.ip,device.port));
                break;
            except Exception as e:
                print(f"Initial connection to " +deviceName+ " failed. Trying again: {e}")
                time.sleep(0.5)
    
    def __init__(self, groundStation, shell, cameraFilter):
        
        self.shellSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.gsSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.cameraFilterSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        
        self.alarmSystem = AlarmSystem(minAltitudeForFlightAssumption=15,consecutiveAscentNeeded=3,
                                       minAltitudeForLandAssumption=15,detachmentCoefficent=1.5,maxLandDifference=5,
                                       buzzerPin=6,buzzerWakeFor=1,buzzerSleepFor=1);

        self.toDelete = 0;
        self.toDeleteList = [10,11,10,9,10,11,10];

        #TODO: team number?
        self.teamNumber = 8;
    
        self.filePath = 'telemetry_data.txt'
        self.latestDataPack = DataPack(0,0,[0,0,0,0,0],'1/1/2038',0,0,0,0,0,0,0,0,0,0,0,0,0,0,['0'],0,0);

        self.groundStation = groundStation;
        self.shell = shell;
        self.cameraFilter = cameraFilter;
        
        self.shellSocket.settimeout(self.shell.timeoutDuration);
        self.gsSocket.settimeout(self.groundStation.timeoutDuration);
        self.cameraFilterSocket.settimeout(self.cameraFilter.timeoutDuration);
        self.sleepBetweenPackage = 0.92;
        
        self.attemptLimit = 10;
        self.attemptLimitDistance = 2;
        self.counter = 0;
        self.command = "SEND_DATA\n";
        self.tryConnectingAgain = False;
        self.dataPackNumber = 0;
        
        self.gsConnectionError = False;
        
        self.errorCodeList = [0,0,0,0,0];
        self.filterCommandList = [];
        self.filterCommandTransmissionAttempt = 5;
        self.filterCommandListSent = False;

        print("Satellite built succesfully");
                
        self.initialConnectionWithDevice(self.shell,self.shellSocket,"shell"); 
        print("Shell connection succesful");
        self.initialConnectionWithDevice(self.groundStation,self.gsSocket,"ground station");
        print("Ground station connection succesful");
        self.initialConnectionWithDevice(self.cameraFilter,self.cameraFilterSocket,"camera socket");
        print("Camera program connection succesful");

    def splitData(self, parsed_data):
        try:
            parsed_str = parsed_data.decode().strip()
            parts = parsed_str.split(',')
        
            if len(parts) == 2:
                altitude = int(parts[0])
                pressure = int(parts[1])
                return [altitude, pressure]
            else:
                print(f"Invalid data format: {parsed_str}")
                return [0, 0]

        except Exception as e:
            print(f"Error splitting data: {e}")
            return [0, 0]
            
    def logDataPack(self,dataPack):
        with open(self.filePath,'a') as file:
            file.write(f"PAKET NUMARASI:{dataPack.packetNumber}\n");
            file.write(f"UYDU STATUSU:{dataPack.stStatus}\n");
            file.write(f"HATA KODU:{dataPack.errorCodeList}\n");
            file.write(f"GONDERME SAATI:{dataPack.transmissionTime}\n");
            file.write(f"BASINC1:{dataPack.satellitePressure}\n");
            file.write(f"BASINC2:{dataPack.shellPressure}\n");
            file.write(f"YUKSEKLIK1:{dataPack.satelliteAltitude}\n");
            file.write(f"YUKSEKLIK2:{dataPack.shellAltitude}\n");
            file.write(f"IRTIFA FARKI:{dataPack.altitudeDifference}\n");
            file.write(f"INIS HIZI:{dataPack.descentSpeed}\n");
            file.write(f"SICAKLIK:{dataPack.temperature}\n");
            file.write(f"PIL GERILIMI:{dataPack.batteryVoltage}\n");
            file.write(f"GPS1 LATITUDE:{dataPack.gpsLat}\n");
            file.write(f"GPS1 LONGITUDE:{dataPack.gpsLong}\n");
            file.write(f"GPS1 ALTITUDE:{dataPack.gpsAlt}\n");
            file.write(f"PITCH:{dataPack.pitch}\n");
            file.write(f"ROLL:{dataPack.roll}\n");
            file.write(f"RHRH:{dataPack.filterCommandList}\n");
            file.write(f"IoT DATA>:{dataPack.iotData}\n");
            file.write(f"TAKIM NO:{dataPack.teamNumber}\n");
            
            file.write(f"\n");                

    def shellConnectionProcedure(self):

        responseShell = [0,0]
        rawData = 0;

        if self.attemptLimit > 0 and self.tryConnectingAgain:
            self.counter += 1
            if self.counter % self.attemptLimitDistance == 0:
                try:
                    self.shellSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.shellSocket.settimeout(self.shell.timeoutDuration)
                    self.shellSocket.connect((self.shell.ip, self.shell.port))
                    self.tryConnectingAgain = False
                    
                except Exception as e:
                    print(f"Error re-connecting to shell server: {e}")
                    self.attemptLimit -= 1
                    print("Attempt limit remain: " + str(self.attemptLimit))
                    tryConnectingAgain = True
                    
        elif not self.tryConnectingAgain:
            try:
                self.shellSocket.send(self.command.encode());
                rawData = self.shellSocket.recv(1024)
                responseShell = self.splitData(rawData);

            except Exception as e:
                self.tryConnectingAgain = True
                print(f"Lost connection with shell: {e}")
        else:
            print("Out of limit")
       

        return responseShell;

    def artificalSatAltFunction(self):
        x = self.dataPackNumber;
        return (70*x) - (7/4)*(x ** 2);

    def artificalShellAltFunction(self):
        x = self.dataPackNumber;
        listLength = len(self.toDeleteList);
        return self.toDelete+self.toDeleteList[x%listLength]+self.artificalSatAltFunction();

    def groundStationReceiveData(self):
        
        responseGs = [0,'0'];        

        if self.gsConnectionError==True:
            try:
                self.gsSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                self.gsSocket.settimeout(self.groundStation.timeoutDuration);
                self.gsSocket.connect((self.groundStation.ip, self.groundStation.port));
                
                self.gsConnectionError = False;
                
                self.gsSocket.send(self.command.encode())
                responseGs = self.gsSocket.recv(1024).decode()
                responseGs = json.loads(responseGs);
            
            except Exception as e:
                print(f"Error with reconnection with GS server: {e}")
        else:
            try:
                self.gsSocket.send(self.command.encode())
                responseGs = self.gsSocket.recv(1024).decode()
                responseGs = json.loads(responseGs);
            
            except Exception as e:
                print(f"Error communicating with GS server: {e}")
                self.gsConnectionError = True;
         
        return responseGs;
     
    def groundStationSendData(self,dataPack):
        
        dataJson = json.dumps(dataPack.__dict__);
        try:
            self.gsSocket.send(dataJson.encode())
        except Exception as e:
            print(f"Error sending data to GS server: {e}")

    def groundStationConnectionProcedure(self, responseShell):
        
        responseGs = self.groundStationReceiveData();
        
        shellPressure = 0;
        """
        shellAltitude = 0;
        if len(responseShell)==2:
            shellAltitude = responseShell[0];
            shellPressure = responseShell[1]*100;
        """
        #TODO: fix this 
        stAltitude = self.artificalSatAltFunction();
        shellAltitude = self.artificalShellAltFunction();
        
        if self.alarmSystem.statusJudge.status==4:
            stAltitude = self.toDeleteList[self.dataPackNumber%5];
        
        self.errorCodeList = self.alarmSystem.getErrorCodeList(stAltitude,shellAltitude,False,False);
        
        if self.dataPackNumber==36:
            self.toDelete=6;

        dataPack = DataPack(
            self.dataPackNumber,
            self.alarmSystem.statusJudge.status,  
            self.errorCodeList,
            "19/1/2038", 
            8,  
            shellPressure, 
            stAltitude, 
            shellAltitude, 
            abs(stAltitude-shellAltitude),  
            8, 
            8, 
            8, 
            8,  
            8,  
            8,  
            8, 
            8,  
            self.filterCommandList,  
            responseGs[1], 
            responseGs[0],
            self.teamNumber
        )
        
        self.latestDataPack = dataPack;
        
        if responseGs[1]!='0' and not self.filterCommandListSent:
            self.sendFilterInfoToFilter(list(responseGs[1]));

        #self.logDataPack(dataPack);
        
        self.groundStationSendData(dataPack);
            
    def sendFilterInfoToFilter(self, infoList):
        print("Sending command list to filter:")
        jsonData = json.dumps(infoList)
        try:
            self.cameraFilterSocket.send(jsonData.encode())
            self.filterCommandListSent = True
        except Exception as e:
            print("Problem with sending filter code. Attempt remains: " + str(self.filterCommandTransmissionAttempt))
            if self.filterCommandTransmissionAttempt > 0:
                self.filterCommandTransmissionAttempt -= 1
                self.sendFilterInfoToFilter(infoList)
  
    def startMainLoop(self):
        while(True):
            responseFromShell = self.shellConnectionProcedure();
            self.groundStationConnectionProcedure(responseFromShell);
            self.dataPackNumber+=1;
            
            if self.alarmSystem.statusJudge.status==5:
                 self.alarmSystem.buzzer.onOffProcedure();                

            time.sleep(self.sleepBetweenPackage);

        
        

