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
    required_fields = ['sender_id', 'sender_region', 'receiver_id', 'receiver_region', 'amount', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = connect_cockroachdb()
        conn.autocommit = False  # Enable transaction management
        cursor = conn.cursor()

        # Convert the input amount to Decimal
        amount = Decimal(data['amount'])

        # Check if sender exists and has sufficient balance
        cursor.execute(
            """
            SELECT balance FROM users 
            WHERE id = %s AND region = %s;
            """,
            (data['sender_id'], data['sender_region'])
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
            (data['receiver_id'], data['receiver_region'])
        )
        if not cursor.fetchone():
            raise ValueError("Receiver does not exist.")

        # Perform transaction: Update balances and record transaction
        cursor.execute(
            """
            UPDATE users 
            SET balance = balance - %s 
            WHERE id = %s AND region = %s;
            """,
            (amount, data['sender_id'], data['sender_region'])
        )
        cursor.execute(
            """
            UPDATE users 
            SET balance = balance + %s 
            WHERE id = %s AND region = %s;
            """,
            (amount, data['receiver_id'], data['receiver_region'])
        )
        cursor.execute(
            """
            INSERT INTO transactions (
                sender_id, sender_region, receiver_id, receiver_region, amount, description
            ) VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                data['sender_id'], data['sender_region'], 
                data['receiver_id'], data['receiver_region'], 
                amount, data['description']
            )
        )

        conn.commit()
        return jsonify({"message": "Transaction processed successfully."})

    except ValueError as ve:
        if conn:
            conn.rollback()
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Error processing transaction: {e}"}), 500

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
