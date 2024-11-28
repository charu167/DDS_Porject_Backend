from decimal import Decimal  # Import Decimal for precise calculations
from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS

# Flask app initialization
app = Flask(__name__)
CORS(app)
# Function to connect to the database
def connect_cockroachdb():
    try:
        connection = psycopg2.connect(
            host="localhost",
            port=26257,
            database="asudb",
            user="charu",
            password="charu123"
        )
        return connection
    except Exception as e:
        raise Exception(f"Error connecting to the database: {e}")

# API endpoint to get all users
@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        conn = connect_cockroachdb()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        user_list = [
            {
                "id": str(user[0]),  # Convert ID to string
                "region": user[1],
                "name": user[2],
                "balance": str(user[3])  # Balance is already a string, ensure consistency
            }
            for user in users
        ]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({"error": f"Error fetching users: {e}"}), 500
    finally:
        if conn:
            conn.close()

            
            

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = connect_cockroachdb()
                conn.autocommit = False  # Start a transaction
                cursor = conn.cursor()

                # Check sender's balance
                cursor.execute(
                    "SELECT balance FROM users WHERE id = %s AND region = %s FOR UPDATE",
                    (data["sender_id"], data["sender_region"]),
                )
                sender_balance = cursor.fetchone()
                if not sender_balance:
                    raise ValueError("Sender does not exist.")

                sender_balance = Decimal(sender_balance[0])  # Ensure this is a Decimal
                amount = Decimal(data["amount"])  # Convert amount to Decimal

                if sender_balance < amount:
                    raise ValueError("Insufficient balance.")

                # Update sender's balance
                cursor.execute(
                    "UPDATE users SET balance = balance - %s WHERE id = %s AND region = %s",
                    (amount, data["sender_id"], data["sender_region"]),
                )

                # Update receiver's balance
                cursor.execute(
                    "UPDATE users SET balance = balance + %s WHERE id = %s AND region = %s",
                    (amount, data["receiver_id"], data["receiver_region"]),
                )

                # Log transaction
                cursor.execute(
                    """
                    INSERT INTO transactions (
                        sender_id, sender_region, receiver_id, receiver_region, amount, description
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        data["sender_id"],
                        data["sender_region"],
                        data["receiver_id"],
                        data["receiver_region"],
                        amount,  # Ensure this is Decimal
                        data["description"],
                    ),
                )

                conn.commit()
                return jsonify({"message": "Transaction processed successfully."})

            except Exception as e:
                conn.rollback()  # Rollback the transaction on error
                if "TransactionRetryWithProtoRefreshError" in str(e):
                    if attempt < max_retries - 1:
                        continue  # Retry the transaction
                    else:
                        raise ValueError("Transaction failed after multiple retries.")
                else:
                    raise e
    except Exception as e:
        return jsonify({"error": f"Error processing transaction: {e}"}), 400
    finally:
        if conn:
            conn.close()



@app.route('/explain_users', methods=['GET'])
def explain_users():
    try:
        conn = connect_cockroachdb()
        cursor = conn.cursor()

        # Get regions from query parameters
        regions = request.args.getlist('regions')  # Accepts regions as a list (e.g., ?regions=us&regions=eu)

        # Construct WHERE clause
        if "all" in regions or not regions:  # If "all" is specified or no region is provided, query all regions
            where_clause = ""
        else:
            placeholders = ', '.join(['%s'] * len(regions))  # Generate placeholders for SQL
            where_clause = f"WHERE region IN ({placeholders})"

        # EXPLAIN ANALYZE query
        query = f"EXPLAIN ANALYZE SELECT * FROM users {where_clause};"
        cursor.execute(query, regions if regions and "all" not in regions else [])
        analysis_result = cursor.fetchall()

        # Extract relevant information
        relevant_keywords = [
            "planning time",
            "execution time",
            "sql nodes",
            "kv nodes",
            "regions",
            "spans"
        ]
        filtered_results = [
            row[0] for row in analysis_result
            if any(keyword in row[0] for keyword in relevant_keywords)
        ]

        return jsonify({
            "message": "Analysis completed.",
            "details": filtered_results
        })

    except Exception as e:
        return jsonify({"error": f"Error running analysis: {e}"}), 500

    finally:
        if conn:
            conn.close()



@app.route('/node_regions', methods=['GET'])
def get_node_regions():
    try:
        conn = connect_cockroachdb()
        cursor = conn.cursor()

        # Query to fetch node ID and region information
        query = """
        SELECT node_id, locality, address 
        FROM crdb_internal.kv_node_status;
        """
        cursor.execute(query)
        nodes = cursor.fetchall()

        # Parse the results into the required format
        node_region_map = []
        for node in nodes:
            node_id = node[0]
            locality = node[1]
            address = node[2]
            
            # Extract region from locality
            region = None
            for part in locality.split(','):
                if 'region=' in part:
                    region = part.split('=')[1]
                    break
            
            # Extract node name from address
            node_name = address.split(':')[0]
            
            node_region_map.append({
                "name": node_name,
                "node_id": node_id,
                "region": region
            })

        return jsonify({
            "message": "Node region mapping retrieved successfully.",
            "nodes": node_region_map
        })

    except Exception as e:
        return jsonify({"error": f"Error retrieving node region mapping: {e}"}), 500

    finally:
        if conn:
            conn.close()



# A simple test route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hello, Flask is working!"})

# Main function to run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
