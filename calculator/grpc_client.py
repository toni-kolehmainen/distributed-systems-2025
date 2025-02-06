import grpc
import os
import calculator_pb2
import calculator_pb2_grpc


def run():
    with grpc.insecure_channel(os.environ.get("CALCULATOR_URI")) as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)

        # Perform various operations
        print("Performing calculations:")
        response = stub.Add(calculator_pb2.CalculationRequest(number1=10, number2=5))
        print(f"10 + 5 = {response.result}")

        response = stub.Subtract(
            calculator_pb2.CalculationRequest(number1=10, number2=5)
        )
        print(f"10 - 5 = {response.result}")

        response = stub.Multiply(
            calculator_pb2.CalculationRequest(number1=10, number2=5)
        )
        print(f"10 * 5 = {response.result}")

        response = stub.Divide(calculator_pb2.CalculationRequest(number1=10, number2=5))
        print(f"10 / 5 = {response.result}")


if __name__ == "__main__":
    run()
