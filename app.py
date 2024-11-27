from flask import Flask, render_template, request, jsonify
import database  # Import database functions

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/accounts', methods=['GET'])
def accounts():
    accounts = database.get_accounts()
    return jsonify(accounts)

@app.route('/transactions', methods=['GET'])
def transactions():
    transactions = database.get_transactions()
    return jsonify(transactions)




@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.json
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    amount = data['amount']
    region = data['region']

    # Call the database function
    result = database.process_payment(sender_id, receiver_id, amount, region)

    # Return the result as JSON
    return jsonify(result), (200 if result["status"] == "success" else 400)




@app.route('/accounts_page', methods=['GET'])
def accounts_page():
    accounts = database.get_accounts()
    return render_template('accounts.html', accounts=accounts)

@app.route('/transactions_page', methods=['GET'])
def transactions_page():
    transactions = database.get_transactions()
    return render_template('transactions.html', transactions=transactions)


if __name__ == '__main__':
    app.run(debug=True)
