import asyncio
import aiokafka
import json
import time

""" if __name__ == "__main__":
    consumer = kafka.KafkaConsumer(
        'the_topic',
        bootstrap_servers='localhost:9092',
        group_id='my_group',  # Consumer group ID
        auto_offset_reset='earliest',  # Start reading from the earliest message
        enable_auto_commit=True,  # Automatically commit the offsets
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Deserialize JSON messages
    )
    for message in consumer:
        print(message.value)
        consumer.commit()
 """

async def create_consumer(topic, bootstrap_servers='localhost:9092'):
    consumer = aiokafka.AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id="my-group" 
    )
    await consumer.start()
    print(f"Consumer subscribed to topic: {topic}")
    return consumer

async def process_message(message):
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        try:
            print(f"Processing order: {message}")
            await asyncio.sleep(2)  # Just simulating async task
            print(f"Order {message['order_id']} processed")
            return  # Successful processing
        except Exception as e:
            print(f"Error processing order {message['order_id']}: {e}")
            retry_count += 1
            await asyncio.sleep(2)  # Wait before retrying
    print(f"Failed to process order {message['order_id']} after {max_retries} retries.")

async def consume_messages(consumer):
    print("Consumer started.")
    try:
        async for message in consumer:
            print(f"Received message: {message.value}")
            await process_message(message.value)
    finally:
        await consumer.stop()

async def main(topic):
    consumer = await create_consumer(topic)  # Create consumer with dynamic topic
    await consume_messages(consumer)

topic_name = "the_topic"  # You can change this to any topic dynamically
asyncio.run(main(topic_name))