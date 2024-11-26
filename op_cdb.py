from random import random
import psycopg2
import random
from datetime import datetime, timedelta
from psycopg2 import sql
import time

def connect_cockroachdb(dbname='payments'):
    conn = psycopg2.connect(
        dbname='payments',
        user='root',  # Default user
        password='',
        host='localhost',
        port='26257',
        sslmode='disable'  # Disable SSL for insecure mode
    )
    return conn

def create_database(dbname):
    conn = connect_cockroachdb()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE {dbname}")
    cursor.close()
    conn.close()

def create_tables(conn):
    cursor = conn.cursor()

    # Create accounts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INT PRIMARY KEY DEFAULT unique_rowid(),
        balance NUMERIC(10,2) NOT NULL CHECK (balance >= 0),
        region TEXT NOT NULL
    );
    """)

    # Create payment_transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment_transactions (
        transaction_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
        timestamp TIMESTAMP DEFAULT now(),
        sender_id INT REFERENCES accounts(account_id) ON DELETE CASCADE,
        receiver_id INT REFERENCES accounts(account_id) ON DELETE CASCADE,
        region TEXT NOT NULL
    );
    """)

    conn.commit()
    cursor.close()
    print("Tables created successfully.")


def insert_mock_data(conn):
    cursor = conn.cursor()

    # Insert accounts with manual account_id values
    mock_accounts = [
        (1, 1000.00, 'North America'),
        (2, 850.50, 'Europe'),
        (3, 1450.75, 'Asia'),
        (4, 500.00, 'South America'),
        (5, 1200.20, 'Africa')
    ]

    cursor.executemany(
        "INSERT INTO accounts (account_id, balance, region) VALUES (%s, %s, %s)",
        mock_accounts
    )

    conn.commit()
    cursor.close()
    print("Mock data inserted successfully.")


def process_payment(conn, sender_id, receiver_id, amount, region):
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (sender_id,))
        sender_balance = cursor.fetchone()
        if not sender_balance:
            raise Exception("Sender account does not exist.")
        if sender_balance[0] < amount:
            raise Exception("Insufficient funds.")

        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, sender_id))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, receiver_id))
        cursor.execute("""
        INSERT INTO payment_transactions (amount, sender_id, receiver_id, region)
        VALUES (%s, %s, %s, %s)
        """, (amount, sender_id, receiver_id, region))

        conn.commit()
        print("Payment processed successfully.")

    except Exception as e:
        conn.rollback()
        print(f"Error processing payment: {e}")

    finally:
        cursor.close()

def view_data(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    records = cursor.fetchall()
    cursor.close()
    return records


def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    cursor.close()
    return tables


if __name__ == '__main__':
    DATABASE_NAME='payments'

    #create_database(DATABASE_NAME)
    #print('Database created')

    # Start timing
    start_time = time.time()

    with connect_cockroachdb(DATABASE_NAME) as conn:
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        create_tables(conn)
        insert_mock_data(conn)
        process_payment(conn, sender_id=1, receiver_id=2, amount=100.00, region='North America')
        process_payment(conn, sender_id=1, receiver_id=3, amount=100.00, region='North America')
        process_payment(conn, sender_id=1, receiver_id=2, amount=10000.00, region='North America')
        process_payment(conn, sender_id=10, receiver_id=2, amount=100.00, region='North America')
        process_payment(conn, sender_id=3, receiver_id=1, amount=50.00, region='North America')
        process_payment(conn, sender_id=3, receiver_id=2, amount=10.00, region='North America')
        process_payment(conn, sender_id=1, receiver_id=2, amount=10.00, region='North America')
        process_payment(conn, sender_id=1, receiver_id=2, amount=10.00, region='North America')
        process_payment(conn, sender_id=11, receiver_id=1, amount=100.00, region='North America')
        process_payment(conn, sender_id=2, receiver_id=3, amount=70.00, region='North America')
    # End timing
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - start_time
    print(f"Total time to process 10 payments: {elapsed_time:.2f} seconds")
    # tables = list_tables(conn)
    # print("Tables in the database:", tables)
    # accounts = view_data(conn, 'accounts')
    # print("Accounts table data:")
    # for account in accounts:
    #     print(account)
    # transactions = view_data(conn, 'payment_transactions')
    # print("Payment transactions table data:")
    # for transaction in transactions:
    #     print(transaction)
