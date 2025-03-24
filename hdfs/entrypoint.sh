#!/bin/bash
# Formater le NameNode si nécessaire
if [ ! -d "/hadoop/dfs/name/current" ]; then
    hdfs namenode -format
fi

# Démarrer le NameNode
hdfs namenode
