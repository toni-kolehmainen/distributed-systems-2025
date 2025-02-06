import time
import random
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import os

env_kafka = os.environ.get("KAFKA_URI")
KAFKA_URL = env_kafka if env_kafka else "localhost:9092"


WORDS = []
with open("words.txt") as file:
    WORDS = file.readlines()


def produce_words() -> str:
    words = [
        WORDS[random.randint(0, len(WORDS))].replace("\n", "")
        for x in range(random.randint(1, 12))
    ]

    return " ".join(words)


def run():
    producer = None
    while not producer:
        try:
            print("Attempting connection...")
            producer = KafkaProducer(bootstrap_servers=KAFKA_URL)
        except NoBrokersAvailable:
            print("No brokers available, attempting again in 10s.")
            time.sleep(10)

    print("Beginning word production")
    while True:
        words = produce_words()
        producer.send("words", bytes(words.encode("utf-8")))
        print(f"sent package '{words}'")
        time.sleep(5)


if __name__ == "__main__":
    run()
