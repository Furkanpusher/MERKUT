import asyncio
import threading
import time
from mavsdk import System
from mavsdk.telemetry import EulerAngle

# Drone objesi her thread için burada tanımlanabilir veya global olabilir
drone = System()

async def get_attitude():
    # Drone bağlantısı (gerçek kullanımda başta yapılmalı)

    # 10 saniye boyunca attitude oku
    start_time = time.time()
    async for att in drone.telemetry.attitude_euler():
        pitch = att.pitch_deg
        yaw = att.yaw_deg
        roll = att.roll_deg
        print(f"Pitch: {pitch}, Yaw: {yaw}, Roll: {roll}")
        
        if time.time() - start_time > 10:
            break

def thread_function():
    asyncio.run(get_attitude())

async def main():
    n = int(input("Kaç thread oluşturulsun? "))
    threads = []

    drone = await build()

    for i in range(n):
        t = threading.Thread(target=thread_function)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

async def build():
    drone = await setup()
    await connect(drone)
    #await arm(drone)
    #await startOffBoardMode(drone)
    return drone

async def setup():
    drone = System()
    return drone

async def connect(drone):
    print("baglanacak")
    #await drone.connect(system_address="serial:///dev/ttyACM2:57600")       # Raspberry
    await drone.connect(system_address="udp://:14540")                     # Gazebo
    print("Bağlantı bekleniyor...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Bağlandı!")
            return True

if __name__ == "__main__":
    main()
