from asyncio.windows_events import NULL
import socket
import time
import json

from data_struct_file import DataPack

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
        
        self.filePath = 'telemetry_data.txt'

        self.groundStation = groundStation;
        self.shell = shell;
        self.cameraFilter = cameraFilter;
        
        self.attemptLimit = 20;
        self.attemptLimitDistance = 5;
        self.counter = 0;
        self.command = 'SEND_DATA';
        self.tryConnectingAgain = False;
        self.dataPackNumber = 0
        
        self.errorCodeList = [0,0,0,0,0];
        self.filterCommandList = [];
        self.filterCommandTransmissionAttempt = 5

        print("Satellite built succesfully");
                
        self.initialConnectionWithDevice(self.shell,self.shellSocket,"shell"); 
        self.initialConnectionWithDevice(self.groundStation,self.gsSocket,"ground station");
        #self.initialConnectionWithDevice(self.cameraFilter,self.cameraFilterSocket,"camera socket");

    
    def shellConnectionProcedure(self):
        responseShell = "null"
        print(self.attemptLimit);
        
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
                self.shellSocket.send(self.command.encode())
                
                responseShell = self.shellSocket.recv(1024).decode()
                responseShell = json.loads(responseShell)
                
            except Exception as e:
                self.tryConnectingAgain = True
                print(f"Lost connection with shell: {e}")
        else:
            print("Out of limit")
            return NULL;
        
        
        return responseShell;
    
    def groundStationConnectionProcedure(self, responseShell):
        try:
            self.gsSocket.send(self.command.encode())
            responseGs = self.gsSocket.recv(1024).decode()
            responseGs = json.loads(responseGs);
            
        except Exception as e:
            print(f"Error communicating with GS server: {e}")
            return
    
        dataPack = DataPack(
            self.dataPackNumber,
            0,  
            self.errorCodeList,
            "19/1/2038", 
            8,  
            responseShell[0], 
            8, 
            responseShell[1], 
            8,  
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
            8,
            8
        )
        if len(responseGs[1])==4:
            self.sendFilterInfoToFilter(list(responseGs[1]));
        
        self.logDataPack(dataPack);
    
        dataJson = json.dumps(dataPack.__dict__);
    
        try:
            self.gsSocket.send(dataJson.encode())
        except Exception as e:
            print(f"Error sending data to GS server: {e}")
            
    def sendFilterInfoToFilter(self,infoList):
        jsonData = json.dumps(infoList)
        
        try:
            self.cameraFilterSocket.send(jsonData.encode());
        except Exception as e:
            print("Problem with sending filter code. Attempt remains: "+str(self.filterCommandTransmissionAttempt));
            if self.filterCommandTransmissionAttempt>0:
                self.filterCommandTransmissionAttempt-=1;
                self.sendFilterInfoToFilter(infoList);
                
    
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
  
    def startMainLoop(self):
        while(True):
            responseFromShell = self.shellConnectionProcedure();
            self.groundStationConnectionProcedure(responseFromShell);
            self.dataPackNumber+=1;
            time.sleep(1);
