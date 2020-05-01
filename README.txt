Sensor Platform
Automated AC Service 

Prerequisite:

* cd to the folder Sensor_Platform. run all commands from here
* python version used is python3
* put the latest version of kakfa as the folder 'kafka' in the same directory 
* make a empty new folder named 'log'
* comment the CLASSPATH variable in ~/.bashrc if there is some error.

* KAFKA CONNECT SETUP
	** Add mongo plugins if required(i.e.,if it is still not running)[add detail][Download plugins from https://search.maven.org/remotecontent?filepath=org/mongodb/kafka/mongo-kafka-connect/1.1.0/mongo-kafka-connect-1.1.0-all.jar , 
	and save to /usr/local/share/kafka/plugins/ (Create the directory if required, if this path doesn't exist)]
	** Go to Kafka, config, connect-standalone.properties,  uncomment "plugin.path=/usr/local/share/java,/usr/local/share/kafka/plugins,/opt/connectors,"

* Export the environt variable as export PYTHONPATH="$PYTHONPATH:[FULL PATH OF THE FOLDER WHERE IOT_PLATFORM IS STORED]"

-----

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

Detailed steps for fire alarm service.

1. For this do the prerequisites and steps 1, 2 as previous.
2. Add the alarm sensor as well.
python Sensors/alarm.py Configs/alarm_config.json
In the prompt for the alarm sensor in the command line user interface. Add the details of the alarm sensor. Make sure to give the location of the sensor as the same location as the temperature sensor.
3. Start the algortihm for fire service
python Sensors/fire_alarm_service.py [NAME OF THE TEMP SENSOR AS GIVEN IN CONFIG]






