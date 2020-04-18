Sensor Platform
Automated AC Service 

0. cd to the folder Sensor_Platform. run all commands from here

1. To start up all services in platform run
./Startup.sh -cluser 
This will start a simple command line interface where the user can give config params for new sensors. 

2. Then add the temperature sensor by executing the commad on a new window
python Sensors/temp_sensor.py Configs/temp_sensor_config.json
A prompt will show up on the simple command line interface to get config details

3. Then start the algorithm automated_ac_service.py
python Algorithms/automated_ac_service.py [NAME OF SENSOR AS GIVEN IN CONFIG]

The prompts should show up on the sensor window after a period of delay(30-60 sec).

