from flask import Flask, jsonify, request
import solver

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World! Here I'll advertise the chrome extension."


@app.route("/solve", methods=['POST'])
def run_solver():
    return jsonify(solver.solve({k: set(v) for d in request.get_json() for (k, v) in d.items()}))


if __name__ == "__main__":
    app.run()
