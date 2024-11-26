#!/bin/bash

# -----------------------------------------------------------------------------
# Script to initialize a CockroachDB cluster using Docker Compose.
# - Starts the CockroachDB cluster using Docker Compose
# - Applies initial cluster settings (e.g., license, organization)
# - Runs an SQL initialization file for database setup
# -----------------------------------------------------------------------------

# Load environment variables
echo "Loading environment variables from .env file..."
source .env

# Start Docker Compose services
echo "Starting Docker Compose services..."
docker-compose up -d

# Allow some time for services to initialize
echo "Waiting for services to start..."
sleep 10
echo "Services are now ready."

# Initialize the CockroachDB cluster
echo "Initializing CockroachDB cluster..."
docker exec -it eu1 cockroach init --certs-dir=/cockroach/certs --host=eu1
if [ $? -ne 0 ]; then
  echo "Cluster initialization failed. Exiting."
  exit 1
fi
echo "Cluster initialization completed."

# Apply CockroachDB enterprise license and organization settings
echo "Applying CockroachDB license and organization settings..."
docker exec -it eu1 cockroach sql --certs-dir=/cockroach/certs --host=eu1 -e "
  SET CLUSTER SETTING enterprise.license = '$COCKROACH_LICENSE';
  SET CLUSTER SETTING cluster.organization = '';
"
if [ $? -ne 0 ]; then
  echo "Failed to apply CockroachDB settings. Exiting."
  exit 1
fi
echo "CockroachDB settings applied successfully."

# Execute the SQL initialization file
echo "Executing SQL initialization script..."
docker exec -i eu1 cockroach sql --certs-dir=/cockroach/certs --host=eu1 < ./init.sql
if [ $? -ne 0 ]; then
  echo "SQL initialization failed. Exiting."
  exit 1
fi
echo "SQL initialization completed successfully."

# Completion message
echo "CockroachDB cluster setup is complete. Services are running."

# -----------------------------------------------------------------------------
# End of Script
# -----------------------------------------------------------------------------
