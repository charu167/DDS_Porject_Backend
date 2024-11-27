from decimal import Decimal
import psycopg2
from psycopg2 import sql

def connect_cockroachdb(dbname='asudb'):
    host = "localhost"  
    port = 26257        
    database = dbname   
    user = "charu"       
    password = "charu123"       

    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    return connection
   

def get_accounts():
    conn = connect_cockroachdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users;")
    accounts = cursor.fetchall()
    conn.close()
    return accounts

def get_transactions():
    conn = connect_cockroachdb()
    cursor = conn.cursor()
    # Assuming the column storing the timestamp is named 'timestamp'
    cursor.execute("SELECT * FROM payment_transactions ORDER BY timestamp DESC")
    transactions = cursor.fetchall()
    conn.close()
    return transactions


def process_transaction(sender_id, sender_region, receiver_id, receiver_region, amount, description):
    try:
        # Establish database connection
        conn = psycopg2.connect(
            host="localhost",
            port=26257,
            database="asudb",
            user="charu",
            password="charu123"
        )
        conn.autocommit = False  # Enable transaction management
        cursor = conn.cursor()

        # Check if sender exists and has sufficient balance
        cursor.execute(
            """
            SELECT balance FROM users 
            WHERE id = %s AND region = %s;
            """,
            (sender_id, sender_region)
        )
        sender_data = cursor.fetchone()
        if not sender_data:
            raise ValueError("Sender does not exist.")
        sender_balance = sender_data[0]
        if sender_balance < amount:
            raise ValueError("Insufficient balance for sender.")

        # Check if receiver exists
        cursor.execute(
            """
            SELECT id FROM users 
            WHERE id = %s AND region = %s;
            """,
            (receiver_id, receiver_region)
        )
        if not cursor.fetchone():
            raise ValueError("Receiver does not exist.")

        # Update sender's balance
        cursor.execute(
            """
            UPDATE users 
            SET balance = balance - %s 
            WHERE id = %s AND region = %s;
            """,
            (amount, sender_id, sender_region)
        )

        # Update receiver's balance
        cursor.execute(
            """
            UPDATE users 
            SET balance = balance + %s 
            WHERE id = %s AND region = %s;
            """,
            (amount, receiver_id, receiver_region)
        )

        # Insert transaction record
        cursor.execute(
            """
            INSERT INTO transactions (
                sender_id, sender_region, receiver_id, receiver_region, amount, description
            ) VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (sender_id, sender_region, receiver_id, receiver_region, amount, description)
        )

        # Commit the transaction
        conn.commit()
        print("Transaction processed successfully.")

    except ValueError as ve:
        conn.rollback()  # Rollback transaction in case of validation error
        print(f"Transaction failed: {ve}")

    except Exception as e:
        conn.rollback()  # Rollback transaction for any other errors
        print(f"Error processing transaction: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
