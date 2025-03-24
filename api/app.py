from flask import Flask, jsonify
import random
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

def random_date(start, end):
    """Génère une date aléatoire entre start et end."""
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Retourne une liste de transactions aléatoires."""
    transactions = []
    for i in range(5):
        transactions.append({
            "transaction_id": f"T{i:05}",
            "date_time": random_date(datetime(2023, 1, 1), datetime(2023, 12, 31)).isoformat(),
            "amount": round(random.uniform(10, 1000), 2),  # Arrondi à 2 décimales
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "merchant_details": f"Merchant{random.randint(1, 20)}",
            "customer_id": f"C{random.randint(1, 10):03}",
            "transaction_type": random.choice(["purchase", "withdrawal"])
        })
    
    # Sauvegarde les données dans un fichier temporaire pour Airflow
    with open('/tmp/transactions.json', 'w') as f:
        json.dump(transactions, f)
    
    return jsonify(transactions)

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Retourne une liste de clients aléatoires."""
    customers = []
    for i in range(3):
        customers.append({
            "customer_id": f"C{i:03}",
            "account_history": [f"T{random.randint(1, 1000):05}" for _ in range(2)],
            "demographics": {
                "age": random.randint(18, 70),
                "location": f"City{random.randint(1, 10)}"
            },
            "behavioral_patterns": {
                "avg_transaction_value": round(random.uniform(50, 500), 2)
            }
        })
    
    # Sauvegarde les données dans un fichier temporaire pour Airflow
    with open('/tmp/customers.json', 'w') as f:
        json.dump(customers, f)
    
    return jsonify(customers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)