from flask import Flask, request, make_response
from werkzeug.exceptions import BadRequest

app = Flask(__name__)


@app.get("/")
def index():
    return make_response({"message": "Basic demonstration control API"})


@app.post("/")
def post_message():
    try:
        message = request.json["message"]
        print(message)
        # Pass message onward here
        return make_response({"message": f"processed message '{message}'"})
    except KeyError:
        raise BadRequest()


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return make_response(e.description, 400)
