# DDS_Porject
Payment System using CockroachDB as the Distributed Database

# Distributed Payment Processing System

This repository contains the code for the Distributed Payment Processing System project, which demonstrates a fault-tolerant, geo-partitioned payment processing application using CockroachDB, Flask, and Docker.

## **Project Structure**

- `backend/`: Contains the Flask application code.
- `database/`: Contains SQL scripts for database schema, data insertion, and zone configurations.
- `docker/`: Contains Docker configuration files for setting up the CockroachDB cluster.
- `.gitignore`: Specifies intentionally untracked files to ignore.
- `README.md`: Project documentation.

## **Getting Started**

### **Prerequisites**

- Docker and Docker Compose installed.
- Python 3.8+ installed.
- `psycopg2` and `Flask` Python packages.

### **Setup**

#### **Database**

1. Navigate to the `docker/` directory and start the CockroachDB cluster:

   ```bash
   cd docker/
   docker-compose up -d
