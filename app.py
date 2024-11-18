from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import pymongo
from kafka import KafkaProducer
import json

app = Flask(__name__)
CORS(app)

# Database Connections
mysql_config = {
    'host': 'localhost',
    'port': 3306,  # Explicitly specify the port number
    'user': 'root',
    'password': 'Manchuri@786',
    'database': 'warehouse'
}

try:
    mysql_conn = mysql.connector.connect(**mysql_config)
    mysql_cursor = mysql_conn.cursor(dictionary=True)  # Fetch data as dictionaries
except mysql.connector.Error as err:
    print(f"Something went wrong: {err}")
    exit(1)

mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
mongo_db = mongo_client['warehouse']
product_categories_collection = mongo_db['productCategories']
location_inventory_collection = mongo_db['locationInventory']

# Kafka Producer
kafka_producer = KafkaProducer(bootstrap_servers=['localhost:9092'])


# --- Helper function to fetch category data ---
def fetch_category_data(product_id):
    category_data = product_categories_collection.find_one({"product_id": product_id})
    if category_data:
        return category_data
    else:
        return {}  # Return an empty dictionary if category data is not found


# --- Product Management ---
@app.route('/products', methods=['GET'])
def get_products():
    # ... (Pagination logic remains the same)

    products = mysql_cursor.fetchall()
    product_list = []
    for product in products:
        product_data = {
            'product_id': product['product_id'],
            'name': product['name'],
            'description': product['description'],
            'supplier_id': product['supplier_id']
        }
        product_data.update(fetch_category_data(product['product_id']))
        product_list.append(product_data)
    return jsonify(product_list)


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    mysql_cursor.execute("SELECT * FROM Products WHERE product_id = %s", (product_id,))
    product = mysql_cursor.fetchone()
    if product:
        product_data = {
            'product_id': product['product_id'],
            'name': product['name'],
            'description': product['description'],
            'supplier_id': product['supplier_id']
        }
        product_data.update(fetch_category_data(product_id))
        return jsonify(product_data)
    else:
        return jsonify({'error': 'Product not found'}), 404


@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    required_fields = ['name', 'description', 'supplier_id', 'category']
    if all(field in data for field in required_fields):
        try:
            mysql_cursor.execute("INSERT INTO Products (name, description, supplier_id) VALUES (%s, %s, %s)", (data['name'], data['description'], data['supplier_id']))
            mysql_conn.commit()
            product_id = mysql_cursor.lastrowid

            # Insert category data into MongoDB
            category_data = {
                "product_id": product_id,
                "category": data['category'],
                "description": data.get('description'),
                "images": data.get('images', [])  # Handle missing images
            }
            product_categories_collection.insert_one(category_data)

            return jsonify({'product_id': product_id}), 201
        except mysql.connector.Error as err:
            mysql_conn.rollback()
            return jsonify({'error': f'Database error: {err}'}), 500
    else:
        return jsonify({'error': 'Missing required fields'}), 400


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    required_fields = ['name', 'description', 'supplier_id', 'category']
    if all(field in data for field in required_fields):
        try:
            mysql_cursor.execute("UPDATE Products SET name = %s, description = %s, supplier_id = %s WHERE product_id = %s", (data['name'], data['description'], data['supplier_id'], product_id))
            mysql_conn.commit()

            category_data = {
                "product_id": product_id,
                "category": data['category'],
                "description": data.get('description'),
                "images": data.get('images', [])  # Handle missing images
            }
            product_categories_collection.update_one({"product_id": product_id}, {"$set": category_data}, upsert=True)

            return jsonify({'message': 'Product updated successfully'}), 200
        except mysql.connector.Error as err:
            mysql_conn.rollback()
            return jsonify({'error': f'Database error: {err}'}), 500

    else:
        return jsonify({'error': 'Missing required fields'}), 400


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        mysql_cursor.execute("DELETE FROM Products WHERE product_id = %s", (product_id,))
        mysql_conn.commit()
        product_categories_collection.delete_one({"product_id": product_id})
        return jsonify({'message': 'Product deleted successfully'}), 200
    except mysql.connector.Error as err:
        mysql_conn.rollback()
        return jsonify({'error': f'Database error: {err}'}), 500

# ... (Rest of your code - Supplier, Location, Stock, Reports) ...

@app.route('/stock', methods=['GET'])
def get_all_stock():
    try:
        mysql_cursor.execute("SELECT * FROM Stock")
        stock_data = mysql_cursor.fetchall()
        return jsonify(stock_data)
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500

if __name__ == '__main__':
    app.run(debug=True)