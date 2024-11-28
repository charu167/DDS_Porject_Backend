### README

# Distributed Payment Processing System

## Overview

This project demonstrates a **Distributed Payment Processing System** that ensures consistent, scalable, and reliable financial transactions across multiple regions. It leverages **CockroachDB** for distributed database management, **Flask** for backend APIs, and **Next.js** for a user-friendly interface. The system supports concurrent transactions, infrastructure insights, and query performance analysis while ensuring fault tolerance and data consistency.

---

## Features

1. **Payment Processing**: Reliable transactions with automatic conflict resolution using CockroachDB’s serializable isolation.
2. **User Management**: Real-time access to user data, including balances and regional details.
3. **Infrastructure Insights**: Visual mapping of database nodes to regions for operational transparency.
4. **Query Analysis**: Detailed performance insights using `EXPLAIN ANALYZE`.

---

## Technologies Used

- **CockroachDB**: Distributed SQL database for scalability and high availability.
- **Flask**: Backend framework for RESTful API development.
- **Next.js**: Modern frontend framework for intuitive UI design.
- **Docker**: Containerization for deploying and managing multi-node clusters.

---

## Highlights

- Handles concurrent financial transactions with robust conflict resolution.
- Provides real-time system insights and performance metrics.
- Scalable and fault-tolerant architecture for distributed environments.

---

## How to Run

### **Backend Setup**

1. **Clone the Repository**  
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Install Required Tools**  
   Ensure the following tools are installed on your system:
   - **Docker**  
   - **Python**

3. **Generate CockroachDB Certificates**  
   - Navigate to the `certificates` folder:
     ```bash
     cd certificates
     ```
   - Provide execute permissions to the `generate-certs.sh` file:
     ```bash
     chmod +x generate-certs.sh
     ```
   - Run the script to generate the certificates:
     ```bash
     ./generate-certs.sh
     ```

4. **Set Up CockroachDB Cluster**  
   - Go back to the root directory:
     ```bash
     cd ..
     ```
   - Save your CockroachDB license key in an `.env` file in the root folder:
     ```
     LICENSE_KEY=<your_cockroachdb_license_key>
     ```
   - Provide execute permissions to the `run.sh` file:
     ```bash
     chmod +x run.sh
     ```
   - Start the CockroachDB cluster and set up the database:
     ```bash
     ./run.sh
     ```

5. **Start the Backend Server**  
   - Navigate to the `backend` folder:
     ```bash
     cd backend
     ```
   - Ensure the following dependencies are installed in your Python environment:
     ```python
     from decimal import Decimal  # Import Decimal for precise calculations
     from flask import Flask, jsonify, request
     import psycopg2
     from flask_cors import CORS
     ```
   - Start the server:
     ```bash
     python app.py
     ```
   - The server will start on `http://127.0.0.1:5000`.

---

Let me know if you need further updates or additional instructions!