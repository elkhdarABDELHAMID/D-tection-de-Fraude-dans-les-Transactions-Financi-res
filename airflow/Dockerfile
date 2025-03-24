FROM apache/airflow:2.8.1-python3.8

# Installer les dépendances système pour Kerberos et un compilateur C
USER root
RUN apt-get update && apt-get install -y \
    libkrb5-dev \
    krb5-user \
    libgssapi-krb5-2 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt et installer les dépendances Python
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt