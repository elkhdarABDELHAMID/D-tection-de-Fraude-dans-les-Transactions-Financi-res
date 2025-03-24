#!/bin/bash

# Make sure no previous instances are running
rm -f /tmp/hive-metastore.pid

# Clear any potentially locked SQLite database
if [ -f /opt/hive/metastore_db/*.lck ]; then
  rm -f /opt/hive/metastore_db/*.lck
fi

# Wait for HDFS to be fully operational
sleep 30

# Start the service
if [ "$SERVICE" = "metastore" ]; then
  exec $HIVE_HOME/bin/hive --service metastore
elif [ "$SERVICE" = "hiveserver2" ]; then
  exec $HIVE_HOME/bin/hiveserver2
fi