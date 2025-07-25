#!/bin/bash
# Encrypted PostgreSQL database backup script
# Usage: ./backup_db_encrypted.sh <db_url> <backup_file.sql.enc> <encryption_password>
# Example: ./backup_db_encrypted.sh "postgresql://user:pass@host:port/db" backup.sql.enc mypassword

set -e

DB_URL="$1"
BACKUP_FILE="$2"
PASSWORD="$3"

if [ -z "$DB_URL" ] || [ -z "$BACKUP_FILE" ] || [ -z "$PASSWORD" ]; then
  echo "Usage: $0 <db_url> <backup_file.sql.enc> <encryption_password>"
  exit 1
fi

# Export the database and encrypt it with OpenSSL AES-256
PGPASSWORD=$(echo $DB_URL | sed -n 's/.*:\/\/(.*):(.*)@.*/\2/p') \
pg_dump "$DB_URL" | openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"$PASSWORD" -out "$BACKUP_FILE"

echo "Encrypted backup saved to $BACKUP_FILE"
