import sys

sys.path.append("../..")
from flask import Flask, request, jsonify
import numpy as np
from matplotlib.pyplot import imread
import pandas as pd
from LSBSteg import decode

app = Flask(__name__)

# Dummy data for testing
carrier_image = np.random.randn(20, 20, 3)
secret_message = "THE ABC MERCY WELL B"


@app.route("/fox/start", methods=["POST"])
def start_game():
    team_id = request.json.get("teamId")
    return (
        jsonify({"msg": secret_message, "carrier_image": carrier_image.tolist()}),
        200,
    )


data = pd.read_csv(
    "C:\dev\HackTrick-AIMfinity\Riddles\ml_easy_sample_example\series_data.csv"
)
# data2 = pd.read_csv("D:\HackTrick\Repo\HackTrick-AIMfinity\Riddles\ml_medium_dataset\MlMediumTrainingData.csv")

dict = {
    "sec_medium_stegano": imread("encoded.png").tolist(),
    "sec_hard": ("266200199BBCDFF1", "0123456789ABCDEF"),
    "cv_easy": "cv_easyTestCase",
    "cv_medium": "cv_mediumTestCase",
    "cv_hard": "cv_hardTestCase",
    "ml_easy": {
        "timestamp": data["timestamp"].tolist(),
        "visits": data["visits"].tolist(),
    },
    "ml_medium": [-20.73948417, 0.061261011],
    "problem_solving_easy": (
        [
            "pharaoh",
            "sphinx",
            "pharaoh",
            "pharaoh",
            "nile",
            "sphinx",
            "pyramid",
            "pharaoh",
            "sphinx",
            "sphinx",
        ],
        3,
    ),
    "problem_solving_medium": "3[d1[e1[1]]]",
    "problem_solving_hard": (3, 2),
}


@app.route("/fox/get-riddle", methods=["POST"])
def get_riddle():
    team_id = request.json.get("teamId")
    riddle_id = request.json.get("riddleId")
    test_case = dict[riddle_id]
    return jsonify({"test_case": test_case}), 200


@app.route("/fox/solve-riddle", methods=["POST"])
def solve_riddle():
    team_id = request.json.get("teamId")
    solution = request.json.get("solution")
    # Dummy logic to simulate solving the riddle
    print(solution)
    budget_increase = 100
    total_budget = 1000
    status = "success"
    return (
        jsonify(
            {
                "budget increase": budget_increase,
                "total budget": total_budget,
                "status": status,
            }
        ),
        200,
    )


@app.route("/fox/send-message", methods=["POST"])
def send_message():
    team_id = request.json.get("teamId")
    messages = request.json.get("messages")
    message_entities = request.json.get("message entities")

    decoded_msg1, decoded_msg2, decoded_msg3 = (
        decode(np.array(messages[0])),
        decode(np.array(messages[1])),
        decode(np.array(messages[2])),
    )
    print(decoded_msg1, decoded_msg2, decoded_msg3)
    # Dummy logic to simulate sending messages
    status = "success"
    return jsonify({"status": status}), 200


@app.route("/fox/end-game", methods=["POST"])
def end_game():
    team_id = request.json.get("teamId")
    # Dummy logic to simulate ending the game
    score = 10
    new_highscore = True
    return (
        f"Game ended successfully with a score of {score}. {'New Highscore reached!' if new_highscore else ''}",
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)
