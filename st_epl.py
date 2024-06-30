from device_file import *

shell = DistantDevice('127.0.0.1',12345,4);
groundStation = DistantDevice('127.0.0.1',12346,10);

#I know it's not distant nor a device but it just fits with the structure
cameraFilter = DistantDevice('127.0.0.1',12347,2);

satellite = Satellite(groundStation,shell,cameraFilter);

satellite.startMainLoop();