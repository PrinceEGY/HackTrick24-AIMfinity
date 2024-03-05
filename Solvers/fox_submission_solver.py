import sys

sys.path.append("..")
import numpy as np
import time
from matplotlib.pyplot import imread
import LSBSteg
from LSBSteg import encode
from riddle_solvers import *
import requests as r
from helpers import dump_response, save_logs
import json

api_base_url = "http://127.0.0.1:5000/fox"  # "http://3.70.97.142:5000/fox"
team_id = "TPRTO2z"


def init_fox(team_id):
    """
    In this fucntion you need to hit to the endpoint to start the game as a fox with your team id.
    If a sucessful response is returned, you will recive back the message that you can break into chunkcs
      and the carrier image that you will encode the chunk in it.
    """
    req = {"teamId": team_id}
    response = r.post(api_base_url + "/start", json=req)
    dump_response("INIT FOX", req, response)
    return response.json()


def generate_message_array(message, image_carrier):
    """
    In this function you will need to create your own startegy. That includes:
        1. How you are going to split the real message into chunkcs
        2. Include any fake chunks
        3. Decide what 3 chuncks you will send in each turn in the 3 channels & what is their entities (F,R,E)
        4. Encode each chunck in the image carrier
    """
    # Lengths = [7, 6, 7]
    chunks = [message[0:7], message[7:13], message[13:]]
    List_Of_Fake_Msgs = ["Fake1", "Fake2"]
    print(chunks)
    print("Sending chunk 1...")
    start = time.time()
    # First
    msg1 = encode(image_carrier.copy(), List_Of_Fake_Msgs[0])
    msg2 = encode(image_carrier.copy(), chunks[0])
    msg3 = encode(image_carrier.copy(), List_Of_Fake_Msgs[1])
    data = [msg1.tolist(), msg2.tolist(), msg3.tolist()]
    send_message(team_id, data, ["F", "R", "F"])
    print("--- %s seconds ---" % (time.time() - start))

    print("Sending chunk 2...")
    start = time.time()
    # Second
    msg1 = encode(image_carrier.copy(), chunks[1])
    msg2 = encode(image_carrier.copy(), List_Of_Fake_Msgs[0])
    msg3 = encode(image_carrier.copy(), List_Of_Fake_Msgs[1])
    data = [msg1.tolist(), msg2.tolist(), msg3.tolist()]
    send_message(team_id, data, ["R", "F", "F"])
    print("--- %s seconds ---" % (time.time() - start))

    print("Sending chunk 2...")
    start = time.time()
    # Third
    msg1 = encode(image_carrier.copy(), List_Of_Fake_Msgs[1])
    msg2 = encode(image_carrier.copy(), List_Of_Fake_Msgs[0])
    msg3 = encode(image_carrier.copy(), chunks[2])
    data = [msg1.tolist(), msg2.tolist(), msg3.tolist()]
    send_message(team_id, data, ["F", "F", "R"])
    print("--- %s seconds ---" % (time.time() - start))


def get_riddle(team_id, riddle_id):
    """
    In this function you will hit the api end point that requests the type of riddle you want to solve.
    use the riddle id to request the specific riddle.
    Note that:
        1. Once you requested a riddle you cannot request it again per game.
        2. Each riddle has a timeout if you didnot reply with your answer it will be considered as a wrong answer.
        3. You cannot request several riddles at a time, so requesting a new riddle without answering the old one
          will allow you to answer only the new riddle and you will have no access again to the old riddle.
    """
    request = {"teamId": team_id, "riddleId": riddle_id}
    resopnse = r.post(api_base_url + "/get-riddle", json=request)
    dump_response("GET RIDDLE", request, resopnse)
    return resopnse.json()


def solve_riddle(team_id, solution):
    """
    In this function you will solve the riddle that you have requested.
    You will hit the API end point that submits your answer.
    Use te riddle_solvers.py to implement the logic of each riddle.
    """
    request = {"teamId": team_id, "solution": solution}
    response = r.post(api_base_url + "/solve-riddle", json=request)
    dump_response("SOLVE RIDDLE", request, response)
    return response.json()


def send_message(team_id, messages, message_entities=["F", "E", "R"]):
    """
    Use this function to call the api end point to send one chunk of the message.
    You will need to send the message (images) in each of the 3 channels along with their entites.
    Refer to the API documentation to know more about what needs to be send in this api call.
    """
    request = {
        "teamId": team_id,
        "messages": messages,
        "message_entities": message_entities,
    }
    reponse = r.post(
        api_base_url + "/send-message",
        json=request,
    )
    dump_response("SEND MESSAGE", request, reponse)
    return reponse.text


def end_fox(team_id):
    """
    Use this function to call the api end point of ending the fox game.
    Note that:
    1. Not calling this fucntion will cost you in the scoring function
    2. Calling it without sending all the real messages will also affect your scoring fucntion
      (Like failing to submit the entire message within the timelimit of the game).
    """
    request = {"teamId": team_id}
    reponse = r.post(api_base_url + "/end-game", json=request)
    dump_response("END FOX GAME", request, reponse)
    return reponse.text


def submit_fox_attempt(team_id):
    """
     Call this function to start playing as a fox.
     You should submit with your own team id that was sent to you in the email.
     Remeber you have up to 15 Submissions as a Fox In phase1.
     In this function you should:
        1. Initialize the game as fox
        2. Solve riddles
        3. Make your own Strategy of sending the messages in the 3 channels
        4. Make your own Strategy of splitting the message into chunks
        5. Send the messages
        6. End the Game
    Note that:
        1. You HAVE to start and end the game on your own. The time between the starting and ending the game is taken into the scoring function
        2. You can send in the 3 channels any combination of F(Fake),R(Real),E(Empty) under the conditions that
            2.a. At most one real message is sent
            2.b. You cannot send 3 E(Empty) messages, there should be atleast R(Real)/F(Fake)
        3. Refer To the documentation to know more about the API handling
    """
    print("Starting Fox Game...")
    start = time.time()
    gamestarted = init_fox(team_id)
    print("--- %s seconds ---" % (time.time() - start))

    Message = gamestarted["msg"]
    Img = gamestarted["carrier_image"]
    Img = np.array(Img)
    for x in riddle_solvers.keys():
        try:
            print("Getting Riddle...", x)
            start = time.time()
            res = get_riddle(team_id, x)
            print("--- %s seconds ---" % (time.time() - start))
            input = res["test_case"]
            ans = riddle_solvers[x](input)

            start = time.time()
            print("Solving Riddle...", x)
            solve_riddle(team_id, ans)

            print("--- %s seconds ---" % (time.time() - start))
        except Exception as e:
            print(e)

    generate_message_array(Message, Img)

    start = time.time()
    print("Ending game...")
    final = end_fox(team_id)
    print("--- %s seconds ---" % (time.time() - start))
    print(final)
    print("Done!")


with open("C:\dev\HackTrick-AIMfinity\SteganoGAN\img.txt", "r") as f:
    img = f.read()
    img = json.loads(img)
solve_sec_medium(img)

print("Starting attemp...")
start = time.time()
submit_fox_attempt(team_id)
print("--- %s seconds ---" % (time.time() - start))


save_logs("fox_logs.txt")
