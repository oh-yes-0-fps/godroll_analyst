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

    def __init__(self, topic: str):
        self.program_init_time = time.time()
        self.last_update = self.program_init_time
        self.fields:dict[str, Union[str, int, float]] = {}
        self.shared_data = shared_state
        self.lock = shared_state_lock
        with self.lock:
            self.shared_data["print_topics"] = {}
        self.add_field("General", "Program Uptime", time.time() - self.program_init_time)

    def add_field(self, name:str, default: Union[str, int, float]) -> Callable[[Union[str, int, float]], None]:
        self.fields[name] = default
        self.__update()
        return lambda x: self.__update_field(name, x)

    def __update(self):
        self.topics = g_topics
        for topic in g_topics:
            self.shared_data["print_topics"][topic] = g_topics[topic]

    def __update_field(self, name, value):
        g_topics: dict = self.shared_data["print_topics"]
        g_topics[topic][name] = valuey
        self.__update(g_topics)

    def drop_topic(self, topic:str):
        g_topics: dict = self.shared_data["print_topics"]
        if topic in g_topics:
            del g_topics[topic]
        self.__update(g_topics)

    def format_output(self):
        print(f"Formatting output (topics are {self.topics.keys()})")
        output = "-"*21 + "\n"
        for topic in self.topics:
            output += f"|_{topic:15}_|\n"
            for field in self.topics[topic]:
                output += "| " + f"{field:15}" + " : " + f" {self.topics[topic][field]}\n"
        output += "-"*21
        return output
    
    def print(self):
        self.__update_field("General", "Program Uptime", time.time() - self.program_init_time)
        if time.time() - self.last_update < 1:
            return
        self.last_update = time.time()
        os.system("cls")
        print(self.format_output())


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


def crawler_main():
    crawler.scrape()


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
    shared_state = multiprocessing.Manager().dict()
    shared_state_lock = multiprocessing.Lock()

    analytics = PrintAnalytics(multiprocessing.Manager().dict())
    p = multiprocessing.Process(target=crawler_main)
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
        analytics.print()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()
