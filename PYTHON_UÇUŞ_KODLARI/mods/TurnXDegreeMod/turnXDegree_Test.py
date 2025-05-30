from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio

from mods.TurnXDegreeMod import turnXDegree_Func

success = 0
fail = False

async def turnXDegree_Test(drone,
                           thrust,
                     delta: int = 5):
    
    print("TURNXDEGREE TEST BASLADI\n")

    global success, fail

    turns = [90, 90, 180, 180, 325, 35, 772, -52, 0, 1, -1]
    differences = []
    test_sayisi = len(turns)

    for turn in turns:
        async for att in drone.telemetry.attitude_euler():
            orig_pitch = att.pitch_deg
            break
        
        await turnXDegree_Func.turn_fixed_wing(drone, turn, thrust)

        async for att in drone.telemetry.attitude_euler():
            new_pitch = att.pitch_deg
            break

        differences.append(orig_pitch-new_pitch)

        await asyncio.sleep(2)

    i = 1
    for diff in differences:
        if diff < delta:
            success += 1
            print(f"{i}. Turn Basarili")
        else:
            print(f"{i}. Turn Basarisiz! - Fark ({turns[i]}): {diff}")
            fail = True
        i = i+1
    print(f"\nTURNXDEGREE TEST SONLANDI. {success}/{test_sayisi}\n")
