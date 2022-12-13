import requests
import logging
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from datetime import datetime
import os



full_fide_stats = {}  # for the fide all stats function
graph_data_count = []  # for graphing matplotlib
graph_data_time = []  # for graphing  matplotlib


def create_all_month_year_combos():
    all_month_year_combos = []
    years = ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    for year in years:
        for month in months:
            all_month_year_combos.append("%s/%s" % (year, month))

    return all_month_year_combos


def get_chesscom_user_data(username):
    refined_user_data = {}
    chesscom_user_data = requests.get("https://api.chess.com/pub/player/%s" % username)
    chesscom_user_data = chesscom_user_data.json()
    username = chesscom_user_data["username"]
    country = chesscom_user_data["country"]
    country = country.split("/")[-1]
    refined_user_data[username] = {
        "username": chesscom_user_data["username"],
        "titles": chesscom_user_data.get("title"),
        "status": chesscom_user_data["status"],
        "country": country,
    }


def get_chesscom_games_data(username):
    all_month_year_combos = create_all_month_year_combos()
    pgn_file = open("%sAllChessComGames.pgn" % username, "w")
    game_index = 1
    bad_games_skipped = 0
    bad_games_skipped_list = []
    all_chesscom_games = {}
    for yearcombo in all_month_year_combos:
        chesscom_games_data = requests.get(
            "https://api.chess.com/pub/player/%s/games/%s" % (username, yearcombo)
        )
        chesscom_games_data = chesscom_games_data.json()
        try:
            for game in chesscom_games_data["games"]:
                try:
                    all_chesscom_games[game_index] = game["pgn"].split("\n")
                    for row in all_chesscom_games[game_index]:
                        if "[ECOUrl" not in row:
                            pgn_file.write(row)
                            pgn_file.write("\n")
                    game_index += 1
                except:
                    bad_white = game["white"]["username"]
                    bad_black = game["white"]["username"]
                    bad_game = "%s vs %s" % (bad_white, bad_black)
                    bad_games_skipped_list.append(bad_game)
                    bad_games_skipped += 1

            graph_data_count.append(len(chesscom_games_data["games"]))
            graph_data_time.append(yearcombo)
            logging.info(
                "%s Games Played in this month - %s"
                % (str(len(chesscom_games_data["games"])), yearcombo)
            )

        except:
            logging.info("Maybe dead API or dead account?! - %s" % yearcombo)

    logging.info(
        "There are %s games in total for the given user - %s - %s"
        % (str(game_index - 1), all_month_year_combos[0], all_month_year_combos[-1])
    )
    if bad_games_skipped > 0:
        logging.info("Skipped %s games due to Bad API Return" % str(bad_games_skipped))

    return all_chesscom_games


def plot_chesscom_activity(username):

    plt.rcParams.update(
        {
            "font.size": 8,
            "xtick.major.size": 8,
            "xtick.major.width": 2,
            "ytick.major.size": 8,
            "ytick.major.width": 2,
        }
    )
    plt.plot(graph_data_time, graph_data_count)
    plt.xlabel("Year/Month")
    plt.xticks(graph_data_time[::6], rotation=90)
    plt.grid(axis="y")
    plt.ylabel("Number of Games Played in Month")
    plt.title("Chess.com Activity Over Time - %s" % username)
    plt.savefig("%sOnlineChessActivity.png" % username, bbox_inches="tight")


def export_data_in_email(username, recipient):

    logging.info("Constructing Email...")
    
    dir_path = "E:\\Coding\\"
    files = [
        "%sAllChessComGames.pgn" % username,
        "%sOnlineChessActivity.png" % username,
    ]

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    sender = "automatedpgns@gmail.com"
    recipient = recipient
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = "Automated PGN Sending Server - Account %s" % username
    body = (
        "THIS MESSAGE IS AUTOMATED \n \nSending PGN for chess.com account: %s. \n \nThis message was sent at %s \n \nPlease report any bugs to automatedpgns@gmail.com \n \nThanks for using this service!\n \nAutomated PGN Sending Server"
        % (username, dt_string)
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


def cleaning_up_files(username):
    dir_path = "D:\James\ChessProject"
    files = [
        "%sAllChessComGames.pgn" % username,
        "%sOnlineChessActivity.png" % username,
    ]
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
    set_logging_params()
    logging.info("Set Logging Params")
    logging.info("Script Start")
    username = "TonRicher"
    recipient_email = "jamesmoreby1gmail.com"
    logging.info("Human Input Declared")

    get_chesscom_user_data(username)
    get_chesscom_games_data(username)
    plot_chesscom_activity(username)

    export_data_in_email(username, recipient_email)
    # cleaning_up_files(username)


if __name__ == "__main__":
    main()
