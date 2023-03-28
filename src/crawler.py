
from selenium import webdriver
import json
from src.util import log_err

from util import log


def control_leaderboard(page: int) -> str:
    return f"https://destinytracker.com/destiny-2/leaderboards/seasonal/all/default?page={page}&playlist=10"

def trials_leaderboard(page: int) -> str:
    return f"https://destinytracker.com/destiny-2/leaderboards/seasonal/all/default?page={page}&playlist=84"

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

PAGE_COUNT =  int((PLAYER_COUNT / 2) / 100)

def scrape() -> bool:
    finished = True
    out_dict:list[tuple[int,int]] = []
    driver = webdriver.Chrome()
    try:
        for page in range(1, PAGE_COUNT + 1):
            driver.get(control_leaderboard(page))
            driver.implicitly_wait(2)
            for entry in range(1, 101):
                try:
                    href = driver.find_element(
                            "xpath", f"//*[@id=\"app\"]/div[2]/div[3]/div/main/div[3]/div[2]/div/div/div[1]/div[2]/table/tbody/tr[{entry}]/td[2]/div/a"
                        ).get_attribute("href").split("/")
                    out_dict.append((href[-1], platform_to_int(href[-2])))
                except Exception as e:
                    print(e)
                    break
        for page in range(1, PAGE_COUNT + 1):
            driver.get(trials_leaderboard(page))
            driver.implicitly_wait(2)
            for entry in range(1, 101):
                try:
                    href = driver.find_element(
                            "xpath", f"//*[@id=\"app\"]/div[2]/div[3]/div/main/div[3]/div[2]/div/div/div[1]/div[2]/table/tbody/tr[{entry}]/td[2]/div/a"
                        ).get_attribute("href").split("/")
                    out_dict.append((int(href[-1]), platform_to_int(href[-2])))
                except Exception as e:
                    print(e)
                    break
    except Exception as e:
        finished = False
        log_err(f"Error while scraping {e}")
    with open("database/players.json", "w") as f:
        log(f"Writing {len(out_dict)} players to database/players.json")
        json.dump(out_dict, f)
    driver.close()
    return finished

scrape()