#!/bin/bash
printf "This is a quick Startup Script to start all the required components\nKafka is provided along with the distribution\nMongodb is required to be installed in the system\nAll services use their default ports\nThis script requires curl and systemctl to be present in the system to run\n"
echo "================================================================================"

logfile=logs/log.txt
zookeeper_logs=logs/zookeeper_logs.txt
kafka_logs=logs/kafka_logs.txt
kafka_connect_logs=logs/connect_logs.txt
manager_logs=logs/manager
gateway_logs=logs/gateway.txt
python_exec=python


echo "Stopping Zookeeper and Kakfa if running" | tee $logfile
sh kafka/bin/zookeeper-server-stop.sh >>$logfile 2>&1 
sh kafka/bin/kafka-server-stop.sh >>$logfile 2>&1
echo "Starting Services" | tee $logfile
sh kafka/bin/zookeeper-server-start.sh kafka/config/zookeeper.properties >> $zookeeper_logs 2>&1 &
pstatus=$!
sleep 5
if ps -p $pstatus > /dev/null
then
	echo -n "Zookeeper Started PId " | tee -a $logfile
	echo $! | tee -a $logfile
else
	echo "Failed to start zookeeper" | tee -a $logfile
fi

sh kafka/bin/kafka-server-start.sh kafka/config/server.properties >> $kafka_logs 2>&1 &
pstatus=$!
sleep 10
if ps -p $pstatus > /dev/null
then
    echo -n "Kafka Started PId " | tee -a $logfile
    echo $! | tee -a $logfile
else
    echo "Failed to start Kafka" | tee $logfile
fi

mongo_status=`systemctl is-active mongod`
if [[ $mongo_status == "inactive" ]]
then
    mongo_status=`systemctl start mongod`
    if [[ $mongo_status == "inactive" ]]
    then
        echo "Mongo db service cannot be started" | tee -a $logfile
    else
        echo "Mongo db service started" | tee -a $logfile
    fi
else
    echo "Mongo Service Running"
fi


kafka_connect_status=`curl -s -o /dev/null -I -w "%{http_code}" localhost:8083`
if [ $kafka_connect_status -eq 200 ]
then
	echo "Kafka Connect Runnning" | tee -a $logfile
else
	sh kafka/bin/connect-standalone.sh kafka/config/connect-standalone.properties Configs/MongoSinkConnector.properties >> $kafka_connect_logs 2>&1 &
	pstatus=$!
	sleep 10
	if ps -p $pstatus > /dev/null
	then
    	echo -n "Kafka Connect Started PId " | tee -a $logfile
	    echo $! | tee -a $logfile
	else
    	echo "Failed to start Kafka Connecet" | tee -a $logfile
	fi
fi


start_cluser=0
managers=2
if [[ $# -eq 1 ]]
then
	if [[ $1 == "-cluser" ]]
	then
		start_cluser=1
	else 
		managers=$1
	fi
elif [[ $# -eq 2 ]]
then
	start_cluser=1
	if [[ $1 == "-cluser" ]]
	then
		managers=$2
	else
		managers=$1
	fi
fi

export PYTHONPATH="$PYTHONPATH:$PWD"
echo "Starting Sensor Managers"
while [[ $managers -gt 0 ]]
do
	manager_logfile="$manager_logs$managers.txt"
	echo "============================================================" >> $manager_logfile
	$python_exec platform/Manager.py >> $manager_logfile 2>&1 &
	managers=$(($managers - 1))
done

echo "Starting Simulated Gateway"
echo "============================================================" >> $gateway_logs
python platform/gateway.py >> $gateway_logs 2>&1 &

if [[ $start_cluser -eq 1 ]]
then
	echo "============================================================"
	$python_exec Utils/SimpleCLUser.py 
fi	
