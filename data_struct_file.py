class DataPack:
    def __init__(self, packetNumber, stStatus, errorCodeList, transmissionTime, satellitePressure, shellPressure,satelliteAltitude,shellAltitude,altitudeDifference,
                 descendSpeed, temperature, batteryVoltage, gpsLat, gpsLong, gpsAlt, pitch, roll, yaw, filterCommandList, iotData, teamNumber):
        self.packetNumber = packetNumber
        self.stStatus = stStatus
        self.errorCodeList = errorCodeList
        self.transmissionTime = transmissionTime
        self.satellitePressure = satellitePressure
        self.shellPressure = shellPressure
        self.satelliteAltitude = satelliteAltitude
        self.shellAltitude = shellAltitude
        self.altitudeDifference = altitudeDifference
        self.descendSpeed = descendSpeed
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
