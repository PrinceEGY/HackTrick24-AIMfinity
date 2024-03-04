import sys

sys.path.append("..")
import numpy as np
from LSBSteg import decode
from helpers import *
import requests
from keras.models import load_model
import time

api_base_url = "http://127.0.0.1:5000"  # "3.70.97.142:5000"
team_id = "123"


def remaining_attempts(team_id):
    """
    In this fucntion you need to hit to the endpoint to start the game as an eagle with your team id.
    If a sucessful response is returned, you will recive back the first footprints.
    """
    endpoint = "http://13.53.169.72:5000/attempts/student"
    request_data = {"teamId": team_id}
    response = requests.post(
        endpoint,
        json=request_data,
    )
    dump_response("remaining attempts", request_data, response)
    response_data = response.json()
    print(response_data, response.status_code)


def init_eagle(team_id):
    """
    In this fucntion you need to hit to the endpoint to start the game as an eagle with your team id.
    If a sucessful response is returned, you will recive back the first footprints.
    """
    endpoint = "/eagle/start"
    request_data = {"teamId": team_id}
    response = requests.post(
        api_base_url + endpoint,
        json=request_data,
    )
    dump_response("eagle_start", request_data, response)
    response_data = response.json()
    return response_data


def skip_msg(team_id):
    """
    If you decide to NOT listen to ANY of the 3 channels then you need to hit the end point skipping the message.
    If sucessful request to the end point , you will expect to have back new footprints IF ANY.
    """
    endpoint = "/eagle/skip-message"
    request_data = {"teamId": team_id}
    response = requests.post(
        api_base_url + endpoint,
        json=request_data,
    )
    response_data = response.json()
    dump_response("eagle_skip_msg", request_data, response)
    return response_data


def request_msg(team_id, channel_id):
    """
    If you decide to listen to any of the 3 channels then you need to hit the end point of selecting a channel to hear on (1,2 or 3)
    """
    endpoint = "/eagle/request-message"
    request_data = {"teamId": team_id, "channelId": int(channel_id)}
    response = requests.post(
        api_base_url + endpoint,
        json=request_data,
    )
    response_data = response.json()
    dump_response("eagle_request_msg", request_data, response)
    return response_data


def submit_msg(team_id, decoded_msg):
    """
    In this function you are expected to:
        1. Decode the message you requested previously
        2. call the api end point to send your decoded message
    If sucessful request to the end point , you will expect to have back new footprints IF ANY.
    """
    endpoint = "/eagle/submit-message"
    request_data = {"teamId": team_id, "decodedMsg": decoded_msg}
    response = requests.post(
        api_base_url + endpoint,
        json=request_data,
    )
    response_data = response.json()
    dump_response("eagle_submit_msg", request_data, response)

    return response_data


def end_eagle(team_id):
    """
    Use this function to call the api end point of ending the eagle  game.
    Note that:
    1. Not calling this fucntion will cost you in the scoring function
    """
    endpoint = "/eagle/end-game"
    request_data = {"teamId": team_id}
    response = requests.post(
        api_base_url + endpoint,
        json=request_data,
    )
    response_data = response.json()
    dump_response("eagle_end", request_data, response)
    print(response_data, response.status_code)


def submit_eagle_attempt(team_id):
    """
    Call this function to start playing as an eagle.
    You should submit with your own team id that was sent to you in the email.
    Remeber you have up to 15 Submissions as an Eagle In phase1.
    In this function you should:
       1. Initialize the game as fox
       2. Solve the footprints to know which channel to listen on if any.
       3. Select a channel to hear on OR send skip request.
       4. Submit your answer in case you listened on any channel
       5. End the Game
    """
    start = time.time()
    response_data = init_eagle(team_id)
    print("init time: ", time.time() - start)
    while response_data != "End of message reached":
        footprints = response_data["footprint"]
        start = time.time()
        channel_id = evaluate_footprints(footprints, model)
        print("evaluation time: ", time.time() - start)
        if channel_id == 0:
            start = time.time()
            response_data = skip_msg(team_id)
            print("skipping time: ", time.time() - start)
        else:
            start = time.time()
            response_data = request_msg(team_id, channel_id)
            print("requesting time: ", time.time() - start)
            encoded_msg = response_data["encodedMsg"]
            start = time.time()
            decoded_msg = decode(np.array(encoded_msg))
            print("decoding time: ", time.time() - start)
            start = time.time()
            response_data = submit_msg(team_id, decoded_msg)
            print("submitting time: ", time.time() - start)

    end_eagle(team_id)


if __name__ == "__main__":
    # Initialize the model before running
    print("Loading model...")
    model = load_model("spectro.keras")
    model.predict(np.zeros((1, 1998, 101, 1)))
    # remaining_attempts("TPRTO2z")
    print("Model loaded")
    print("Starting eagle attempt...")
    submit_eagle_attempt(team_id)
    save_logs()
