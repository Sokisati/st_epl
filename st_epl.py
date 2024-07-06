from device_file import *

shell = DistantDevice('192.168.33.23',12345,4);
groundStation = DistantDevice('192.168.33.243',12346,10);

#I know it's not distant nor a device but it just fits with the structure
cameraFilter = DistantDevice('127.0.0.1',12347,2);

satellite = Satellite(groundStation,shell,cameraFilter);

satellite.startMainLoop();