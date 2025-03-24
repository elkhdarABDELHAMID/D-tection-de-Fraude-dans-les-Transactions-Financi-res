from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from hdfs import InsecureClient
import json
import os
from pyhive import hive
import logging

# Configurer le logger pour Airflow
logger = logging.getLogger("airflow.task")

# Fonction pour créer les répertoires dans HDFS
def create_hdfs_directories():
    client = InsecureClient('http://fraud-detection-docker-hdfs-namenode-1:9870', user='hive')
    directories = [
        '/fraud_detection/transactions',
        '/fraud_detection/customers',
        '/fraud_detection/external_data'
    ]
    for directory in directories:
        try:
            client.makedirs(directory, permission=755)
            logger.info(f"Répertoire {directory} créé avec succès dans HDFS.")
        except Exception as e:
            logger.error(f"Erreur lors de la création du répertoire {directory} : {e}")
            raise

# Fonction pour récupérer les données depuis l'API et les sauvegarder localement
def fetch_data():
    endpoints = {
        "/api/transactions": "transactions.json",
        "/api/customers": "customers.json",
        "/api/externalData": "external_data.json"
    }
    
    os.makedirs("/tmp", exist_ok=True)
    
    for endpoint, filename in endpoints.items():
        try:
            url = f"http://fraud-detection-docker-api-1:5000{endpoint}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            local_path = f"/tmp/{filename}"
            with open(local_path, 'w') as f:
                json.dump(data, f)
            logger.info(f"Données de {endpoint} sauvegardées dans {local_path}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération des données de {endpoint} : {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données de {endpoint} dans {local_path} : {e}")
            raise

# Fonction pour uploader les fichiers dans HDFS
def store_data():
    client = InsecureClient('http://fraud-detection-docker-hdfs-namenode-1:9870', user='hive')
    files_to_upload = [
        ("/tmp/transactions.json", "/fraud_detection/transactions/transactions.json"),
        ("/tmp/customers.json", "/fraud_detection/customers/customers.json"),
        ("/tmp/external_data.json", "/fraud_detection/external_data/external_data.json")
    ]
    
    for local_path, hdfs_path in files_to_upload:
        try:
            client.upload(hdfs_path, local_path, overwrite=True)
            logger.info(f"Fichier {local_path} uploadé avec succès vers {hdfs_path} dans HDFS.")
        except Exception as e:
            logger.error(f"Erreur lors de l'upload du fichier {local_path} vers {hdfs_path} : {e}")
            raise

# Fonction pour exécuter une requête Hive et détecter les fraudes
def detect_fraud():
    try:
        # Connexion à Hive
        conn = hive.connect(host='testprojetairflow-hive-server-1', port=10000, database='fraud_detection')
        cursor = conn.cursor()

        # Créer une base de données si elle n'existe pas
        cursor.execute("CREATE DATABASE IF NOT EXISTS fraud_detection")
        cursor.execute("USE fraud_detection")

        # Créer les tables si elles n'existent pas
        cursor.execute("""
        CREATE EXTERNAL TABLE IF NOT EXISTS transactions (
            transaction_id STRING,
            customer_id STRING,
            amount DOUBLE,
            timestamp STRING
        )
        ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
        STORED AS TEXTFILE
        LOCATION '/fraud_detection/transactions'
        """)

        cursor.execute("""
        CREATE EXTERNAL TABLE IF NOT EXISTS customers (
            customer_id STRING,
            name STRING,
            email STRING
        )
        ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
        STORED AS TEXTFILE
        LOCATION '/fraud_detection/customers'
        """)

        cursor.execute("""
        CREATE EXTERNAL TABLE IF NOT EXISTS external_data (
            customer_id STRING,
            credit_score INT,
            location STRING
        )
        ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
        STORED AS TEXTFILE
        LOCATION '/fraud_detection/external_data'
        """)

        # Requête pour détecter les transactions suspectes
        query = """
        SELECT t.transaction_id, t.customer_id, t.amount, t.timestamp, c.name, e.credit_score
        FROM transactions t
        JOIN customers c ON t.customer_id = c.customer_id
        JOIN external_data e ON t.customer_id = e.customer_id
        WHERE t.amount > 150 AND e.credit_score < 650
        """
        
        cursor.execute(query)
        results = cursor.fetchall()

        # Loguer les résultats
        if results:
            for row in results:
                logger.info(f"Transaction suspecte : {row}")
        else:
            logger.info("Aucune transaction suspecte détectée.")

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Erreur lors de la détection des fraudes avec Hive : {e}")
        raise

# Arguments par défaut du DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définir le DAG
with DAG(
    'fraud_detection_workflow',
    default_args=default_args,
    description='Collecte, stockage et détection de fraudes',
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2025, 3, 19),
    catchup=False,
) as dag:

    # Tâche pour créer les répertoires dans HDFS
    create_dirs_task = PythonOperator(
        task_id='create_hdfs_directories',
        python_callable=create_hdfs_directories,
    )

    # Tâche 1 : Récupérer les données et les sauvegarder localement
    fetch_data_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data,
    )

    # Tâche 2 : Stocker les données dans HDFS
    store_data_task = PythonOperator(
        task_id='store_data',
        python_callable=store_data,
    )

    # Tâche 3 : Détecter les fraudes avec Hive
    detect_fraud_task = PythonOperator(
        task_id='detect_fraud',
        python_callable=detect_fraud,
    )

    # Définir les dépendances
    create_dirs_task >> fetch_data_task >> store_data_task >> detect_fraud_task