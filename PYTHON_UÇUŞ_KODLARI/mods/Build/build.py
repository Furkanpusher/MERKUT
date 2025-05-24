"""
    Baglanti saglar, ucagi arm eder ve offroad moda gecis yapar.
"""
from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio



async def build():
    drone = System()
    await connect(drone)
    return drone 

async def connect(drone):
    await drone.connect(system_address="udp://:14540")

    print("Bağlantı bekleniyor...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Bağlandı!")
            return True

async def arm(drone):
    try:
        print("ARM ediliyor...")
        await drone.action.arm()
    except Exception as e:
        print(f"ARM başarısız: {e}")
        exit

async def startOffBoardMode(drone):
    print("Offboard moda geçiliyor...")
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.7))
    await drone.offboard.start()