#!/bin/bash
# Script de instalación y configuración de Neo4j para ACAG-P

NEO4J_VERSION="5.12.0"
NEO4J_TAR="neo4j-enterprise-$NEO4J_VERSION-unix.tar.gz"
NEO4J_URL="https://neo4j.com/artifact.php?name=$NEO4J_TAR"

# Descargar e instalar Neo4j Enterprise
wget -O $NEO4J_TAR "$NEO4J_URL"
tar -xf $NEO4J_TAR
sudo mv neo4j-enterprise-$NEO4J_VERSION /usr/local/neo4j

# Crear usuario dedicado
sudo useradd --system --no-create-home --home /usr/local/neo4j neo4j

# Configurar variables de entorno
echo 'export NEO4J_HOME="/usr/local/neo4j"' >> /etc/profile.d/neo4j.sh
echo 'export PATH="$NEO4J_HOME/bin:$PATH"' >> /etc/profile.d/neo4j.sh

# Configuración de memoria y rendimiento
sudo bash -c 'cat > /usr/local/neo4j/conf/neo4j.conf << EOL
# Configuración ACAG-P para Neo4j
server.memory.pagecache.size=2G
server.memory.heap.initial_size=1G
server.memory.heap.max_size=4G
dbms.default_database=acag_knowledge
dbms.security.auth_enabled=true
dbms.logs.query.timeout_logging_enabled=true
dbms.logs.query.threshold=100ms
EOL'

# Establecer permisos
sudo chown -R neo4j:neo4j /usr/local/neo4j
sudo chmod -R 755 /usr/local/neo4j

echo "Neo4j $NEO4J_VERSION instalado y configurado para ACAG-P"