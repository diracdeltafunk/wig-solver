from flask import Flask, jsonify, request
from flask_cors import CORS
import solver
import os

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello_world():
    return "Hello, World! Here I'll advertise the chrome extension."


@app.route("/solve", methods=['POST'])
def run_solver():
    return jsonify(solver.solveStrict({k: set(v) for d in request.get_json() for (k, v) in d.items()}))


@app.route("/health")
def return_ok():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
