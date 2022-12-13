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
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import pandas as pd
import yaml as yaml
from yaml.loader import Loader
from datetime import datetime

full_fide_stats = {}  # for the fide all stats function
graph_data_count = []  # for graphing matplotlib
graph_data_time = []  # for graphing  matplotlib

# TODO read Country code + Country from an API


def reading_csv_to_dict():
    with open('E:\Learning\WeatherAPP\Country-CountryCode.csv', mode='r') as infile:
        reader = csv.reader(infile)
        c_cc_dict = {rows[0]: rows[1] for rows in reader}


def email_input():
    email_address = input("Email Address for Automated PGN Sending Service: ")
    print("Please Check Your Input and Make Sure It's Correct => %s" %
          email_address)
    proceed = input("Good Input? (\"YES\" to confirm) ")
    if proceed != "YES":
        print("Input not confirmed")
        return email_input()

    return email_address


def chesscom_username_input():
    chesscom_username = input("Enter chess.com username: ")
    regex = r'^[A-Za-z0-9]*$'
    if re.search(regex, chesscom_username):
        print("Please Check Your Input and Make Sure It's Correct => %s" %
              chesscom_username)
        proceed = input("Good Input? (\"YES\" to confirm) ")
        if proceed == "YES":
            return chesscom_username
        else:
            print("Input not confirmed")
            return chesscom_username_input()
    else:
        print("Invalid Chess.com Username. Please try again.")
        return chesscom_username_input()


def create_all_month_year_combos():
    all_month_year_combos = []
    years = ["2013", "2014", "2015", "2016",
             "2017", "2018", "2019", "2020", "2021"]
    months = ["01", "02", "03", "04", "05",
              "06", "07", "08", "09", "10", "11", "12"]

    for year in years:
        for month in months:
            all_month_year_combos.append("%s/%s" % (year, month))

    return all_month_year_combos


def get_chesscom_user_data(username):
    refined_user_data = {}
    chesscom_user_data = requests.get(
        "https://api.chess.com/pub/player/%s" % username)
    chesscom_user_data = chesscom_user_data.json()
    username = chesscom_user_data["username"]
    country = chesscom_user_data["country"]
    country = country.split("/")[-1]
    refined_user_data[username] = {
        "username": chesscom_user_data["username"],
        # "titles" : chesscom_user_data["title"],
        "status": chesscom_user_data["status"],
        "country": country
    }
    pprint.pprint(refined_user_data[username])


def get_chesscom_games_data(username):
    all_month_year_combos = create_all_month_year_combos()
    pgn_file = open('%sAllChessComGames.pgn' % username, 'w')
    game_index = 1
    bad_games_skipped = 0
    bad_games_skipped_list = []
    all_chesscom_games = {}
    for yearcombo in all_month_year_combos:
        chesscom_games_data = requests.get(
            "https://api.chess.com/pub/player/%s/games/%s" % (username, yearcombo))
        chesscom_games_data = chesscom_games_data.json()
        try:
            for game in chesscom_games_data["games"]:
                try:
                    all_chesscom_games[game_index] = game['pgn'].split("\n")
                    for row in all_chesscom_games[game_index]:
                        if "[ECOUrl" not in row:
                            pgn_file.write(row)
                            pgn_file.write("\n")
                    game_index += 1
                except:
                    bad_white = game["white"]["username"]
                    bad_black = game["white"]["username"]
                    bad_game = ("%s vs %s" % (bad_white, bad_black))
                    bad_games_skipped_list.append(bad_game)
                    bad_games_skipped += 1

            graph_data_count.append(len(chesscom_games_data["games"]))
            graph_data_time.append(yearcombo)
            print("%s Games Played in this month - %s" %
                  (str(len(chesscom_games_data["games"])), yearcombo))

        except:
            print("Maybe dead API or dead account?! - %s" % yearcombo)

    print("There are %s games in total for the given user - %s - %s" %
          (str(game_index-1), all_month_year_combos[0], all_month_year_combos[-1]))
    if bad_games_skipped > 0:
        print("Skipped %s games due to Bad API Return" %
              str(bad_games_skipped))

    return all_chesscom_games


def plot_chesscom_activity(username):

    plt.rcParams.update({
        'font.size': 8,
        'xtick.major.size': 8,
        'xtick.major.width': 2,
        'ytick.major.size': 8,
        'ytick.major.width': 2,
    })
    plt.plot(graph_data_time, graph_data_count)
    plt.xlabel('Year/Month')
    plt.xticks(graph_data_time[::6], rotation=90)
    plt.grid(axis='y')
    plt.ylabel('Number of Games Played in Month')
    plt.title('Chess.com Activity Over Time - %s' % username)
    plt.savefig('OnlineChessActivity%s.png' % username, bbox_inches="tight")


def fide_name_input():
    surname = input("Enter Surname: ")
    regex = r'^[A-Za-z-]*$'
    if re.search(regex, surname):
        print("Please Check Your Input and Make Sure It's Correct => %s" % surname)
        proceed = input("Good Input? (\"YES\" to confirm) ")
        if proceed != "YES":
            print("Input not confirmed")
            return fide_name_input()

        return surname

    else:
        print("Invalid Surname. Please try again.")
        return fide_name_input()


def get_fide_details():
    surname = fide_name_input()
    index = 0
    fide_query_names = []
    fide_query_links = []
    fide_query_fideID = []
    fide_availible_people = {}
    fide_page = ('https://fide.com/search?query=' + surname)
    url = urllib.request.urlopen(fide_page)
    soup = BeautifulSoup(url, 'html.parser')
    names = soup.find_all(
        'div', attrs={'class': 'member-block-info-position ng-star-inserted'})
    links = soup.find_all('a', attrs={'class': 'member-block-text'})
    for row_n in names:
        clean_name = re.split('> |<', str(row_n))[-2]
        fide_query_names.append(clean_name)
    for row_l in links:
        parse_links = re.split('> |<', str(row_l))
        for row_l1 in parse_links:
            if "href=" in row_l1:
                clean_link = row_l1.split('href=')[1]
                clean_link = clean_link[1:-2]
                fide_query_links.append(clean_link)
                fideID = clean_link.split("/")[-1]
                fide_query_fideID.append(fideID)

    for fideID in fide_query_fideID:
        fide_availible_people[fideID] = {
            "link": fide_query_links[index],
            "name": fide_query_names[index],
        }
        index += 1

    return fide_availible_people


def get_fide_stats():
    fide_availible_people = get_fide_details()
    if fide_availible_people == {}:
        print("No People In FIDE Database under that name.")
        try_again = input(
            "Would you like to try again with a different surname? (\"YES\" to try again) ")
        if try_again == "YES":
            return get_fide_stats()
        else:
            sys.exit(1)
    print("Options for FIDE IDs:")
    pprint.pprint(fide_availible_people)
    user_confirmed_id = input(
        "Please input the ID you want to fetch stats for: ")
    if user_confirmed_id not in fide_availible_people.keys():
        print("FIDE ID you typed did not match query return. Try Again.")
        return get_fide_stats()

    print("Fetching stats for FIDE ID: %s  NAME: %s " %
          (user_confirmed_id, fide_availible_people[user_confirmed_id]["name"]))
    return user_confirmed_id


def get_fide_page_specific_stats(fide_id):
    current_time = datetime.now()
    current_time = current_time.strftime("%d/%b/%Y")
    REGEX1 = re.compile(r'<[^>]+>')
    REGEX2 = re.compile(r'\s')
    query = "https://ratings.fide.com/profile/%s" % fide_id
    url = urllib.request.urlopen(query)
    soup = BeautifulSoup(url, 'html.parser')
    fide_name = str(soup.find_all(
        'div', attrs={'class': 'col-lg-8 profile-top-title'}))
    all_stats = str(soup.find_all(
        'div', attrs={'class': 'col-lg-12 profile-top-info'}))
    all_ratings = str(soup.find_all(
        'div', attrs={'class': 'col-lg-12 profile-top-ratingCont'}))
    fide_name = REGEX1.sub('', fide_name)
    all_stats = REGEX1.sub('', all_stats)
    all_ratings = REGEX1.sub('', all_ratings)
    fide_name = REGEX2.sub('', fide_name).strip("[ ]")
    all_stats_col = all_stats.strip("[ ]").split(":")
    all_stats = all_stats.strip("[ ]").split()
    all_ratings = all_ratings.strip("[ ]").split()
    full_fide_stats[fide_id] = {
        "full_name": fide_name,
        "fide_id": fide_id,
        "surname": fide_name.split(",")[0],
        "world_rank": all_stats[3],
        "federation": all_stats[5],
        "b_year": all_stats[10],
        "gender": all_stats[12],
        "fide_title": all_stats[15],
        "rating_std": all_ratings[2],
        "rating_rapid": all_ratings[4],
        "rating_blitz": all_ratings[6],
        "timestamp" : current_time
    }

    pprint.pprint(full_fide_stats)

    return full_fide_stats


def get_fide_rating_month_data(fide_id):
    query = "https://ratings.fide.com/a_calculations.phtml?event=%s" % fide_id

    r = requests.get(query)
    # this parses all the tables in webpages to a list
    df_list = pd.read_html(r.text)
    all_df = df_list[0]
    all_df = all_df.iloc[1:]
    all_df['Period'] = pd.to_datetime(all_df['Period'], format='%B %Y').dt.date
    availible_standard_games = all_df[all_df.Standard.str.contains(
        "No Games") == False].drop(["Standard", "Rapid", "Blitz"], axis=1)
    availible_rapid_games = all_df[all_df.Rapid.str.contains(
        "No Games") == False].drop(["Standard", "Rapid", "Blitz"], axis=1)
    availible_blitz_games = all_df[all_df.Blitz.str.contains(
        "No Games") == False].drop(["Standard", "Rapid", "Blitz"], axis=1)
    availible_standard_games_months = availible_standard_games.values.tolist()
    availible_rapid_games_months = availible_rapid_games.values.tolist()
    availible_blitz_games_months = availible_blitz_games.values.tolist()
    pdb.set_trace()
    # TODO SOMETHING HERE


def get_all_fide_opponents(fide_id):
    all_played = {}
    query = "https://ratings.fide.com/a_data_opponents.php?pl=%s" % fide_id
    all_opponent_data = requests.get(query)
    all_opponent_data = all_opponent_data.json()

    for opponent in all_opponent_data:
        all_played[opponent["name"]] = {
            "country": opponent["country"],
            "fide_id": opponent["id_number"],
            "name": opponent["name"],
        }

    return all_played


def fide_profile_analytics():
    pass


def rating_change_calc():
    user_fide_rating = float(input("Enter Your FIDE Rating:  "))
    opponent_fide_rating = float(input("Enter Opponent's FIDE Rating:  "))
    k_factor = float(input("Enter your K-factor:  "))

    expected_score_for_user = 1.0 / \
        (1.0 + 10.0 ** ((user_fide_rating-opponent_fide_rating)/400))
    potential_scores = [1.0, 0.5, 0.0]
    rating_changes = []
    new_ratings = []

    for actual_user_score in potential_scores:
        new_rating = float(user_fide_rating + k_factor *
                           (actual_user_score-expected_score_for_user))
        new_ratings.append(new_rating)
        rating_change = (user_fide_rating + new_rating)
        rating_changes.append(rating_change)

    print("Exact Rating: Change: Win: %.2f, Draw: %.2f, Loss: %.2f" %
          (rating_changes[2], rating_changes[1], rating_changes[0]))
    print("New Ratings: Win: %.2f, Draw: %.2f, Loss: %.2f" %
          (new_ratings[0], new_ratings[1], new_ratings[2]))


def export_data_in_email(username, recipient):
    #email = email_input()
    print("Sending Email...")
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    sender = "automatedpgns@gmail.com"
    recipient = recipient
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Automated PGN Sending Server - Account %s" % username
    body = "THIS MESSAGE IS AUTOMATED \n \nSending PGN for chess.com account: %s. \n \nThis message was sent at %s \n \nPlease report any bugs to automatedpgns@gmail.com \n \nThanks for using this service!\n \nAutomated PGN Sending Server" % (
        username, dt_string)
    msg.attach(MIMEText(body, 'plain'))
    pgn_filename = '%sAllChessComGames.pgn' % username
    # matplot_filename = 'OnlineChessActivity%s.png' % username #TODO
    pgn_attachment = open(
        'E:\ChessProject\%sAllChessComGames.pgn' % username, "rb")
    # matplot_attachment = open('E:\ChessProject\OnlineChessActivity%s.png' % username , "rb") #TODO
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((pgn_attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition',
                 "attachment; filename= %s" % pgn_filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender, "uiopqwerty169")
    text = msg.as_string()
    try:
        s.sendmail(sender, recipient, text)
        print("Email sent to %s" % recipient)
    except:
        print("Unable to send mail. File size was probably too big. Limit is 25 MB")
    s.quit()


def get_chessgames_games(fide_id):
    index = 1
    otb_games = open('%s - OTBGames.pgn' % fide_id, 'w')
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
                otb_games.write("[Event \"%s\"] \n" % game["event"])
                otb_games.write("[White \"%s\"] \n" % game["white"])
                otb_games.write("[Black \"%s\"] \n" % game["black"])
                otb_games.write("[Result \"%s\"] \n" % game["result"])
                otb_games.write("[WhiteElo \"%s\"] \n" % game["white_elo"])
                otb_games.write("[BlackElo \"%s\"] \n" % game["black_elo"])
                otb_games.write("[ECO \"%s\"] \n" % game["eco"])
                otb_games.write("[Date \"%s\"] \n \n" % date)
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

def hello():
    
    hello = "hello world"

    return hello


def main():
    yaml_file = open("E:\ChessProject\config.yaml")
    user_defined_config = yaml.load(yaml_file, Loader)
    #fide_id = get_fide_stats()
    get_fide_page_specific_stats(user_defined_config["fide_id"])
    all_rating_month_data = get_fide_rating_month_data(
        user_defined_config["fide_id"])
    all_opponents_played = get_all_fide_opponents(
        user_defined_config["fide_id"])
    fide_profile_analytics()

    #chesscom_username = chesscom_username_input()
    all_chesscom_games = get_chesscom_games_data(
        user_defined_config["username"])
    plot_chesscom_activity(user_defined_config["username"])

    get_chessgames_games(user_defined_config["fide_id"])

    export_data_in_email(
        user_defined_config["username"], user_defined_config["email"])


if __name__ == "__main__":
    main()