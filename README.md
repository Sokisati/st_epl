# Documentation

This program is developed by me for TEKNOFEST Model Satellite Project 2024. Keep in mind that some of the problems I solved could have been avoided by using aysnc or multithreaded programming but I didn't had the time to learn those (thank you thermodynamics, differential equations and fluid dynamics) at the time and it would have been very risky to implement something I have just learned in a project like this. I also didn't had anyone I can ask for help or guidance.

Also, keep in mind that while guidebook refers to our main product as "mission payload", I prefer it to call satellite or st for short.

## Task
To sum 25 pages worth of info, flight computer has 4 main tasks:
1) Transmit (and record on micro SD card) camera footage to ground station program. 
2) Apply colored camera filters according to the command transmitted by ground station program.
3) Detach mission payload from its shell.
4) Transmit telemetry data packet to ground station program at 1 Hz.

First and second task are separate programs, so I won't cover them here. If you want to check them out, you can find them in my profile as camera_epl and camera_filter_epl.

Fourth task will take like %90 of this readme file, so let's get the third task out of the way.

## Detachment-lock
Basically, our model satellite consists of 2 parts: Mission payload and shell. As you may have guessed, big guns are in mission payload. 
You can see our detachment mechanism below, it's connected to a servo motor. When program calls detach method (belonging to servo object), servo angle is set to detachment angle (which can be changed from parameter file).

![](https://github.com/Sokisati/st_epl/blob/master/images/detach.png)

Detachment method is called automatically if satellite status is 3 (status 3 means it's time to say goodbye to mama) or manually if ground station says so.
And... that's about it for this task.

## Telemetry data
Telemetry data is a data packet that consist of many things like transmission time, packet number, satellite status, error code list, temperature, IoT data, battery voltage, team number etc. It's content and transmission frequency is stated in guidebook. 
It's got 21 elements inside, but we can group them like in the tree below (this tree doesn't exist in the program, it's just a neat representation):

![](https://github.com/Sokisati/st_epl/blob/master/images/data_tree.jpg)

### Non-native data
Hold on, what do you mean non-native data? All of these are supposed to be transmitted to ground station program but we need data from ground station data like IoT and color filter command. Sounds awfully familiar to chicken-egg problem, right?
Before I transmit the telemetry data packet, I need to get data from shell and ground station (all the other data are already pretransmitted, hence the name "native") but synchronization is the key word here. 
If I program the shell and ground station to transmit their data at a fixed rate, it will cause numerous problems. What if flight computer is dealing with a problem and needs 3 seconds to handle it? What will happen if ground station or shell data doesn't arrive? 
That's why our mission payloads flight computer (Raspberry Pi Zero 2W) first attempts to transmit a string command "SEND_DATA" to shells flight computer (ESP32) and if it fails to do so, it doesn't wait for an answer. If it can transmit command successfully, it waits for the incoming respond. Then, same procedure applies to ground station.

![](https://github.com/Sokisati/st_epl/blob/master/images/tcp.gif)

Another advantage of this method is that I can change transmission frequency just by changing sleeping time in mission payload program.

I used TCP/IP protocol for this. This enables me to know whether there is an active/healthy connection to target socket by setting a timeout.
#### Sleep
Operations like reading sensor data, transmitting data, waiting for responses, and handling exceptions all take variable time depending on CPU usage, temperature, and RAM usage. Therefore, instead of using a simplistic `time.sleep(1)`, I implemented an algorithm that waits until the system time changes. This method helps mitigate the issue of time drift.

### Involves both
Now, these are data types that needs data from both native and non-native sources. Altitude difference is straightforward:  |Shell alt - Mission payload alt|
Status and error code list however, is not. Error code list is dependent on status so let's start with it.

### Status
Determining the status of the satellite is one of the most critical tasks for the flight computer. According to the guidebook, there are six defined statuses, each representing a different phase of the mission:

- **0 = Awaiting flight:** The satellite is on the ground, waiting for launch.
- **1 = Ascent:** The satellite has been launched and is ascending.
- **2 = Model satellite descent:** The satellite has reached its peak altitude and is now descending.
- **3 = Detachment:** The mission payload (st) is ready to separate from the shell.
- **4 = Mission payload descent:** The mission payload has detached and is descending independently.
- **5 = Landed and awaiting rescue:** The mission payload has landed and is awaiting retrieval.

To determine these statuses, the program monitors various parameters such as altitude, altitude difference between the mission payload and the shell, and other environment-specific conditions.

#### How Status Changes Work

The `SatelliteStatusJudge` class handles the logic for updating the satellite's status based on real-time telemetry data. Here's a breakdown of how each status is determined:

1. **Awaiting Flight (Status 0):** The satellite remains in this status until both the altitude reaches a minimum threshold (`minAltitudeForFlightAssumption`) and consecutive ascent conditions are detected. If these conditions are met, the status changes to Ascent (1).
    
2. **Ascent (Status 1):** During ascent, the program continuously checks for descent conditions. If it detects a series of decreasing altitudes that exceed a defined measurement deviation, the status changes to Descent (2).
    
3. **Descent (Status 2):** As the satellite descends, it checks if the altitude falls below a predefined detachment altitude (`detachmentAltitude`). When this happens, the status changes to Detachment (3).
    
4. **Detachment (Status 3):** In this phase, the flight computer checks if the mission payload should detach from the shell by monitoring the altitude difference between the mission payload and the shell. If the altitude difference exceeds a set threshold (`detachmentDifference`), or the shell sends a detachment command, the status changes to Mission Payload Descent (4). Alternatively, if the system detects landing conditions (minimal altitude variation over a certain period), it will directly transition to Landed (5).
    
5. **Mission Payload Descent (Status 4):** After detachment, the mission payload is on its own. The system monitors for landing conditions. If the payload's altitude falls below a minimum landing altitude (`minAltitudeForLandAssumption`) or if the landing condition (`checkForLand()`) is met, the status changes to Landed (5).
    
6. **Landed and Awaiting Rescue (Status 5):** The final status indicates that the mission payload has safely landed and is awaiting recovery. The program will stop checking for further status updates.
