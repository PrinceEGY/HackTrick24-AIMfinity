import sys

sys.path.append("..")
from flask import Flask, request
from flask_restful import Resource, Api
import numpy as np
from LSBSteg import encode
from helpers import load_dataset
import time

app = Flask(__name__)
api = Api(app)

TEAM_ID = "123"
MSG = "MOCK SERVER WORKING!"
x_real, y_real, x_fake, y_fake = load_dataset("../footprints_dataset")
COUNT = 0
start_time = 0


class Start(Resource):
    def post(self):
        if request.json["teamId"] == TEAM_ID:
            global start_time, COUNT
            start_time = time.time()
            response = {"footprint": {"1": empty, "2": real, "3": fake}}

            COUNT += 1
            return response, 200
        return "Failure", 400


class RequestMessage(Resource):
    def post(self):
        if request.json["teamId"] == TEAM_ID:
            print(f"channelId chosen was: {request.json['channelId']}")
            encoded_message = encode(img, MSG)
            response = {"encodedMsg": encoded_message.tolist()}
            return response, 200
        return "Failure", 400


class SkipImage(Resource):
    def post(self):
        if request.json["teamId"] == TEAM_ID:
            global COUNT
            if COUNT == 5:
                return "End of message reached"

            response = {"footprint": {"1": empty, "2": real, "3": fake}}

            COUNT += 1
            return response, 200
        return "Failure", 400


class SubmitMessage(Resource):
    def post(self):
        if request.json["teamId"] == TEAM_ID:
            global COUNT
            decoded_msg = request.json["decodedMsg"]
            if decoded_msg == MSG:
                print("Message decoded successfully!")

            if COUNT == 5:
                return "End of message reached"

            response = {"footprint": {"1": empty, "2": real, "3": fake}}

            COUNT += 1
            return response, 200
        return "Failure", 400


class EndGame(Resource):
    def post(self):
        if request.json["teamId"] == TEAM_ID:
            print("--- %s seconds ---" % (time.time() - start_time))
            return "Game ended successfully with a score of 10. New Highscore reached!”"
        return "Failure", 400


api.add_resource(Start, "/eagle/start")
api.add_resource(RequestMessage, "/eagle/request-message")
api.add_resource(SkipImage, "/eagle/skip-message")
api.add_resource(SubmitMessage, "/eagle/submit-message")
api.add_resource(EndGame, "/eagle/end-game")

if __name__ == "__main__":
    img = np.random.randn(20, 20, 3)
    empty, real, fake = np.random.randn(*x_real[0].shape) * 10, x_real[0], x_fake[0]
    empty, real, fake = empty.tolist(), real.tolist(), fake.tolist()
    app.run(debug=True)
