import email
import json
import pprint
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
import pymongo
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from time import time


def get_chessgames_games(fide_id):
    index = 1
    otb_games = open("%sOTBGames.pgn" % fide_id, "w")
    all_chessgames_data = {}
    query0 = "https://chessabc.com/getgames/%s/0" % fide_id
    try:
        chessgames_data0 = requests.get(query0)
        chessgames_data0 = chessgames_data0.json()
    except:
        print("Bad Response from Server 0 - API Dead?")
    query1 = "https://chessabc.com/getgames/%s/1" % fide_id
    try:
        chessgames_data1 = requests.get(query1)
        chessgames_data1 = chessgames_data1.json()
    except:
        print("Bad Response from Server 1 - API Dead?")
    combined_chessgames_data = chessgames_data0 + chessgames_data1
    try:
        for game in combined_chessgames_data:
            date = game["date"].split("T")[0]
            all_chessgames_data[index] = {
                "white": game["white"],
                "white_elo": game["white_elo"],
                "black": game["black"],
                "black_elo": game["black_elo"],
                "result": game["result"],
                "date": date,
                "eco": game["eco"],
                "event": game["event"],
                "moves": game["moves"],
            }
            try:
                otb_games.write('[Event "%s"] \n' % game["event"])
                otb_games.write('[White "%s"] \n' % game["white"])
                otb_games.write('[Black "%s"] \n' % game["black"])
                otb_games.write('[Result "%s"] \n' % game["result"])
                otb_games.write('[WhiteElo "%s"] \n' % game["white_elo"])
                otb_games.write('[BlackElo "%s"] \n' % game["black_elo"])
                otb_games.write('[ECO "%s"] \n' % game["eco"])
                otb_games.write('[Date "%s"] \n \n' % date)
                otb_games.write("%s \n \n " % game["moves"])
            except:
                print("Error while writing file")

            index += 1
    except:
        print("API Didn't return expected data - No Games in Database?")
        print("Trying again with different Parameters...")
        try:
            pass
        except:
            pass


def export_data_in_email(fide_id, recipient):
    logging.info("Constructing Email...")

    dir_path = "D:\James\ChessProject"
    files = [
        "%sOTBGames.pgn" % fide_id,
    ]

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    sender = "automatedpgns@gmail.com"
    recipient = recipient
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = "Automated PGN Sending Server - FIDE ID: %s" % fide_id
    body = (
        "THIS MESSAGE IS AUTOMATED \n \nSending PGN for FIDE ID: %s. \n \nThis message was sent at %s \n \nPlease report any bugs to automatedpgns@gmail.com \n \nThanks for using this service!\n \nAutomated PGN Sending Server"
        % (fide_id, dt_string)
    )
    msg.attach(MIMEText(body, "plain"))

    for f in files:  # add files to the message
        file_path = os.path.join(dir_path, f)
        attachment = MIMEApplication(open(file_path, "rb").read(), _subtype="txt")
        attachment.add_header("Content-Disposition", "attachment", filename=f)
        msg.attach(attachment)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(sender, "uiopqwerty169")
    text = msg.as_string()
    try:
        s.sendmail(sender, recipient, text)
        logging.info("Email sent to %s" % recipient)
    except:
        logging.info(
            "Unable to send mail. File size was probably too big. Limit is 25 MB"
        )
    s.quit()


def cleaning_up_files(fide_id):
    dir_path = "D:\James\ChessProject"
    files = ["%sOTBGames.pgn" % fide_id]
    for f in files:  # add files to the message
        file_path = os.path.join(dir_path, f)
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info("File Deleted - %s" % file_path)
        else:
            logging.info("No File Existed - %s" % file_path)


def set_logging_params():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    fide_id = "427756"
    recipient_email = "karenmoreby@hotmail.com"
    set_logging_params()
    logging.info("Set Logging Params")

    get_chessgames_games(fide_id)

    export_data_in_email(fide_id, recipient_email)
    cleaning_up_files(fide_id)


if __name__ == "__main__":
    main()
