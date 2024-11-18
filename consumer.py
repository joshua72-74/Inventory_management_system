import asyncio
from kafka import KafkaConsumer
import json
import pymongo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MongoDB Connection (use try-except for better error handling)
try:
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
    mongo_db = mongo_client['warehouse']  # Use 'warehouse' database
    location_inventory_collection = mongo_db['locationInventory']
except pymongo.errors.ConnectionFailure as e:
    logging.critical(f"Could not connect to MongoDB: {e}")
    exit(1)

# Kafka Consumer
consumer = KafkaConsumer('stock_updates', 
                        bootstrap_servers=['localhost:9092'], 
                        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                        auto_offset_reset='earliest'  # Consume from the beginning of the topic
                       )


async def process_message(message):
    try:
        stock_data = json.loads(message.value)
        product_id = stock_data['product_id']
        location_id = stock_data['location_id']
        quantity = stock_data['quantity']

        result = location_inventory_collection.update_one(
            {'location_id': location_id, 'product_id': product_id},
            {'$set': {'quantity': quantity}},
            upsert=True
        )

        if result.matched_count == 1:
            logging.info(f"Updated stock for product {product_id} at location {location_id} to {quantity}")
        elif result.upserted_id is not None:
            logging.info(f"Created new stock entry for product {product_id} at location {location_id} with quantity {quantity}")
        else:
            logging.warning(f"No matching document found for product {product_id} at location {location_id}")

    except (KeyError, TypeError) as e:
        logging.error(f"Error processing message: {e}. Invalid message: {message.value}")
    except pymongo.errors.PyMongoError as e:
        logging.error(f"MongoDB error: {e}")
    except Exception as e:
        logging.exception(f"General error: {e}")


async def consume_messages():
    async for message in consumer:
        asyncio.create_task(process_message(message))

async def main():
    await consume_messages()

if __name__ == '__main__':
    asyncio.run(main())