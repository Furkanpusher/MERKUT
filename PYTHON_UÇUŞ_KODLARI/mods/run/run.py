import asyncio
import threading
import sys

from mods.Build import build
from mods.SimpleMovements import straightFlight, takeoff
from mods.TurnXDegreeMod import turn_fixed_wing
from mavsdk.offboard import Attitude
from mavsdk import System
from mavsdk.offboard import OffboardError
from mavsdk.telemetry import FlightMode

should_run = False  # Global flag to start/stop the application
task = None         # Global variable for the asyncio task

async def run():
    global should_run

    drone = await build()
    print(f"kumanda bekleniyor")
    
    

    print("test")
    while True:
        if await check_offboard_mode(drone):
            await asyncio.sleep(10)
            break
        await asyncio.sleep(0.1)

    await drone.action.arm()
    await asyncio.sleep(1)
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 1))

    print("STRAIGHT FLIGHT BASLADI")
    # await straightFlight(drone, 5)
    print("STRAIGHT FLIGHT TAMAMLANDI")

    print("180 DERECE DONUS BASLADI")
    await turn_fixed_wing(drone, -15)
    print("basladi")
    await turn_fixed_wing(drone, 15)
    await turn_fixed_wing(drone, -40)
    await turn_fixed_wing(drone, 40)
    print("180 DERECE DONUS TAMAMLANDI")

async def check_offboard_mode(drone):
    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode == FlightMode.OFFBOARD:
            print("Drone OFFBOARD modunda!")
            return True
        else:
            print(f"Drone OFFBOARD modunda değil, mevcut mod: {flight_mode}")
            return False

def input_listener(loop):
    global should_run, task

    while True:
        input("Enter'a basarak başlat/durdur...\n")
        should_run = not should_run

        if should_run:
            print("Uygulama başlatılıyor...")
            task = asyncio.run_coroutine_threadsafe(run(), loop)
        else:
            print("Uygulama durduruluyor...")
            if task:
                task.cancel()

def main():
    loop = asyncio.new_event_loop()
    threading.Thread(target=input_listener, args=(loop,), daemon=True).start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Çıkılıyor...")
    finally:
        loop.stop()

if __name__ == "__main__":
    main()
