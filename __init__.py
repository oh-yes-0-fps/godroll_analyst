from dataclasses import dataclass
import multiprocessing
import time
import asyncio
import os.path

from src.util import log, log_err
import src.trainer as trainer
import src.crawler as crawler
from bungie_data_grabber import get_player_by_id, player_valid


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
    _time = time.time()


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
    # p = multiprocessing.Process(target=crawler_main)
    # PROCESSES.append(p)
    # p.start()
    # p = multiprocessing.Process(target=trainer_main)
    # PROCESSES.append(p)
    # p.start()
    # p = multiprocessing.Process(target=bungie_main)
    # PROCESSES.append(p)
    # p.start()
    # for proc in PROCESSES[LAST_PROCESS:]:
    #     proc.join()
    crawler.scrape()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()
