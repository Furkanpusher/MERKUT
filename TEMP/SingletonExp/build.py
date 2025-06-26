"""
    Baglanti saglar, ucagi arm eder ve offroad moda gecis yapar.
"""
from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio

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

async def arm(drone):
    try:
        #await wait_until_ready(drone)
        print("ARM ediliyor...")
        await drone.action.arm()
        await asyncio.sleep(1)
        if await is_armed(drone):
            print("ARM edildi.")
        else:
            print("ARM basarisiz.")
    except Exception as e:
        print(f"ARM sirasinda bir hata olustu: {e}")

async def startOffBoardMode(drone):
    print("Offboard moda geçiliyor...")
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.7))
    await drone.offboard.start()
    print("Offboard moda geçildi")


async def wait_until_ready(drone):
    print("Sistem hazır mı diye kontrol ediliyor...")
    async for health in drone.telemetry.health_all_ok():
        if health:
            print("Sistem uçmaya hazır.")
            break
        await asyncio.sleep(1)
    
# Aracin arm edilip edilmedigini doner
async def is_armed(drone):
    async for armed in drone.telemetry.armed():
        return armed