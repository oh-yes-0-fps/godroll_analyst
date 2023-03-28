
from enum import Enum
import urllib3
import html5lib
import json
import os.path

from util import log, log_err


class TrnActivityId(Enum):
    TRIALS = 84
    CONTROL = 10


def leaderboard(page: int, activity: TrnActivityId) -> str:
    return f"http://destinytracker.com/destiny-2/leaderboards/seasonal/all/default?page={page}&playlist={activity.value}"


def platform_to_int(platform: str) -> int:
    if platform == "xbl":
        return 1
    elif platform == "psn":
        return 2
    elif platform == "steam":
        return 3
    elif platform == "stadia":
        return 4
    else:
        raise ValueError("Invalid platform value")


PLAYER_COUNT = 12500
THREAD_COUNT = 5
PAGE_COUNT = int(PLAYER_COUNT / 100)


def scrape_urllib3_thread(page_start: int, page_end) -> bool:
    finished = True
    out_dict: list[tuple[int, int]] = []
    try:
        for page in range(page_start, page_end + 1):
            with urllib3.PoolManager() as http:
                for r in [http.request("GET", leaderboard(page, TrnActivityId.TRIALS)), http.request("GET", leaderboard(page, TrnActivityId.CONTROL))]:
                    # r = http.request("GET", leaderboard(page, TrnActivityId.CONTROL))
                    table_body = html5lib.parse(
                        r.data)[1][0][4][2][0][1][5][1][0][0][3][2][0][1]
                    for entry_index in range(0, 100):
                        try:
                            entry = table_body[entry_index]
                            href = entry[1][0][0].get("href").split("/")
                            elo = int(entry[3][0][0].tail.replace(
                                ",", "").replace(" ", ""))
                            out_dict.append(
                                (int(href[-1]), platform_to_int(href[-2]), elo))
                            log((href[-1], platform_to_int(href[-2])))
                        except Exception as e:
                            log_err(
                                f"Error while scraping (player iteration) {e}")
                            break
    except Exception as e:
        finished = False
        log_err(f"Error while scraping {e}")
    with open("database/players.json", "w") as f:
        if not os.path.exists("database"):
            os.mkdir("database")
        log(f"Writing {len(out_dict)} players to database/players.json")
        json.dump(out_dict, f)
    return finished


if __name__ == "__main__":
    scrape_urllib3_thread(1, PAGE_COUNT)
