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
        
    def printValues(self):
        print(f"Packet Number: {self.packetNumber}")
        print(f"ST Status: {self.stStatus}")
        print(f"Error Code List: {self.errorCodeList}")
        print(f"Transmission Time: {self.transmissionTime}")
        print(f"Satellite Pressure: {self.satellitePressure}")
        print(f"Shell Pressure: {self.shellPressure}")
        print(f"Satellite Altitude: {self.satelliteAltitude}")
        print(f"Shell Altitude: {self.shellAltitude}")
        print(f"Altitude Difference: {self.altitudeDifference}")
        print(f"Descent Speed: {self.descentSpeed}")
        print(f"Temperature: {self.temperature}")
        print(f"Battery Voltage: {self.batteryVoltage}")
        print(f"GPS Latitude: {self.gpsLat}")
        print(f"GPS Longitude: {self.gpsLong}")
        print(f"GPS Altitude: {self.gpsAlt}")
        print(f"Pitch: {self.pitch}")
        print(f"Roll: {self.roll}")
        print(f"Yaw: {self.yaw}")
        print(f"Filter Command List: {self.filterCommandList}")
        print(f"IoT Data: {self.iotData}")
        print(f"Team Number: {self.teamNumber}")
        print("\n")

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
        cameraFilterPath = '/home/tars/camera_filter_epl/camera_filter_epl.py'
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

        self.simulation = False

        print("Satellite built succesfully");
        self.oled.display(self.oled.shellAwait);
        #self.initialConnectionWithDevice(self.shell,self.shellSocket,"Shell"); 
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
        
        proccesedData = dataPack
        attributes = [
            'packetNumber', 'stStatus', 'errorCodeList', 'transmissionTime',
            'satellitePressure', 'shellPressure', 'satelliteAltitude', 'shellAltitude',
            'altitudeDifference', 'descentSpeed', 'temperature', 'batteryVoltage',
            'gpsLat', 'gpsLong', 'gpsAlt', 'pitch', 'roll', 'filterCommandList',
            'iotData', 'teamNumber'
        ]
        
        # Replace all -666 values with 'n/a'
        for attr in attributes:
            if getattr(proccesedData, attr) == -666:
                setattr(proccesedData, attr, 'n/a')

        with open(self.filePath,'a') as file:
            file.write(f"PAKET NUMARASI:{proccesedData.packetNumber}\n");
            file.write(f"UYDU STATUSU:{proccesedData.stStatus}\n");
            file.write(f"HATA KODU:{proccesedData.errorCodeList}\n");
            file.write(f"GONDERME SAATI:{proccesedData.transmissionTime}\n");
            file.write(f"BASINC1:{proccesedData.satellitePressure}\n");
            file.write(f"BASINC2:{proccesedData.shellPressure}\n");
            file.write(f"YUKSEKLIK1:{proccesedData.satelliteAltitude}\n");
            file.write(f"YUKSEKLIK2:{proccesedData.shellAltitude}\n");
            file.write(f"IRTIFA FARKI:{proccesedData.altitudeDifference}\n");
            file.write(f"INIS HIZI:{proccesedData.descentSpeed}\n");
            file.write(f"SICAKLIK:{proccesedData.temperature}\n");
            file.write(f"PIL GERILIMI:{proccesedData.batteryVoltage}\n");
            file.write(f"GPS1 LATITUDE:{proccesedData.gpsLat}\n");
            file.write(f"GPS1 LONGITUDE:{proccesedData.gpsLong}\n");
            file.write(f"GPS1 ALTITUDE:{proccesedData.gpsAlt}\n");
            file.write(f"PITCH:{proccesedData.pitch}\n");
            file.write(f"ROLL:{proccesedData.roll}\n");
            file.write(f"RHRH:{proccesedData.filterCommandList}\n");
            file.write(f"IoT DATA>:{proccesedData.iotData}\n");
            file.write(f"TAKIM NO:{proccesedData.teamNumber}\n");
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
            return (957.88 - 12.28*x)
     
    def artificalShellAltFunction(self):
        x = self.dataPackNumber;
        add = 0
        if self.alarmSystem.statusJudge.status==3:
            add = 120
            
        if x<20:
            return x*35 + add
        else:
            return (958 - 12*x)

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
            
    def groundStationResponseActions(self,responseGs):
        if responseGs[1]!='0' and not self.filterCommandListSent:
            self.sendFilterInfoToFilter(list(responseGs[1]));
        
        if responseGs[2]==1:
            self.servo.detach();

    def groundStationConnectionProcedure(self, responseShell):
        
        responseGs = self.groundStationReceiveData();
        
        shellAltitude = responseShell[0];
        shellPressure = responseShell[1];
        
        stAltitude = self.sensorPack.sensorDataPack.altitude;
        
        #just in case bme680 fail midflight
        if stAltitude==-666:
            if self.alarmSystem.statusJudge.status==3:
                stAltitude = shellAltitude
            else:
                stAltitude = self.sensorPack.sensorDataPack.alt

        if self.simulation:
            stAltitude = self.artificalSatAltFunction();
            shellAltitude = self.artificalShellAltFunction();

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
        dataPack.printValues();
        
        self.groundStationSendData(dataPack);
        
        self.logDataPack(dataPack);
    
        return responseGs
            
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
            #to avoid excessive cpu usage
            time.sleep(0.01);
    
    def prepareToEndMission(self):
        self.oled.shutOff();
        self.commandToSend = "END_MISSION\n"
        
    def terminateCameraProgram(self):
        process_name = "python3"
        target_script = "camera_epl.py"

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info.get('cmdline')
            if isinstance(cmdline, list) and proc.info['name'] == process_name and target_script in cmdline:
                pid = proc.info['pid']
                print(f"Found process '{target_script}' with PID {pid}")

                os.kill(pid, signal.SIGINT)
                print(f"Sent SIGINT to process '{target_script}' with PID {pid}")
                break
        else:
            print(f"No process named '{target_script}' found.")
     
    def endMission(self):

        self.terminateCameraProgram();    
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
        responseGs = []
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
            
            responseGs = self.groundStationConnectionProcedure(responseFromShell);
            
            self.groundStationResponseActions(responseGs)

            self.dataPackNumber+=1;
            
            if self.missionEndCounter==30:
                self.endMission();
            
            self.sleep();


