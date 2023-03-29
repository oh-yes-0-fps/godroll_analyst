from dataclasses import dataclass
import multiprocessing
from multiprocessing.managers import DictProxy
import time
import asyncio
import os.path
from typing import Callable, Union

from src.util import log, log_err
import src.trainer as trainer
import src.crawler as crawler
from src.bungie_data_grabber import get_player_by_id, player_valid

@dataclass()
class perkInput:
    weapon_type_hash: int
    weapon_element_hash: int
    weapon_rpm: int
    perk_hash: int
    secondary_perk_hash: int
    all_available_perks: list[int]
    subclass_hash: int = 0

    def to_dict(self) -> dict:
        return {
            "weapon_type_hash": self.weapon_type_hash,
            "weapon_element_hash": self.weapon_element_hash,
            "weapon_rpm": self.weapon_rpm,
            "perk_hash": self.perk_hash,
            "other_perk_hash": self.secondary_perk_hash,
            "all_available_perks": tuple(self.all_available_perks),
            "subclass_hash": self.subclass_hash
        }

class PrintAnalytics:

    def __init__(self, topic: str, shared_data: DictProxy):
        self.dropped = False
        self.topic = "topic_"+topic
        self.last_update = time.time()
        self.fields:dict[str, Union[str, int, float]] = {}
        self.shared_data = shared_data

    def add_field(self, name:str, default: Union[str, int, float]) -> Callable[[Union[str, int, float]], None]:
        self.fields[name] = default
        self.__update()
        return lambda x: self.__update_field(name, x)

    def __update(self):
        if self.dropped:
            return
        self.shared_data[self.topic] = self.fields

    def __update_field(self, name, value):
        if self.dropped:
            return
        if name in self.fields:
            self.fields[name] = value
            self.__update()

    def drop_topic(self):
        if self.dropped:
            return
        self.shared_data[self.topic] = "dropped"
        self.dropped = True

    def format_output(self, _topics: dict[str, dict]):
        output = "-"*21 + "\n"
        for topic in _topics:
            if "topic" not in topic or _topics[topic] == "dropped":
                continue
            output += f"|_{topic.removeprefix('topic_')}_________________|\n"
            for field in _topics[topic]:
                output += "| " + f"{field:15}" + " : " + f" {_topics[topic][field]}\n"
        output += "-"*21
        return output

    def print(self):
        if time.time() - self.last_update < 1:
            return
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print(self.format_output(self.shared_data))
        self.last_update = time.time()


GLOBAL_DATA = {}


def write_global(key, value):
    try:
        global GLOBAL_DATA
        GLOBAL_DATA[key] = value
    except Exception as e:
        log_err(f"Gloabl data write error: {e}")


def read_global(key):
    try:
        global GLOBAL_DATA
        return GLOBAL_DATA[key]
    except Exception as e:
        log_err(f"Gloabl data read error: {e}")
        return None


LAST_PROCESS = 0
PROCESSES: list[multiprocessing.Process] = []


def crawler_main(tdata):
    crawler.scrape(tdata)


def trainer_main():
    _time = time.time()
    started_model = False
    model = None
    while True:
        if not (os.path.exists("database/players.json") and os.path.exists("database/players.json")):
            time.sleep(600)
            continue
        if not started_model:
            started_model = True
            model = trainer.GodrollModel()
        model.train()


def bungie_main():
    _time = time.time()
    while True:
        if read_global("players") is None:
            time.sleep(600)
            continue
        weapon_inputs = []
        for raw_player in read_global("players"):
            player = get_player_by_id(raw_player[0], raw_player[1])
            if not player_valid(player):
                continue


if __name__ == "__main__":
    start_time = time.time()

    print("Starting main process")
    analytics_data = multiprocessing.Manager().dict()

    player_data = multiprocessing.Manager().list()

    print("Starting sub processes")
    analytics = PrintAnalytics("Main", analytics_data)
    uptime = analytics.add_field("Program Uptime", f"{0:.3f}s")
    p = multiprocessing.Process(target=crawler_main, args=(analytics_data,))
    PROCESSES.append(p)
    p.start()
    # p = multiprocessing.Process(target=trainer_main)
    # PROCESSES.append(p)
    # p.start()
    # p = multiprocessing.Process(target=bungie_main)
    # PROCESSES.append(p)
    # p.start()
    # for proc in PROCESSES[LAST_PROCESS:]:
    #     proc.join()



    while True:
        uptime(time.time() - start_time)
        analytics.print()
