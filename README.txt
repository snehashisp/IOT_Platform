Sensor Platform
Automated AC Service 

prerequisite:
cd to the folder Sensor_Platform. run all commands from here
python version used is python3

1. To start up all services in platform run
./Startup.sh -cluser 
This will start a simple command line interface where the user can give config params for new sensors. 

2. Then add the temperature sensor by executing the commad on a new window
python Sensors/temp_sensor.py Configs/temp_sensor_config.json
A prompt will show up on the simple command line interface to get config details

3. Then start the algorithm automated_ac_service.py
python Algorithms/automated_ac_service.py [NAME OF SENSOR AS GIVEN IN CONFIG]

The prompts should show up on the sensor window after a period of delay(30-60 sec).


=============================================

Detail steps for fire alarm service.

1. For this do the prerequisites and steps 1, 2 as previous.
2. Add the alarm sensor as well.
python Sensors/alarm.py Configs/alarm_config.json
In the prompt for the alarm sensor in the command line user interface. Add the details of the alarm sensor. Make sure to give the location of the sensor as the same location as the temperature sensor.
3. Start the algortihm for fire service
python Sensors/fire_alarm_service.py [NAME OF THE TEMP SENSOR AS GIVEN IN CONFIG]






