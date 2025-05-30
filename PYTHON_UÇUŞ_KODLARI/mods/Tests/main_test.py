import asyncio
from mods.Tests import build_test, takeOff_test, straightFlight_test
from mods.TurnXDegreeMod import turnXDegree_Test

default_thrust = 0.7

async def main_test():

    print("MAIN TEST BASLATILIYOR ----------------------------------------")
    
    drone = await build_test()

    await takeOff_test(drone)

    await straightFlight_test(drone, default_thrust)

    await turnXDegree_Test(drone, default_thrust)

    print("MAIN TEST SONLANDI ----------------------------------------")

asyncio.run(main_test())
