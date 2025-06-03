
import sys
from mods.SimpleMovements import straightFlight

test_sayisi = 1
success = 0
failure = False

async def straightFlight_test(drone,
                              altitude_enable: bool = False,
                              altitude_delta: int = 5,
                              other_delta: int = 1):

    global success, test_sayisi, failure

    print("STRAIGHT FLIGHT TEST BASLADI\n")

    if altitude_enable:
        async for position in drone.telemetry.position():
            altitude = abs(position.relative_altitude_m)
            break
    async for att in drone.telemetry.attitude_euler():
        yaw = att.yaw_deg
        roll = att.roll_deg
        break

    await straightFlight(drone, 5)

    if altitude_enable:
        async for position in drone.telemetry.position():
            new_altitude = abs(position.relative_altitude_m)
            break
    async for att in drone.telemetry.attitude_euler():
        new_yaw = att.yaw_deg
        new_roll = att.roll_deg
        break

    if altitude_enable:
        altitude_diff = abs(new_altitude - altitude)
    yaw_diff = abs(new_yaw - yaw)
    roll_diff = abs(new_roll - roll)

    if altitude_enable and altitude_diff > altitude_delta:
        failure = True
    elif yaw_diff > other_delta or roll_diff > other_delta:
        failure = True
    else:
        print("straigthFlight_test basarili.\n")
        success += 1

    if failure:
        print("straigthFlight_test basarisiz.")
        if altitude_enable:
            print(f"(Irtifa farki: {altitude_diff:.2f})")
        print(f"(Yon farklari -> yaw: {yaw_diff:.2f} roll: {roll_diff:.2f})\n")

    print(f"STRAIGHT FLIGHT TEST SONLANDI. {success}/{test_sayisi}\n")
