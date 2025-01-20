import asyncio
import aiokafka
import json

async def send_one(topic, message, bootstrap_servers='localhost:9092'):
    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    try:
        await producer.send_and_wait(topic, message)
        print(f"Sent message: {message}")
    finally:
        await producer.stop()

async def main():
    topic_name = 'the_topic'  # Change this to your topic
    message = {'order_id': 123, 'product': 'widget', 'quantity': 10}
    await send_one(topic_name, message)

asyncio.run(main())

""" producer = kafka.KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_message(topic, message):
    producer.send(topic, {'message': message})
    producer.flush()

if __name__ == "__main__":
    send_message('the_topic', 'Hello, Kafka!') """