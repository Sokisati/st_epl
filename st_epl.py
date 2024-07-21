from device_file import *

shell = DistantDevice(mp.shellIp,mp.shellPort,mp.shellTimeout);
groundStation = DistantDevice(mp.groundStationIp,mp.groundStationPort,mp.groundStationTimeout);

#I know it's not distant nor a device but it just fits with the structure
cameraFilter = DistantDevice(mp.cameraFilterIp,mp.cameraFilterPort,mp.cameraFilterTimeout);

satellite = Satellite(groundStation,shell,cameraFilter);

satellite.startMainLoop();