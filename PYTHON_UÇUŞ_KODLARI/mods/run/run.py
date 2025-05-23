import asyncio
from mods.Build import build, arm, startOffBoardMode
from mods.SimpleMovements import straightFlight, takeoff
from mods.TurnXDegreeMod import turn_fixed_wing

async def run():
    drone = await build()
    await arm(drone)
    print("ARM TAMAMLANDI")
    await startOffBoardMode(drone)  # Thrust saglandi
    print("OFFBOARD AÇILDI")

    await takeoff(drone)
    print("TAKEOFF TAMAMLANDI")

    await straightFlight(drone, 5)
    print("STRAIGHT FLIGHT TAMAMLANDI")
    await turn_fixed_wing(drone, 180)
    print("180 DERECE DONUS TAMAMLANDI")
asyncio.run(run())