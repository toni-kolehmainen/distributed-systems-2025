import grpc
import os
import calculator_pb2
import calculator_pb2_grpc
import requests
from flask import Flask, request, make_response
from werkzeug.exceptions import BadRequest
from prometheus_flask_exporter import PrometheusMetrics
import etcd3
import time
import threading
from openai import OpenAI

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')
env_calc = os.environ.get("CALCULATOR_URI")
env_kafka = os.environ.get("KAFKA_URI")
enc_kafkaservice = os.environ.get("KAFKASERVICE_URI")
ETCD_HOST = os.environ.get("ETCD_HOST", "localhost")  # or "etcd-service" in Kubernetes
CALCULATOR_URI = env_calc if env_calc else "localhost:50052"
KAFKA_URI = env_kafka if env_kafka else "localhost:9092"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY,  # This is the default and can be omitted
)
# Pakko olla http://, muuten ei toimi
KAFKASERVICE_URI = enc_kafkaservice if enc_kafkaservice else "http://kafkaservice:8084"

# etcd setup for leader election

LEADER_KEY = "/leader"  # The key in etcd used for leader election
LEASE_TTL = 10  # Lease TTL in seconds

# Setup etcd client
etcd_client = etcd3.client(host=ETCD_HOST, port=2379)

# Global variable to track the current leader
current_leader = None

# class LeaderElection:
#     def __init__(self, etcd_client, leader_key, lease_ttl):
#         self.etcd = etcd_client
#         self.leader_key = leader_key
#         self.lease_ttl = lease_ttl
#         self.current_leader = None
#         self.lock = threading.Lock()

#     def acquire_leadership(self):
#         """Try to acquire leadership by putting a key in etcd with a lease."""
#         lease = self.etcd.lease(self.lease_ttl)
#         lease_id = lease.id

#         try:
#             # Attempt to acquire leadership by setting the leader key with a lease
#             success = self.etcd.put(self.leader_key, "leader", lease=lease)
#             if success:
#                 print("Successfully acquired leadership!")
#                 self.current_leader = lease_id
#                 return True
#             else:
#                 print("Failed to acquire leadership.")
#                 return False
#         except Exception as e:
#             print(f"Error acquiring leadership: {e}")
#             return False

#     def renew_leadership(self):
#         """Periodically renew leadership while holding the lease."""
#         while self.current_leader:
#             time.sleep(self.lease_ttl / 2)  # Renew the lease before it expires
#             print("Renewing leadership...")
#             self.etcd.refresh_lease(self.current_leader)
#             print("Leadership renewed.")

#     def lose_leadership(self):
#         """Lose leadership and clear the leader key."""
#         print("Losing leadership...")
#         self.etcd.delete(self.leader_key)
#         self.current_leader = None

#     def run_for_leadership(self):
#         """Start the leader election process and hold leadership."""
#         while True:
#             with self.lock:
#                 if self.acquire_leadership():
#                     # Start a thread to periodically renew leadership
#                     renew_thread = threading.Thread(target=self.renew_leadership)
#                     renew_thread.start()
#                     # Simulate doing work while being the leader
#                     time.sleep(15)  # Do work as the leader (e.g., perform calculations or interact with Kafka)
#                     self.lose_leadership()
#                     renew_thread.join()  # Clean up the renewal thread
#                 else:
#                     print("Waiting to become leader...")

#             time.sleep(5)  # Retry acquiring leadership after a short wait


# # Instantiate leader election manager
# leader_election = LeaderElection(etcd_client, LEADER_KEY, LEASE_TTL)

@app.get("/")
@metrics.histogram('http_request_duration_seconds', 'Request latencies by status and path',
                   labels={'status': lambda r: r.status_code, 'path': lambda: request.path})
@metrics.gauge('process_cpu_usage', 'Current CPU usage in percent')
@metrics.gauge('process_memory_usage_bytes', 'Current memory usage in bytes')
def index():
    with grpc.insecure_channel(CALCULATOR_URI) as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)
        response = stub.Add(calculator_pb2.CalculationRequest(number1=1, number2=2))
        return make_response(
            {"message": "Basic demonstration control API", "'1+2'": response.result}
        )

@app.post("/")
@metrics.do_not_track()
def post_message():
    try:
        message = request.json["message"]
        message = request
        print(message)
        # Pass message onward here
        return make_response({"message": f"processed message '{message}'"})
    except KeyError:
        raise BadRequest()

@app.post("/new_topic")
@metrics.do_not_track()
def new_kafka_topic():
    if request.content_type != 'application/json':
        return make_response("Request content type must be JSON", 415)
    
    new_topic = request.json["topic"]

    try:
        response = requests.post(f"{KAFKASERVICE_URI}/kafka_topic", json={"topic": new_topic})
        return make_response(response.json(), response.status_code)
    except Exception as e:
        return make_response({"error": str(e)}, 500)

# test that kafka works with grpc
@app.post("/send_producer")
@metrics.do_not_track()
def post_message_kafka():
    if request.content_type != 'application/json':
        return make_response("Request content type must be JSON", 415)
    
    data = request.json
    if not data:
        return make_response("Request content type must be JSON", 415)

    topic = data.get("topic")
    one = data.get("number1")
    two = data.get("number2")

    try:
        with grpc.insecure_channel(CALCULATOR_URI) as channel:
            stub = calculator_pb2_grpc.CalculatorStub(channel)
            response = stub.Add(calculator_pb2.CalculationRequest(number1=one, number2=two))
    except grpc.RpcError as e:
        return make_response({"error": f"gRPC error: {e}"}, 500)

    try:
        kafkaResponse = requests.post(f"{KAFKASERVICE_URI}/kafka_producer", json={"topic": topic, "message": response.result})
        kafkaResponse.raise_for_status()
        return make_response(kafkaResponse.json())
    except requests.RequestException as e:
        return make_response({"error": f"Kafka service error: {e}"}, 500)

@app.post("/start_consumer")
@metrics.do_not_track()
def start_consumer():
    if request.content_type != 'application/json':
        return make_response("Request content type must be JSON", 415)

    topic = request.json["topic"]

    try:
        response = requests.post(f"{KAFKASERVICE_URI}/start_consumer", json={"topic": topic})
        return make_response(response.json(), response.status_code)
    except KeyError:
        return make_response({"error": "Bad Request"}), 400

@app.post("/suggest_enhancements")
@metrics.do_not_track()
def suggest_enhancements():
    if request.content_type != "application/json":
        return make_response("Request content type must be JSON", 415)

    # Example input: Kafka topic name, calculator input, or message content
    input_data = request.json.get("input")

    if not input_data:
        return make_response("Missing 'input' field in request body", 400)

    try:
        messages = [
            {"role": "system", "content": "You are an nerd who has high iq and knows a lot from everything."},
            {"role": "user", "content": input_data}
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" if needed
            messages=messages,
            temperature=0.7,
            max_tokens=200,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.3
        )

        # Correct way to extract content
        suggestion= response.choices[0].message.content
        # Call ChatGPT API for suggestions
        return make_response({"suggestion": suggestion}, 200)
        # return make_response({"suggestion": input_data}, 200)
    except Exception as e:
        return make_response({"error": str(e)}, 500)

@app.errorhandler(BadRequest)
@metrics.do_not_track()
def handle_bad_request(e):
    return make_response(e.description, 400)

# Run leader election in a background thread
# leader_thread = threading.Thread(target=leader_election.run_for_leadership)
# leader_thread.daemon = True
# leader_thread.start()
