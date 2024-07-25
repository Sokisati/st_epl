import time
import math
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import bme680
import gpsd

class MPUSensor:
    def __init__(self, dt=1.0):
        self.dt = dt  
        self.yaw = 0  
        self.gyroZBias = 0  

        self.mpu = MPU9250(
            address_ak=AK8963_ADDRESS,
            address_mpu_master=MPU9050_ADDRESS_68,
            address_mpu_slave=None,
            bus=1,
            gfs=GFS_250, 
            afs=AFS_2G,  
            mfs=AK8963_BIT_16,  
            mode=AK8963_MODE_C100HZ 
        )
        time.sleep(0.4)
        self.mpu.configure()
        time.sleep(0.4)
        self.calculateGyroBias()

    def calculateGyroBias(self):
        biasSum = 0
        numSamples = 100  
        for _ in range(numSamples):
            gyroData = self.mpu.readGyroscopeMaster()
            biasSum += gyroData[2]  
            time.sleep(0.01)
        self.gyroZBias = biasSum / numSamples

    def getRoll(self):
        accelData = self.mpu.readAccelerometerMaster()
        ax, ay, az = accelData
        roll = math.atan2(ay, az) * (180 / math.pi)
        return roll

    def getPitch(self):
        accelData = self.mpu.readAccelerometerMaster()
        ax, ay, az = accelData
        pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az)) * (180 / math.pi)
        return pitch

    def getYaw(self):
        gyroData = self.mpu.readGyroscopeMaster()
        gyroZ = gyroData[2]
        self.yaw += (gyroZ - self.gyroZBias) * self.dt
        return self.yaw
    
    def test(self):

        print("Roll");
        print(self.getRoll());
        print("Pitch");
        print(self.getPitch());
        print("Yaw");
        print(self.getYaw());

class BMESensor:
    def __init__(self):
        try:
            self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        
        # Disable gas measurements to prevent overheating (we don't need it)
        self.sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)

        self.temperature = None
        self.pressure = None
        self.humidity = None
        self.altitude = None
        
        time.sleep(0.4);

    def readSensorData(self):
        if self.sensor.get_sensor_data():
            self.temperature = self.sensor.data.temperature
            self.pressure = self.sensor.data.pressure * 100  
            self.humidity = self.sensor.data.humidity
            self.altitude = 44330 * (1 - (self.pressure / 101325) ** (1 / 5.255)) 
            return True
        return False

    def getTemp(self):
        if self.sensor.get_sensor_data():
            return self.sensor.data.temperature

    def getPressure(self):
        if self.sensor.get_sensor_data():
            return self.sensor.data.pressure * 100 

    def getAlt(self):
        if self.sensor.get_sensor_data():
            pressure = self.getPressure();
            return (44330 * (1 - (pressure / 101325) ** (1 / 5.255)))
    
    def test(self):
        if self.sensor.get_sensor_data():
            print("temp:")
            print(self.getTemp());
            print("pressure:")
            print(self.getPressure());
            print("alt:")
            print(self.getAlt());
        else:
            print("error")
            
class GPSSensor:
    def __init__(self):

        gpsd.connect()
        time.sleep(1);
    
    def getLat(self):

        packet = gpsd.get_current()
        return packet.lat

    def getLong(self):

        packet = gpsd.get_current()
        return packet.lon

    def getAlt(self):

        packet = gpsd.get_current()
        return packet.alt

    def test(self):
        print("Latitude:", self.getLat())
        print("Longitude:", self.getLong())
        print("Altitude:", self.getAlt())
        
class SensorDataPack:
    def __init__(self):
        self.lat = 0;
        self.long = 0;
        self.alt = 0;
        self.temperature = 0;
        self.pressure = 0;
        self.altitude = 0;
        self.voltage = 0;
        self.roll = 0;
        self.pitch = 0;
        self.yaw = 0;
        self.dateAndTime = '1/1/2038-31:52:12'
        
class SensorPack:
    
    def __init__(self):
        self.bme = BMESensor();
        self.gyro = MPUSensor();
        self.gps = GPSSensor();
        self.sensorDataPack = SensorDataPack();
    
    def test(self):
        self.bme.test();
        self.gyro.test();
        self.gps.test();

    def updateSensorDataPack(self):
        self.sensorDataPack.lat = 0;
        self.sensorDataPack.long = 0;
        self.sensorDataPack.alt = 0;
        self.sensorDataPack.roll = self.gyro.getRoll();
        self.sensorDataPack.pitch = self.gyro.getPitch();
        self.sensorDataPack.yaw = self.gyro.getYaw();
        self.sensorDataPack.temperature = self.bme.getTemp();
        self.sensorDataPack.pressure = self.bme.getPressure();
        self.sensorDataPack.altitude = self.bme.getAlt();
    
    def printDataPack(self):
        print(f"Latitude: {self.sensorDataPack.lat}")
        print(f"Longitude: {self.sensorDataPack.long}")
        print(f"Altitude (GPS): {self.sensorDataPack.alt}")
        print(f"Temperature: {self.sensorDataPack.temperature}")
        print(f"Pressure: {self.sensorDataPack.pressure}")
        print(f"Altitude (BME): {self.sensorDataPack.altitude}")
        print(f"Voltage: {self.sensorDataPack.voltage}")
        print(f"Roll: {self.sensorDataPack.roll}")
        print(f"Pitch: {self.sensorDataPack.pitch}")
        print(f"Yaw: {self.sensorDataPack.yaw}")
        print(f"Date and Time: {self.sensorDataPack.dateAndTime}")
        