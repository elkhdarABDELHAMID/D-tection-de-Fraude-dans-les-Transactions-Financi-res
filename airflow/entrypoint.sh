#!/bin/bash
sleep 60  # Attendre que Hive soit prêt
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
airflow webserver & airflow scheduler
