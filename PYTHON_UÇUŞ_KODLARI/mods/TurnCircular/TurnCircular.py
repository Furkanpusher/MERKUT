from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio
import time

# 10 saniye saat yonunde
async def turn_circular_10_sec(drone):
    await turn_circular(drone, 10)

# 10 saniye saat yonunun tersine
async def turn_circular_neg_10_sec(drone):
    await turn_circular(drone, -10)

# 60 saniye saat yonunde
async def turn_circular_60_sec(drone):
    await turn_circular(drone, 60)

# 60 saniye saat yonunun tersine
async def turn_circular_neg_60_sec(drone):
    await turn_circular(drone, -60)

async def turn_circular(drone,
                                time: int = 10,
                                bank_angle_deg: float = 15.0,
                                default_pitch: float = 1.0,
                                normal_throttle: float = 0.7):

    initial_time = time.time()
    
    while time.time() - 10 <= initial_time:

        await drone.offboard.set_attitude(Attitude(bank_angle_deg, default_pitch, 0.0, normal_throttle))

        await asyncio.sleep(0.01)


    # Orijinal pitch ve throttle ile uçuşa devam
    print("[Manevra] Orijinal pitch ve throttle değerleri korunarak harekete devam ediliyor.")
    await drone.offboard.set_attitude(Attitude(0.0, default_pitch, 0.0, normal_throttle))