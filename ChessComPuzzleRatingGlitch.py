import requests
import json
import threading

def solve_tactic():
        PHPSESSID = "4fbadbb3ea0073ea6ff889bab3ddae7f"

        apex = "www.chess.com"
        urls = {"next_tactic": f"http://{apex}/callback/tactics/rated/next",
                "submit_tactic": f"https://{apex}/callback/tactics/submitMoves"}

        r = requests.get(url=urls["next_tactic"], cookies={'PHPSESSID': PHPSESSID})
        tactic = json.loads(r.content.decode())

        solution = {"_token":"Kl9JaIgqa4qnFTPiv3hak0lyElyS7_BgGFr6cM88IzQ",
                    "isSolvedWithHint":0,
                    "totalTime":0,
                    "moves":tactic['tcnMoveList'],
                    "tacticsProblemId":int(tactic['id'])}

        r = requests.post(url=urls['submit_tactic'],
                cookies={'PHPSESSID': PHPSESSID},
                json=solution)
        result = json.loads(r.content.decode())

        if (int(result['newRatingInfo']['user']['current']) > 100000): exit()

        print(f"""
        Problem ID: {tactic['id']}
        TCN Solution: {tactic['tcnMoveList']}
        Provisional: {tactic['isRatingProvisionalOrPreprovisional']}
        Result: {result['result']}
        Rating Change: +{result['newRatingInfo']['user']['change']}
        Rating Current: {result['newRatingInfo']['user']['current']}
        Streak: {result['newRatingInfo']['currentStreak']}
        """)

thread_count = 3
while True:
        threads = [ threading.Thread(target=solve_tactic) for i in range(thread_count) ]
        [ thread.start() for thread in threads ]
        [ thread.join() for thread in threads ] 