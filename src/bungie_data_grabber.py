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

async def main():
    destiny = pydest.Pydest("89c9db2c0a8b46449bb5e654b6e594d0")

    async def get_player_by_id(platform: Platform, id: int):
        return await destiny.api.get_profile(platform.value, id, [205, 204])

    async def get_player_by_id(combined_id: tuple[Platform, int]):
        return await destiny.api.get_profile(combined_id[0].value, combined_id[0], [205, 204])

    async def get_players_in_clan(clan_id: int) -> list[tuple[Platform, int]]:
        res = await destiny.api.get_members_of_group(clan_id)
        out = []
        for member in res["Response"]["results"]:
            out.append((Platform.from_value(member["destinyUserInfo"]["membershipType"]), member["destinyUserInfo"]["membershipId"]))
        return out

    print(res)

    return destiny.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()