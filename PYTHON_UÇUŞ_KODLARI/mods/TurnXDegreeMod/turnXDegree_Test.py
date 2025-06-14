from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio

from mods.TurnXDegreeMod import turn_fixed_wing

async def test_turns(drone):
    turns = [90, 90, 180, 180, 325, 35, 772, -52, 0, 1, -1]
    differences = []

    for turn in turns:
        async for att in drone.telemetry.attitude_euler():
            orig_pitch = att.pitch_deg
            break
        
        await turn_fixed_wing(drone, turn)

        async for att in drone.telemetry.attitude_euler():
            new_pitch = att.pitch_deg
            break

        differences.append(orig_pitch-new_pitch)

        await asyncio.sleep(2)

    i = 0
    for diff in differences:
        print(f"Fark {i+1} ({turns[i]}): {diff:.2f}  --  ", end="")
        if -5 <= diff <= 5:
            print("Basarili")
        else:
            print("Basarisiz")
        i += 1