#!/bin/bash

if [ "$SERVICE" = "metastore" ]; then
  if ps -ef | grep -v grep | grep -q "org.apache.hadoop.hive.metastore.HiveMetaStore"; then
    exit 0
  else
    exit 1
  fi
elif [ "$SERVICE" = "hiveserver2" ]; then
  if ps -ef | grep -v grep | grep -q "org.apache.hive.service.server.HiveServer2"; then
    exit 0
  else
    exit 1
  fi
fi