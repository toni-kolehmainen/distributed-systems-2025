import grpc
import os
import calculator_pb2
import calculator_pb2_grpc
from flask import Flask, request, make_response
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
env_calc = os.environ.get("CALCULATOR_URI")
CALCULATOR_URI = env_calc if env_calc else "localhost:50052"


@app.get("/")
def index():
    with grpc.insecure_channel(CALCULATOR_URI) as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)
        response = stub.Add(calculator_pb2.CalculationRequest(number1=1, number2=2))
        return make_response(
            {"message": "Basic demonstration control API", "'1+2'": response.result}
        )


@app.post("/")
def post_message():
    try:
        message = request.json["message"]
        message = request
        print(message)
        # Pass message onward here
        return make_response({"message": f"processed message '{message}'"})
    except KeyError:
        raise BadRequest()


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return make_response(e.description, 400)
