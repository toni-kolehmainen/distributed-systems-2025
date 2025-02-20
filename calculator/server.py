from concurrent import futures
import grpc
import pymongo
import calculator_pb2
import calculator_pb2_grpc
import os
import uuid

# MongoDB Connection

client = pymongo.MongoClient(
                            os.environ.get("MONGO_URI"),
                            read_preference=pymongo.ReadPreference.SECONDARY
                            )
db = client["calculator_db"].with_options(read_concern=pymongo.read_concern.ReadConcern("local"))
collection = db["calculations"]

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    def log_to_db(self, operation, number1, number2, result):
        """Log calculation to MongoDB."""
        collection.insert_one(
            {
                "operation": operation,
                "number1": number1,
                "number2": number2,
                "result": result,
            },
            write_concern=pymongo.WriteConcern(w=1)
        )

    def Add(self, request, context):
        result = request.number1 + request.number2
        # self.log_to_db("Add", request.number1, request.number2, result)
        return calculator_pb2.CalculationResponse(result=result)

    def Subtract(self, request, context):
        result = request.number1 - request.number2
        self.log_to_db("Subtract", request.number1, request.number2, result)
        return calculator_pb2.CalculationResponse(result=result)

    def Multiply(self, request, context):
        result = request.number1 * request.number2
        self.log_to_db("Multiply", request.number1, request.number2, result)
        return calculator_pb2.CalculationResponse(result=result)

    def Divide(self, request, context):
        if request.number2 == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Division by zero is not allowed")
            return calculator_pb2.CalculationResponse()
        result = request.number1 / request.number2
        self.log_to_db("Divide", request.number1, request.number2, result)
        return calculator_pb2.CalculationResponse(result=result)

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), server)
    server.add_insecure_port("[::]:50052")
    print("Calculator Server is running on port 50052...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    server()
