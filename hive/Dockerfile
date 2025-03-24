FROM apache/hive:4.0.0

USER root

RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    wget \
    sqlite3 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create directory and add SQLite JDBC driver
RUN mkdir -p /opt/hive/lib && \
    wget -P /opt/hive/lib https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.46.0.1/sqlite-jdbc-3.46.0.1.jar && \
    chmod -R 755 /opt/hive/lib

# Create schema file directory
RUN mkdir -p /opt/hive/conf

# Copy files with explicit file creation
COPY entrypoint.sh /entrypoint.sh
COPY hive-schema.sql /opt/hive/conf/hive-schema.sql 

# Set permissions explicitly
RUN chmod +x /entrypoint.sh && \
    chown -R hive:hive /opt/hive

USER hive

ENTRYPOINT ["/entrypoint.sh"]