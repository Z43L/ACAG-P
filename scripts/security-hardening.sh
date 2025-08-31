#!/bin/bash
# Script de hardening de seguridad para ACAG-P

echo "🔒 Aplicando medidas de seguridad..."

# Configurar firewall
ufw allow 8000/tcp
ufw allow 7474/tcp
ufw allow 7687/tcp
ufw allow 6379/tcp
ufw --force enable

# Configurar permisos de archivos
chmod 600 .env.production
chmod 600 config/*_password.txt
chmod 750 scripts/*.sh

# Configurar Docker security
cat > /etc/docker/daemon.json << EOF
{
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
EOF

# Reiniciar Docker
systemctl restart docker

# Configurar log rotation
cat > /etc/logrotate.d/acag << EOF
/var/log/acag/*.log {
    daily
    rotate 30
    missingok
    notifempty
    compress
    delaycompress
    copytruncate
}
EOF

echo "✅ Hardening de seguridad completado"