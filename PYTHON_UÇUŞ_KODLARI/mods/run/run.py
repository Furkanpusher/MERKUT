import asyncio
from mods.Build import build
from mods.SimpleMovements import straightFlight, takeoff
from mods.TurnXDegreeMod import turn_fixed_wing

async def run():
    drone = await build()

    print("TAKEOFF BASLADI")
    await takeoff(drone)
    print("TAKEOFF TAMAMLANDI")

    print("STRAIGHT FLIGHT BASLADI")
    await straightFlight(drone, 5)
    print("STRAIGHT FLIGHT TAMAMLANDI")

    print("180 DERECE DONUS BASLADI")
    await turn_fixed_wing(drone, 180)
    print("180 DERECE DONUS TAMAMLANDI")

asyncio.run(run())