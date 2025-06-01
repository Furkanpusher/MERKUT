import asyncio
import sys
from mods.SimpleMovements import takeoff

test_sayisi = 1
success = 0
failure = False

async def takeOff_test(drone, 
                       target_altitude: int = 20,
                       delta: int = 4):
    global success, failure
    print("TAKEOFF TEST BASLATILDI\n")
    print(f"Hedef irtifa: {target_altitude}  -  Hata payi: {delta}")

    async for position in drone.telemetry.position():
        altitude = abs(position.relative_altitude_m)
        break
    
    if altitude > 5:
        print(f"Irtifa yerden yuksek!: {altitude}")
        exit()

    await takeoff(drone, target_altitude)

    async for position in drone.telemetry.position():
        altitude = abs(position.relative_altitude_m)
        break
    
    if target_altitude - delta <= altitude <= target_altitude + delta:
        success += 1
        print("takeOff_test basarili.\n")
    else:
        print("takeOff_test basarisiz.\n")
        failure = True

    if failure:
        sys.exit()

    print(f"TAKEOFF TEST SONLANDI. {success}/{test_sayisi}\n")
