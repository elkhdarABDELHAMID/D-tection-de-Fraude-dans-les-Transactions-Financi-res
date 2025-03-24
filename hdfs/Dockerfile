FROM bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8

# Remplacer les sources de paquets pour utiliser le dépôt d'archive Debian
RUN echo "deb http://archive.debian.org/debian stretch main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security stretch/updates main" >> /etc/apt/sources.list

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de configuration
COPY hdfs-site.xml /opt/hadoop/etc/hadoop/hdfs-site.xml
COPY core-site.xml /opt/hadoop/etc/hadoop/core-site.xml

# Script pour démarrer le NameNode ou le DataNode
COPY start-hdfs.sh /start-hdfs.sh
RUN chmod +x /start-hdfs.sh

CMD ["/start-hdfs.sh"]