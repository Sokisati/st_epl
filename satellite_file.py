from device_file import *
import socket
import time
import json
from sensor_file import *
import psutil
import os
import signal
import subprocess

class DataPack:
    def __init__(self, packetNumber, stStatus, errorCodeList, transmissionTime, satellitePressure, shellPressure,satelliteAltitude,shellAltitude,altitudeDifference,
                 descentSpeed, temperature, batteryVoltage, gpsLat, gpsLong, gpsAlt, pitch, roll, yaw, filterCommandList, iotData, teamNumber):
        self.packetNumber = packetNumber
        self.stStatus = stStatus
        self.errorCodeList = errorCodeList
        self.transmissionTime = transmissionTime
        self.satellitePressure = satellitePressure
        self.shellPressure = shellPressure
        self.satelliteAltitude = satelliteAltitude
        self.shellAltitude = shellAltitude
        self.altitudeDifference = altitudeDifference
        self.descentSpeed = descentSpeed
        self.temperature = temperature
        self.batteryVoltage = batteryVoltage
        self.gpsLat = gpsLat
        self.gpsLong = gpsLong
        self.gpsAlt = gpsAlt
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
        self.filterCommandList = filterCommandList
        self.iotData = iotData
        self.teamNumber = teamNumber

class Satellite:
    
    def initialConnectionWithDevice(self, device, sock, deviceName):
        while True:
            try:
                print(f"Attempting connection to {deviceName} at {device.ip}:{device.port}")
                sock.connect((device.ip, device.port))
                print(f"{deviceName} connection successful")
                break
            except socket.timeout:
                print(f"Initial connection to {deviceName} timed out. Trying again.")
            except socket.error as e:
                print(f"Initial connection to {deviceName} failed. Trying again: {e}")
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as e:
                print(f"Unexpected error when connecting to {deviceName}: {e}")
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            time.sleep(0.2)
    
    def __init__(self, groundStation, shell, cameraFilter):
        cameraFilterPath = '/home/glados/camera_filter_epl/camera_filter_epl.py'
        subprocess.Popen(['python3', cameraFilterPath])
        
        self.mp = MissionParameters()
        self.oled = OLED();
        
        self.oled.display(self.oled.logoPage);
        time.sleep(self.oled.logoPage.actionSecond);
        
        self.sensorPack = SensorPack(); 
        self.shellSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.gsSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.cameraFilterSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        
        self.alarmSystem = AlarmSystem();
        
        self.commandToSend = "SEND_DATA\n"
        self.missionEndLine = "Thank you for participating in this Aperture Science computer-aided enrichment activity."
        self.missionEndCounter = 0;

        self.filePath = 'telemetry_data.txt'

        self.groundStation = groundStation;
        self.shell = shell;
        self.cameraFilter = cameraFilter;
        self.servo = Servo();
        
        self.shellSocket.settimeout(self.shell.timeoutDuration);
        self.gsSocket.settimeout(self.groundStation.timeoutDuration);
        self.cameraFilterSocket.settimeout(self.cameraFilter.timeoutDuration);

        self.shellAttemptCounter = 0;
        self.tryConnectingAgain = False;
        
        self.dataPackNumber = 0;
        
        self.gsConnectionError = False;
        
        self.iot = 0;
        self.shellAltitude = 0;
        
        self.errorCodeList = [0,0,0,0,0];
        self.filterCommandList = [];
        self.filterCommandListSent = False;

        print("Satellite built succesfully");
        self.oled.display(self.oled.shellAwait);
        self.initialConnectionWithDevice(self.shell,self.shellSocket,"Shell"); 
        self.oled.display(self.oled.gsAwait);
        self.initialConnectionWithDevice(self.groundStation,self.gsSocket,"Ground station");
        self.oled.display(self.oled.gsSucces);
        self.initialConnectionWithDevice(self.cameraFilter,self.cameraFilterSocket,"camera socket");

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

        responseShell = [-666,-666]
        rawData = -666;

        if self.mp.shellConnectionAttemptLimit > 0 and self.tryConnectingAgain:
            self.shellAttemptCounter += 1
            if (self.shellAttemptCounter % self.mp.shellConnectionAttemptPeriod) == 0:
                try:
                    self.shellSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.shellSocket.settimeout(self.mp.shellTimeout)
                    self.shellSocket.connect((self.mp.shellIp, self.mp.shellPort))
                    
                    self.tryConnectingAgain = False
                    
                except Exception as e:
                    print(f"Error re-connecting to shell server: {e}")
                    self.mp.shellConnectionAttemptLimit -= 1
                    print("Attempt limit remain: " + str(self.mp.shellConnectionAttemptLimit))
                    self.tryConnectingAgain = True
                    
        elif not self.tryConnectingAgain:
            try:
                self.shellSocket.send(self.commandToSend.encode());
                rawData = self.shellSocket.recv(1024)
                responseShell = self.splitData(rawData);

            except Exception as e:
                self.tryConnectingAgain = True
                print(f"Lost connection with shell: {e}")
        else:
            pass
       
        return responseShell;

    def artificalSatAltFunction(self):
        x = self.dataPackNumber;
        
        if x<20:
            return x*35
        else:
            return (1225 - 11.67*x)

        
    def artificalShellAltFunction(self):
        x = self.dataPackNumber;
        add = 0
        if self.alarmSystem.statusJudge.status==3:
            add = 120
        if x<20:
            return x*35 + add
        else:
            return 700 - (6.67*x) + add

    def groundStationReceiveData(self):
        responseGs = [-666,'0',0] 

        if self.gsConnectionError:
            try:
                self.gsSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.gsSocket.settimeout(self.groundStation.timeoutDuration)
                self.gsSocket.connect((self.groundStation.ip, self.groundStation.port))

                self.gsConnectionError = False

                self.gsSocket.send(self.commandToSend.encode())
                raw_response = self.gsSocket.recv(1024).decode()
                responseGs = json.loads(raw_response)
            
            except Exception as e:
                print(f"Error with reconnection with GS server: {e}")
                
        else:
            try:
                self.gsSocket.send(self.commandToSend.encode())
                raw_response = self.gsSocket.recv(1024).decode()
                responseGs = json.loads(raw_response)
            
            except Exception as e:
                print(f"Error communicating with GS server: {e}")
                self.gsConnectionError = True

   
        if not isinstance(responseGs, list) or len(responseGs) < 2:
            responseGs = [0, '0',0] 

        return responseGs

    def groundStationSendData(self,dataPack):
        
        dataJson = json.dumps(dataPack.__dict__);
        try:
            self.gsSocket.send(dataJson.encode())
        except Exception as e:
            print(f"Error sending data to GS server: {e}")

    def groundStationConnectionProcedure(self, responseShell):
        
        responseGs = self.groundStationReceiveData();
        
        shellAltitude = responseShell[0];
        shellPressure = responseShell[1]*100;
        
        stAltitude = self.sensorPack.sensorDataPack.altitude;
        
        #just in case bme680 fail midflight
        if stAltitude==-666:
            if self.alarmSystem.statusJudge.status==3:
                stAltitude = shellAltitude
            else:
                stAltitude = self.sensorPack.sensorDataPack.alt

        stAltitude = self.artificalSatAltFunction();
        shellAltitude = self.artificalShellAltFunction();

        if self.dataPackNumber == 35:
            self.toDelete = 20;

        self.errorCodeList = self.alarmSystem.getErrorCodeList(stAltitude,shellAltitude,
                                                               self.sensorPack.sensorDataPack.lat)

        self.iot = responseGs[0];
        self.shellAltitude = shellAltitude
        
        dataPack = DataPack(
            self.dataPackNumber,
            self.alarmSystem.statusJudge.status,  
            self.errorCodeList,
            self.sensorPack.sensorDataPack.dateAndTime, 
            self.sensorPack.sensorDataPack.pressure,  
            shellPressure, 
            stAltitude, 
            shellAltitude, 
            abs(stAltitude-shellAltitude),  
            self.alarmSystem.statusJudge.getDescentSpeed(), 
            self.sensorPack.sensorDataPack.temperature, 
            self.sensorPack.sensorDataPack.voltage, 
            self.sensorPack.sensorDataPack.lat,  
            self.sensorPack.sensorDataPack.long,  
            self.sensorPack.sensorDataPack.alt,  
            self.sensorPack.sensorDataPack.pitch, 
            self.sensorPack.sensorDataPack.roll,  
            self.sensorPack.sensorDataPack.yaw, 
            responseGs[1], 
            responseGs[0],
            self.mp.teamNumber
        )
        
        if responseGs[1]!='0' and not self.filterCommandListSent:
            self.sendFilterInfoToFilter(list(responseGs[1]));
        
        if responseGs[2]!=0:
            self.servo.detach();

        self.logDataPack(dataPack);
        
        self.groundStationSendData(dataPack);
            
    def sendFilterInfoToFilter(self, infoList):
        print("Sending list to filter:")
        jsonData = json.dumps(infoList)
        try:
            self.cameraFilterSocket.send(jsonData.encode())
            self.filterCommandListSent = True
        except Exception as e:
            print("Problem with sending filter code. Attempt remains: " + str(self.mp.cameraFilterAttemptLimit))
            if self.mp.cameraFilterAttemptLimit > 0:
                self.mp.cameraFilterAttemptLimit -= 1
                self.sendFilterInfoToFilter(infoList)
                
    def sleep(self):
        currentTime = self.sensorPack.time.getDateAndTime();
        updatedTime = self.sensorPack.time.getDateAndTime();
        while currentTime==updatedTime:
            updatedTime = self.sensorPack.time.getDateAndTime();
            time.sleep(0.01); #to avoid excessive cpu usage
    
    def prepareToEndMission(self):
        self.oled.shutOff();
        self.commandToSend = "END_MISSION\n"
        
    def killCameraProgram(self):
        process_name = "python3"
        target_script = "camera_epl.py"

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == process_name and target_script in proc.info['cmdline']:
                pid = proc.info['pid']
                print(f"Found process '{target_script}' with PID {pid}")
        
                os.kill(pid, signal.SIGINT)
                print(f"Sent SIGINT to process '{target_script}' with PID {pid}")
                break
        else:
            print(f"No process named '{target_script}' found.")
        
    def endMission(self):

        self.killCameraProgram();    
        print(self.missionEndLine);
    
        #it landed and it's been 30 seconds, we don't need transmission anymore
        self.alarmSystem.buzzer.onOffLoop();
        
    def statusAction(self):
        if self.alarmSystem.statusJudge.status!=0:            
            self.oled.shutOff();

        if self.alarmSystem.statusJudge.status==3:
            self.servo.detach();
        
        if self.alarmSystem.statusJudge.status==5:
            self.missionEndCounter+=1
            if self.missionEndCounter==30:
                self.prepareToEndMission();
                  
    def startMainLoop(self):
        while(True):

            self.statusAction();

            self.sensorPack.updateSensorDataPack();
            
            self.oled.updateDisplayProcedure(self.sensorPack.sensorDataPack.temperature,
                                            self.sensorPack.sensorDataPack.pressure,
                                            self.sensorPack.sensorDataPack.altitude,
                                            self.sensorPack.sensorDataPack.voltage,
                                            self.sensorPack.sensorDataPack.dateAndTime,
                                            self.sensorPack.sensorDataPack.roll,
                                            self.sensorPack.sensorDataPack.pitch,
                                            self.sensorPack.sensorDataPack.yaw,
                                            self.iot,
                                            self.shellAltitude,self.alarmSystem.errorCodeList,
                                            self.sensorPack.sensorDataPack.current,self.gsConnectionError)  
                
            responseFromShell = self.shellConnectionProcedure();
            self.groundStationConnectionProcedure(responseFromShell);
            
            self.dataPackNumber+=1;
            
            if self.missionEndCounter==30:
                self.endMission();
            
            self.sleep();


