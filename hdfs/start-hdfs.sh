#!/bin/bash
# Start HDFS services

# Wait for HDFS to be available
sleep 15

# Create required Hive directories
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/hive/warehouse
$HADOOP_HOME/bin/hdfs dfs -chmod 777 /user/hive/warehouse
$HADOOP_HOME/bin/hdfs dfs -chown hive:hadoop /user/hive/warehouse

# Continue with existing script content