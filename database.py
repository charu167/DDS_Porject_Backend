import psycopg2
from psycopg2 import sql

def connect_cockroachdb(dbname='payments'):
    conn = psycopg2.connect(
        dbname=dbname,
        user='root',
        password='',
        host='localhost',
        port='26257',
        sslmode='disable'
    )
    return conn

def get_accounts():
    conn = connect_cockroachdb()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    conn.close()
    return accounts

# def get_transactions():
#     conn = connect_cockroachdb()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM payment_transactions")
#     transactions = cursor.fetchall()
#     conn.close()
#     return transactions


def get_transactions():
    conn = connect_cockroachdb()
    cursor = conn.cursor()
    # Assuming the column storing the timestamp is named 'timestamp'
    cursor.execute("SELECT * FROM payment_transactions ORDER BY timestamp DESC")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

from decimal import Decimal



# def process_payment(sender_id, receiver_id, amount, region):
#     conn = connect_cockroachdb()  # Ensure the connection is created here
#     cursor = conn.cursor()

#     try:
#         cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (sender_id,))
#         sender_balance = cursor.fetchone()

#         if not sender_balance:
#             raise Exception("Sender account does not exist.")

#         # Convert amount to Decimal for proper comparison
#         amount = Decimal(amount)

#         if sender_balance[0] < amount:
#             raise Exception("Insufficient funds.")

#         cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, sender_id))
#         cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, receiver_id))
#         cursor.execute("""
#         INSERT INTO payment_transactions (amount, sender_id, receiver_id, region)
#         VALUES (%s, %s, %s, %s)
#         """, (amount, sender_id, receiver_id, region))

#         conn.commit()
#         return {"message": "Payment processed successfully."}

#     except Exception as e:
#         conn.rollback()
#         return {"error": str(e)}

#     finally:
#         cursor.close()
#         conn.close()

def process_payment(sender_id, receiver_id, amount, region):
    conn = connect_cockroachdb()
    cursor = conn.cursor()

    try:
        # Fetch sender's balance
        cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (sender_id,))
        sender_balance = cursor.fetchone()

        if not sender_balance:
            return {"status": "error", "message": "Sender account does not exist."}

        from decimal import Decimal
        amount = Decimal(amount)

        if sender_balance[0] < amount:
            return {"status": "error", "message": "Insufficient funds."}

        # Process payment
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, sender_id))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, receiver_id))
        cursor.execute("""
        INSERT INTO payment_transactions (amount, sender_id, receiver_id, region)
        VALUES (%s, %s, %s, %s)
        """, (amount, sender_id, receiver_id, region))

        conn.commit()
        return {"status": "success", "message": "Payment processed successfully."}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        cursor.close()
        conn.close()
