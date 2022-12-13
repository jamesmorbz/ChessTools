import email
import json
from pprint import pprint
from matplotlib import axes
import requests
import csv
import sys
import fileinput
import math
import os
import time
import pdb
import logging
import re
from bs4 import BeautifulSoup
import urllib.request
import decimal
import matplotlib.pyplot as plt
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email import encoders
from datetime import datetime
import pandas as pd
import yaml as yaml
from yaml.loader import Loader
from datetime import datetime
from pymongo import MongoClient
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import time
import random
import math
import chess

database_name = "ChessBackend"
collection_name = "Puzzles"


def fetch_puzzle_data():
    i = 1
    puzzle_data = {}
    user_rating = 2900
    how_many_puzzles = 100
    logging.info("Initializing Connection with MongoDB")
    myclient = MongoClient("localhost", 27017)
    mydb = myclient[database_name]
    mycol = mydb[collection_name]
    logging.info("Connected to MongoDB")
    logging.info(
        "Fetching Data for Ratings %s to %s" % (user_rating, user_rating + 200)
    )
    subset = mycol.find(
        {
            "$and": [
                {"rating": {"$gt": user_rating}},
                {"rating": {"$lt": user_rating + 200}},
            ]
        }
    )

    for doc in subset:
        if i > how_many_puzzles:
            break
        else:
            puzzle_data[i] = doc
            i += 1

    logging.info("Data Retrieved!")
    return puzzle_data


def fen_to_board(fen):
    board = []
    for row in fen.split("/"):
        crow = []
        for c in row:
            if c == " ":
                break
            elif c in "12345678":
                crow.extend(["--"] * int(c))
            elif c == "p":
                crow.append("bp")
            elif c == "P":
                crow.append("wp")
            elif c > "Z":
                crow.append("b" + c.upper())
            else:
                crow.append("w" + c)

        board.append(crow)
    return board


def random_number_gen(max_number):
    random_number = random.randint(1, max_number)
    return random_number


def set_logging_params():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    set_logging_params()
    logging.info("Set Logging Params")
    logging.info("Script Start")
    puzzle_data = fetch_puzzle_data()
    max_number = len(puzzle_data)
    counter = 0
    already_done = []
    logging.info("There is %s puzzles for you to play through" % str(max_number))
    while counter < max_number:
        random_num = random_number_gen(max_number)
        if random_num in already_done:
            continue
        else:
            already_done.append(random_num)
            random_puzzle_picked = puzzle_data[random_num]["fen"]
            # puzzle_position = fen_to_board(random_puzzle_picked) NOT CURRENTLY BEING USED. USING PY CHESS MODULE INSTEAD OF MY FUNCTION. Same thing though.
            logging.info(
                "Showing Puzzle Number %s out of %s"
                % (str(random_num), str(max_number))
            )
            print(chess.Board(random_puzzle_picked))
            # time.sleep(2)
            pprint("Answer is: %s" % puzzle_data[random_num]["moves"])
            counter += 1


if __name__ == "__main__":
    main()
