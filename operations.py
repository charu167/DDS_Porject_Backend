from random import random
import psycopg2
import random
from datetime import datetime, timedelta
from psycopg2 import sql


def connect_potsgres(dbname='postgres'):
    conn = psycopg2.connect(dbname=dbname, user='postgres', password='Qwerty@12345', host='localhost', port='5432')
    return conn

def create_database(dbname):
    conn = connect_potsgres()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE {dbname}")
    cursor.close()
    conn.close()

# Create tables
def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id SERIAL PRIMARY KEY,
        balance NUMERIC(10,2) NOT NULL CHECK (balance >= 0),
        region TEXT NOT NULL
    );
    """)

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

# Insert mock data
def insert_mock_data(conn):
    cursor = conn.cursor()

    mock_accounts = [
        (1000.00, 'North America'),
        (850.50, 'Europe'),
        (1450.75, 'Asia'),
        (500.00, 'South America'),
        (1200.20, 'Africa')
    ]

    cursor.executemany(
        "INSERT INTO accounts (balance, region) VALUES (%s, %s)",
        mock_accounts
    )

    conn.commit()
    cursor.close()
    print("Mock data inserted successfully.")

# Process payment
def process_payment(conn, sender_id, receiver_id, amount, region):
    cursor = conn.cursor()

    try:
        # Check sender's balance
        cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (sender_id,))
        sender_balance = cursor.fetchone()
        if not sender_balance:
            raise Exception("Sender account does not exist.")
        if sender_balance[0] < amount:
            raise Exception("Insufficient funds.")

        # Deduct amount from sender
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, sender_id))

        # Add amount to receiver
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, receiver_id))

        # Insert transaction record
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

# View data
def view_data(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    records = cursor.fetchall()
    cursor.close()
    return records



if __name__ == '__main__':
    DATABASE_NAME='payments'

    create_database('payments')
    print('database created')

    with connect_potsgres(DATABASE_NAME) as conn:
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        create_tables(conn)

        insert_mock_data(conn)

        process_payment(conn, sender_id=1, receiver_id=2, amount=100.00, region='North America')

        # View data
        # print("Accounts:")
        # print(view_data(conn, 'accounts'))
        # print("\nPayment Transactions:")
        # print(view_data(conn, 'payment_transactions'))

    conn.close()

      





