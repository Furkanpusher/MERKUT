import asyncio
from mods.SimpleMovements import takeoff

async def takeOff_test(drone):
    
    print("TAKEOFF TEST BASLATILDI\n")

    takeoff(drone, 20)