# Add the necessary imports here
import time
import numpy as np
import pandas as pd
import torch
from SteganoGAN.utils import *
import pickle
import sys
import pandas as pd
import torch
import google.generativeai as genai
from word2number import w2n
import os
from sec_hard_solver import DES_encrypt
from PIL import Image
from cv_easy_solver import reorder_shards
from cv_med_solver import find_and_fill
from sklearn.cluster import DBSCAN

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

sys.path.insert(0, "SteganoGAN")
from SteganoGAN.utils import *
from statsmodels.tsa.arima.model import ARIMA

GOOGLE_API_KEY = "AIzaSyCAgAH6gJHxgceoOMmNoxnJ-kg-bqP5PKo"
genai.configure(api_key=GOOGLE_API_KEY)
vision_model = genai.GenerativeModel("gemini-pro-vision")


def solve_cv_easy(test_case: tuple) -> list:
    """
    This function takes a tuple as input and returns a list as output.

    Parameters:
    input (tuple): A tuple containing two elements:
        - A numpy array representing a shredded image.
        - An integer representing the shred width in pixels.

    Returns:
    list: A list of integers representing the order of shreds. When combined in this order, it builds the whole image.
    """
    shredded_image, shred_width = test_case
    shredded_image = np.array(shredded_image, dtype=np.uint8)
    order, batches = reorder_shards(shredded_image)
    return order


def solve_cv_medium(input: tuple) -> list:
    """
    This function takes a tuple as input and returns a list as output.

    Parameters:
    input (tuple): A tuple containing two elements:
        - A numpy array representing the RGB base image.
        - A numpy array representing the RGB patch image.

    Returns:
    list: A list representing the real image.
    """
    combined_image_array, patch_image_array = input
    combined_image = np.array(combined_image_array, dtype=np.uint8)
    patch_image = np.array(patch_image_array, dtype=np.uint8)
    res = find_and_fill(
        combined_image,
        patch_image,
        threshold=0.4,
        auto_scale=(0.05, 0.5, 0.01),
        fill_size=10,
    )
    return res


def solve_cv_hard(input: tuple) -> int:
    extracted_question, image = input
    image = np.array(image, dtype=np.uint8)
    image = Image.fromarray(image)
    """
    This function takes a tuple as input and returns an integer as output.

    Parameters:
    input (tuple): A tuple containing two elements:
        - A string representing a question about an image.
        - An RGB image object loaded using the Pillow library.

    Returns:
    int: An integer representing the answer to the question about the image.
    """
    start = time.time()
    response = vision_model.generate_content([extracted_question, image], stream=True)
    response.resolve()
    print("Time taken to get response from model: ", time.time() - start)
    print(response.text)

    ans = ""
    res = response.text
    print(res)
    words_list = res.split()
    for word in words_list:
        word = (
            word.replace(".", "")
            .replace(",", "")
            .replace("?", "")
            .replace("!", "")
            .replace(":", "")
            .replace(";", "")
        )
        try:
            w2n.word_to_num(word)
            ans += word + " "
            print(word, w2n.word_to_num(str(word)), "ans=", ans)

        except Exception as e:
            print(e)

    ans = w2n.word_to_num(ans)
    print(f"ans={ans}")

    return ans


def solve_ml_easy(input: pd.DataFrame) -> list:
    data = pd.DataFrame(input)

    """
    This function takes a pandas DataFrame as input and returns a list as output.

    Parameters:
    input (pd.DataFrame): A pandas DataFrame representing the input data.

    Returns:
    list: A list of floats representing the output of the function.
    """
    data.fillna(data.mode(), inplace=True)
    model = ARIMA(data["visits"], order=(1, 1, 1))

    # Fit the model to the training data
    model_fit = model.fit()

    # Forecast the number of attacks for the next 50 days
    predictions = model_fit.forecast(steps=50).astype(int)
    return predictions.tolist()


def solve_ml_medium(input: list) -> int:
    """
    This function takes a list as input and returns an integer as output.

    Parameters:
    input (list): A list of signed floats representing the input data.

    Returns:
    int: An integer representing the output of the function.
    """
    df = pd.read_csv("MlMediumTrainingData.csv")
    df.drop("class", axis=1, inplace=True)
    df.loc[len(df)] = input
    cluster = DBSCAN(eps=2, min_samples=5, leaf_size=112)
    cluster.fit(df)
    return int(cluster.labels_[-1])


def solve_sec_medium(input: torch.Tensor) -> str:
    img = torch.tensor(input)
    """
    This function takes a torch.Tensor as input and returns a string as output.

    Parameters:
    input (torch.Tensor): A torch.Tensor representing the image that has the encoded message.

    Returns:
    str: A string representing the decoded message from the image.
    """
    decoded_message = decode(img)  # Decode the message using the decode function
    if decoded_message:
        return decoded_message
    else:
        return "Failed to find message."


def solve_sec_hard(input: tuple) -> str:
    """
    This function takes a tuple as input and returns a list a string.

    Parameters:
    input (tuple): A tuple containing two elements:
        - A key
        - A Plain text.

    Returns:
    list:A string of ciphered text
    """

    res = DES_encrypt(input)
    return res


def solve_problem_solving_easy(input: tuple) -> list:
    words, X = input
    word_counts = {}

    # Count the frequency of each word
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    # Sort the words based on frequency and lexicographical order
    sorted_words = sorted(word_counts.keys(), key=lambda x: (-word_counts[x], x))

    # Return the X most recurring words
    return sorted_words[:X]


def solve_problem_solving_medium(input: str) -> str:
    """
    This function takes a string as input and returns a string as output.

    Parameters:
    input (str): A string representing the input data.

    Returns:
    str: A string representing the solution to the problem.
    """
    stack = []
    current_string = ""
    current_number = 0

    for char in input:
        if char.isdigit():
            current_number = current_number * 10 + int(char)
        elif char == "[":
            stack.append((current_string, current_number))
            current_string = ""
            current_number = 0
        elif char == "]":
            prev_string, prev_number = stack.pop()
            current_string = prev_string + current_string * prev_number
        else:
            current_string += char

    return current_string


def solve_problem_solving_hard(input: tuple) -> int:
    """
    This function takes a tuple as input and returns an integer as output.

    Parameters:
    input (tuple): A tuple containing two integers representing m and n.

    Returns:
    int: An integer representing the solution to the problem.
    """

    x, y = input
    dp = [[1 for _ in range(y)] for _ in range(x)]

    for i in range(1, x):
        for j in range(1, y):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    # Another Solution
    # nCr = x+y-2 C y-1

    return dp[x - 1][y - 1]


riddle_solvers = {
    "cv_easy": solve_cv_easy,
    "cv_medium": solve_cv_medium,
    "cv_hard": solve_cv_hard,
    "ml_easy": solve_ml_easy,
    "ml_medium": solve_ml_medium,
    "sec_medium_stegano": solve_sec_medium,
    "sec_hard": solve_sec_hard,
    "problem_solving_easy": solve_problem_solving_easy,
    "problem_solving_medium": solve_problem_solving_medium,
    "problem_solving_hard": solve_problem_solving_hard,
}
