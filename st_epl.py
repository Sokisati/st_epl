from satellite_file import *
import sys

shell = DistantDevice(mp.shellIp,mp.shellPort,mp.shellTimeout);
groundStation = DistantDevice(mp.groundStationIp,mp.groundStationPort,mp.groundStationTimeout);

#I know it's not distant nor a device but it just fits with the structure
cameraFilter = DistantDevice(mp.cameraFilterIp,mp.cameraFilterPort,mp.cameraFilterTimeout);

satellite = Satellite(groundStation,shell,cameraFilter);

if (len(sys.argv)==2)and(sys.argv[1]=='sim'):
    satellite.simulation = True

satellite.startMainLoop();