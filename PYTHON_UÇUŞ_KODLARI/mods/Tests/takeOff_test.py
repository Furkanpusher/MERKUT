import asyncio
import sys
from mods.SimpleMovements import takeoff

test_sayisi = 1
success = 0
failure = False
raspberryPiAltitude = 0

async def takeOff_test(drone, 
                       target_altitude: int = 20,
                       altitude_enable: bool = False,
                       delta: int = 4):
    global success, failure, raspberryPiAltitude
    print("TAKEOFF TEST BASLATILDI\n")
    print(f"Hedef irtifa: {target_altitude}  -  Hata payi: {delta}")

    if altitude_enable:
        #async for position in drone.telemetry.position():
        #    altitude = abs(position.relative_altitude_m)
        #    break
        if raspberryPiAltitude > 5:
            print(f"Irtifa yerden yuksek!: {raspberryPiAltitude}")
            exit()

    await takeoff(drone, target_altitude)

    if altitude_enable:
        #async for position in drone.telemetry.position():
        #    altitude = abs(position.relative_altitude_m)
        #    break
        if target_altitude - delta <= raspberryPiAltitude <= target_altitude + delta:
            success += 1
            print("takeOff_test basarili.\n")
        else:
            print("takeOff_test basarisiz.\n")
            failure = True
    else:
        success += 1
        print("takeOff_test basarili.\n")
    if failure:
        sys.exit()

    print(f"TAKEOFF TEST SONLANDI. {success}/{test_sayisi}\n")
