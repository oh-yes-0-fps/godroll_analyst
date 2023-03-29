
from enum import Enum
import multiprocessing
from multiprocessing.managers import DictProxy
import time
import urllib3
import html5lib
import json
import os.path
import threading
from main import PrintAnalytics
from src.util import log, log_debug, log_err


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

__glbl_dict = {}
class __singleton_dict:
    @staticmethod
    def insert(key, value):
        global __glbl_dict
        __glbl_dict[key] = value

    @staticmethod
    def clear():
        global __glbl_dict
        __glbl_dict = {}

    @staticmethod
    def get_cpy():
        global __glbl_dict
        return __glbl_dict.copy()


PLAYER_COUNT = 12500
THREAD_COUNT = 5
PAGE_COUNT = int(PLAYER_COUNT / 100)


def __scraper_thread(page_start: int, page_end: int, players_grabbed: list[int], thread_id: int) -> bool:
    finished = True
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
                            __singleton_dict.insert(
                                int(href[-1]), (platform_to_int(href[-2]), elo))
                            log_debug(href[-1])
                            players_grabbed[thread_id] += 1
                        except Exception as e:
                            log_err(
                                f"Error while scraping (player iteration) {e}")
                            break
    except Exception as e:
        finished = False
        log_err(f"Error while scraping {e}")

    return finished


def scrape(tdata: DictProxy):
    analytics = PrintAnalytics("Scraper", tdata)
    start_time = time.time()
    players_grabbed = []
    for i in range(0, THREAD_COUNT):
        players_grabbed.append(0)
    updater1 = analytics.add_field("Uptime", time.time() - start_time)
    updater2 = analytics.add_field("Players Grabbed", players_grabbed[0])
    updater3 = analytics.add_field("Players/s", f"{players_grabbed[0] / (time.time()+0.1 - start_time):.3f}/s")
    __singleton_dict.clear()
    page_start = 1
    page_step = int(PAGE_COUNT / THREAD_COUNT)
    threads: list[threading.Thread] = []
    # make a mutex int u can share between threads 
    for i in range(0, THREAD_COUNT):
        threads.append(
            threading.Thread(target=__scraper_thread, args=(page_start, page_start + page_start, players_grabbed, i)))
        page_start += page_step
    for t in threads:
        t.start()
    while threading.active_count() > 1:
        time.sleep(1)
        try:
            updater1(time.time() - start_time)
            updater2(sum(players_grabbed))
            updater3(f"{sum(players_grabbed) / (time.time()+0.1 - start_time):.3f}/s")
        except:
            pass
    if not os.path.exists("database"):
        os.mkdir("database")
    out_dict = __singleton_dict.get_cpy()
    with open("database/players.json", "w") as f:
        log(f"Writing {len(out_dict)} players to database/players.json")
        json.dump(out_dict, f)
    analytics.drop_topic("Scraper")