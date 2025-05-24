from mods.Build import build, arm, connect, startOffBoardMode
from mavsdk.offboard import Attitude
test_sayisi = 4
success = 0
async def build_test() :
    drone = await build()

    if drone is None:
        print("Build basarisiz!")
        exit()

    print("Build basarili.")
    success += 1

    await connect_test(drone)
    await arm_test(drone)
    await startOffBoardMode_test(drone)

    print(f"build_test bitti. {success}/{test_sayisi}")

async def connect_test(drone):
    connect_success = False

    connect_success = await connect(drone)
    
    if connect_success:
        print("connect_test basarili.")
        success += 1
    else:
        print("connect_test basarisiz!")
        exit()

async def arm_test(drone):
    try:
        await arm(drone)
        if is_armed(drone):
            print("arm_test basarili.")
            success += 1
        else:
            print("arm_test basarisiz!")
    except Exception as e:
        print(f"arm_test sirasinda hata olustu: {e}")
        exit

async def startOffBoardMode_test(drone):
    try:
        await startOffBoardMode(drone)
        print("startOffBoard_test basarili.")
        success += 1
    except Exception as e:
        print(f"startOffBoard_test sirasinda hata olustu: {e}")

# Aracin arm edilip edilmedigini doner
async def is_armed(drone):
    async for armed in drone.telemetry.armed():
        return armed