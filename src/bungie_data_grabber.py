import datetime
import pydest
import asyncio
from enum import Enum


class Platform(Enum):
    XBOX = 1
    PSN = 2
    STEAM = 3

    def from_value(value: int):
        if value == 1:
            return Platform.XBOX
        elif value == 2:
            return Platform.PSN
        elif value == 3:
            return Platform.STEAM
        else:
            raise ValueError("Invalid platform value")

destiny = pydest.Pydest("89c9db2c0a8b46449bb5e654b6e594d0")

async def get_player_by_id(platform: Platform, id: int):
    res = await destiny.api.get_profile(platform.value, id, [205, 204, 100])
    return res["Response"]

async def get_players_in_clan(clan_id: int) -> list[tuple[Platform, int]]:
    res = await destiny.api.get_members_of_group(clan_id)
    out = []
    for member in res["Response"]["results"]:
        out.append((Platform.from_value(member["destinyUserInfo"]["membershipType"]), member["destinyUserInfo"]["membershipId"]))
    return out


def player_valid(player: dict) -> bool:
    iso_time = player["profile"]["data"]["dateLastPlayed"]
    unix_time = int(datetime.datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ").timestamp())
    return unix_time > datetime.datetime.now().timestamp() - (60 * 60 * 24 * 30)