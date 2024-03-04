import requests
import numpy as np
import time
from matplotlib.pyplot import imread
import LSBSteg
from LSBSteg import encode
from riddle_solvers import *
import requests as r

api_base_url = "http://127.0.0.1:5000/fox"
team_id = "TPRTO2z"


def init_fox(team_id):
    '''
    In this fucntion you need to hit to the endpoint to start the game as a fox with your team id.
    If a sucessful response is returned, you will recive back the message that you can break into chunkcs
      and the carrier image that you will encode the chunk in it.
    '''
    req1 = r.post(api_base_url + "/start", json={"teamId": team_id})
    LogResponse("Start Fox Game:\n" + req1.text)
    return req1.json()


def generate_message_array(message, image_carrier):
    '''
    In this function you will need to create your own startegy. That includes:
        1. How you are going to split the real message into chunkcs
        2. Include any fake chunks
        3. Decide what 3 chuncks you will send in each turn in the 3 channels & what is their entities (F,R,E)
        4. Encode each chunck in the image carrier
    '''
    Lengths = [7, 6, 7]
    chunks = [message[i:i + length] for i, length in enumerate(Lengths)]
    List_Of_Fake_Msgs = ["Fake1", "Fake2"]

    # First
    msg1 = encode(image_carrier.copy(), List_Of_Fake_Msgs[0])
    msg2 = encode(image_carrier.copy(), chunks[0])
    msg3 = encode(image_carrier.copy(), List_Of_Fake_Msgs[1])
    data = [msg1.tolist(), msg2.tolist(), msg3.tolist()]
    send_message(team_id, data, ['F', 'R', 'F'])
    # Second
    msg1 = encode(image_carrier.copy(), chunks[1])
    msg2 = encode(image_carrier.copy(), List_Of_Fake_Msgs[0])
    msg3 = encode(image_carrier.copy(), List_Of_Fake_Msgs[1])
    data = [msg1.tolist(), msg2.tolist(), msg3.tolist()]
    send_message(team_id, data, ['R', 'F', 'F'])
    # Third
    msg1 = encode(image_carrier.copy(), List_Of_Fake_Msgs[1])
    msg2 = encode(image_carrier.copy(), List_Of_Fake_Msgs[0])
    msg3 = encode(image_carrier.copy(), chunks[2])
    data = [msg1.tolist(), msg2.tolist(), msg3.tolist()]
    send_message(team_id, data, ['F', 'F', 'R'])


def get_riddle(team_id, riddle_id):
    '''
    In this function you will hit the api end point that requests the type of riddle you want to solve.
    use the riddle id to request the specific riddle.
    Note that:
        1. Once you requested a riddle you cannot request it again per game.
        2. Each riddle has a timeout if you didnot reply with your answer it will be considered as a wrong answer.
        3. You cannot request several riddles at a time, so requesting a new riddle without answering the old one
          will allow you to answer only the new riddle and you will have no access again to the old riddle.
    '''

    BASE_URL = "http://127.0.0.1:5000/fox"
    request = r.post(BASE_URL + "/get-riddle", json={"teamId": team_id, "riddleId": riddle_id})
    res = request.json()
    LogResponse(f"Riddle --> {riddle_id}:\n" + request.text)
    return res


def solve_riddle(team_id, solution):
    '''
    In this function you will solve the riddle that you have requested.
    You will hit the API end point that submits your answer.
    Use te riddle_solvers.py to implement the logic of each riddle.
    '''
    re = r.post(api_base_url + "/solve-riddle", json={"teamId": team_id, "solution": solution})
    LogResponse(f"Riddle Solves:\n" + re.text)
    return re.json()


def send_message(team_id, messages, message_entities=['F', 'E', 'R']):
    '''
    Use this function to call the api end point to send one chunk of the message.
    You will need to send the message (images) in each of the 3 channels along with their entites.
    Refer to the API documentation to know more about what needs to be send in this api call.
    '''
    req1 = r.post(api_base_url + "/send-message",
                  json={"teamId": team_id, "messages": messages, "message_entities": message_entities})
    LogResponse("Send Message:\n" + req1.text)
    return req1.text


def end_fox(team_id):
    '''
    Use this function to call the api end point of ending the fox game.
    Note that:
    1. Not calling this fucntion will cost you in the scoring function
    2. Calling it without sending all the real messages will also affect your scoring fucntion
      (Like failing to submit the entire message within the timelimit of the game).
    '''
    req1 = r.post(api_base_url + "/end-game", json={"teamId": team_id})
    LogResponse("End Fox Game:\n" + req1.text)
    return req1.text


def submit_fox_attempt(team_id):
    '''
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
    '''

    gamestarted = init_fox(team_id)
    Message = np.array(gamestarted["msg"])
    Img = gamestarted["carrier_image"]
    Img = np.array(Img)

    for x in riddle_solvers.keys():
        res = get_riddle(team_id, "sec_hard")
        input = res["test_case"]
        LogResponse(f"Riddle {x}:\n" + str(input))
        ans = riddle_solvers[x](input)
        solve_riddle(team_id, ans)

    generate_message_array(Message, Img)
    final = end_fox(team_id)
    LogResponse("End Fox Game:\n", final)
    print(final)
    pass


LogsFinal = []


def LogResponse(response_text):
    LogsFinal.append(response_text + "\n----------------------------------\n")


submit_fox_attempt(team_id)

# start = time.time()
# img = imread('D:/HackTrick/Sol/HackTrick24/SteganoGAN/sample_example/encoded.png')
# img = np.array(img)
# print(solve_sec_medium(img))
# end = time.time()

# print(end-start)

with open("LogsFile.txt", "a+") as f:
    for x in LogsFinal:
        f.write(x)

