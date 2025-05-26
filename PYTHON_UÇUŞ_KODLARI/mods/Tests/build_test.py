import asyncio
import sys
from mods.Build import setup, arm, connect, startOffBoardMode
from mavsdk.offboard import Attitude
test_sayisi = 4
success = 0
failure = False
async def build_test() :
    global success

    print("BUILD TEST BASLATILDI\n")

    drone = await setup_test()
    await checkFailure()
    await connect_test(drone)
    await checkFailure()
    await startOffBoardMode_test(drone)
    await checkFailure()
    await arm_test(drone)
    await checkFailure()

    await printResult()
    return drone


async def setup_test():
    global success
    drone = await setup()
    if drone is None:
        print("setup_test basarisiz!\n")
    else:
        print("setup_test basarili.\n")
        success += 1
    return drone

async def connect_test(drone):
    global success
    connect_success = False

    connect_success = await connect(drone)
    
    if connect_success:
        print("connect_test basarili.\n")
        success += 1
    else:
        print("connect_test basarisiz!\n")
        failure = True

async def arm_test(drone):
    global success
    try:
        await arm(drone)
        if await is_armed(drone):
            print("arm_test basarili.\n")
            success += 1
        else:
            print("arm_test basarisiz!\n")
            failure = True
    except Exception as e:
        print(f"arm_test sirasinda hata olustu: {e}")
        failure = True

async def startOffBoardMode_test(drone):
    global success
    try:
        await startOffBoardMode(drone)
        print("startOffBoard_test basarili.\n")
        success += 1
    except Exception as e:
        print(f"startOffBoard_test sirasinda hata olustu: {e}")
        failure = True

# Aracin arm edilip edilmedigini doner
async def is_armed(drone):
    async for armed in drone.telemetry.armed():
        return armed
    
async def printResult():
    global success, test_sayisi
    print(f"BUILD TEST SONLANDI. {success}/{test_sayisi}\n")

async def checkFailure():
    global failure
    if failure:
        await printResult()
        sys.exit()
