from flask import Flask, jsonify, request, redirect
from jsonschema import ValidationError, validate
from flask_cors import CORS
import solver.solver
import os

app = Flask(__name__)
CORS(app)

# Input to the API should match this JSON schema
# This JSON data must be an object containing the property "sets"
# "sets" is an array of objects, each of which has exactly one property,
# which is an array. It must be the case either that all of these arrays
# consist of integers, or that all of these arrays consist of strings.
# The data may also contain the property "method", which specifies which
# linear program to run. The options are "strict", "relaxed", and "transpose".
# The data may also specify a non-negative integer parameter named
# "param". This is the argument to relaxedSolve or transposeSolve,
# as appropriate.
schema = {
    "type": "object",
    "properties": {
        "method": {
            "type": "string",
            "pattern": "^(strict|relaxed|transpose)$"
        },
        "sets": {
            "type": "array",
            "uniqueItems": True,
            "oneOf": [
                {
                    "items": {
                        "type": "object",
                        "minProperties": 1,
                        "maxProperties": 1,
                        "additionalProperties": {
                            "type": "array",
                            "uniqueItems": True,
                            "items": {"type": "integer"}
                        }
                    }
                },
                {
                    "items": {
                        "type": "object",
                        "minProperties": 1,
                        "maxProperties": 1,
                        "additionalProperties": {
                            "type": "array",
                            "uniqueItems": True,
                            "items": {"type": "string"}
                        }
                    }
                }
            ]
        },
        "param": {
            "type": "integer",
            "minimum": 0
        }
    },
    "required": ["sets"],
    "additionalProperties": False
}


@ app.route("/")
def hello_world():
    return redirect("https://www.wig-solver.app", code=302)


@ app.route("/solve", methods=['POST'])
def run_solver():
    data = request.get_json()
    try:
        validate(data, schema)
    except ValidationError as e:
        return "Invalid data: " + e.message, 400
    dictionary = {k: set(v) for d in data["sets"] for (k, v) in d.items()}
    if "method" not in data or data["method"] == "strict":
        # Run strict solve
        return jsonify(solver.solver.solveStrict(dictionary))
    if "param" not in data:
        # Run alternate solve with default parameters
        if data["method"] == "relaxed":
            return jsonify(solver.solver.solveRelaxed(dictionary))
        if data["method"] == "transpose":
            return jsonify(solver.solver.solveTranspose(dictionary))
    # Run alternate solve with specified parameters
    if data["method"] == "relaxed":
        return jsonify(solver.solver.solveRelaxed(dictionary, data["param"]))
    if data["method"] == "transpose":
        return jsonify(solver.solver.solveTranspose(dictionary, data["param"]))


@ app.route("/health")
def return_ok():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
