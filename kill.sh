#!/bin/bash

# -----------------------------------------------------------------------------
# Script to shut down the CockroachDB cluster and clean up resources.
# - Stops all Docker Compose services
# - Removes all associated volumes to ensure a clean slate for future runs
# -----------------------------------------------------------------------------

# Stop and remove all Docker Compose services along with volumes
echo "Stopping and removing Docker Compose services with volumes..."
docker-compose down -v
if [ $? -ne 0 ]; then
  echo "Failed to shut down Docker Compose services. Exiting."
  exit 1
fi
echo "Docker Compose services stopped and volumes removed successfully."

# Completion message
echo "CockroachDB cluster has been shut down and cleaned up."

# -----------------------------------------------------------------------------
# End of Script
# -----------------------------------------------------------------------------
