import multiprocessing
import time
import asyncio
import os.path

from src.util import log, log_err
import src.trainer as trainer

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
    pass

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
    
    pass

if __name__ == "__main__":
    p = multiprocessing.Process(target=crawler_main)
    PROCESSES.append(p)
    p.start()
    p = multiprocessing.Process(target=trainer_main)
    PROCESSES.append(p)
    p.start()
    p = multiprocessing.Process(target=bungie_main)
    PROCESSES.append(p)
    p.start()
    for proc in PROCESSES[LAST_PROCESS:]:
        proc.join()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()