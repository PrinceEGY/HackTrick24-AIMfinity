import sys

sys.path.append("../..")
from flask import Flask, request, jsonify
import numpy as np
from matplotlib.pyplot import imread
import pandas as pd
from LSBSteg import decode
from PIL import Image
import json


app = Flask(__name__)

# Dummy data for testing
carrier_image = Image.open("carrier_image.jpg")
secret_message = "Unseen data in view."
cv_easy = Image.open(r"C:\dev\HackTrick-AIMfinity\Solvers\Mock Fox\shredded_img.jpg")
cv_med_combined = Image.open(
    r"C:\dev\HackTrick-AIMfinity\Solvers\Mock Fox\combined_large_image.png"
)
cv_med_patch = Image.open(
    r"C:\dev\HackTrick-AIMfinity\Solvers\Mock Fox\patch_image.png"
)
cv_hard = Image.open(r"C:\dev\HackTrick-AIMfinity\Solvers\fox_logs\cv_hard1.jpg")

data = pd.read_csv(
    "C:\dev\HackTrick-AIMfinity\Riddles\ml_easy_sample_example\series_data.csv"
)

with open("img.txt", "r") as f:
    img = f.read()
    img = json.loads(img)


dict = {
    "sec_medium_stegano": img,
    "sec_hard": ("266200199BBCDFF1", "0123456789ABCDEF"),
    "cv_easy": [np.array(cv_easy).tolist(), 64],
    "cv_medium": [np.array(cv_med_combined).tolist(), np.array(cv_med_patch).tolist()],
    "cv_hard": ["How many people are wearing glasses?", np.array(cv_hard).tolist()],
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


@app.route("/fox/start", methods=["POST"])
def start_game():
    team_id = request.json.get("teamId")
    return (
        jsonify(
            {"msg": secret_message, "carrier_image": np.array(carrier_image).tolist()}
        ),
        200,
    )


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
    # print(solution)
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
