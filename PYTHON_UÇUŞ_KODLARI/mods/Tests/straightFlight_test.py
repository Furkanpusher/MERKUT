import sys
from mods.SimpleMovements import straightFlight

test_sayisi = 1
success = 0
failure = False

async def straightFlight_test(drone,
                              enable_altitude: bool = False,
                              altitude_delta: int = 5,
                              other_delta: int = 1):

    global success, test_sayisi, failure

    print("STRAIGHT FLIGHT TEST BASLADI\n")

    if enable_altitude:
        async for position in drone.telemetry.position():
            altitude = abs(position.relative_altitude_m)
            break
    async for att in drone.telemetry.attitude_euler():
        yaw = att.yaw_deg
        roll = att.roll_deg
        break

    await straightFlight(drone, 5, enable_altitude)

    if enable_altitude:
        async for position in drone.telemetry.position():
            new_altitude = abs(position.relative_altitude_m)
            break
    async for att in drone.telemetry.attitude_euler():
        new_yaw = att.yaw_deg
        new_roll = att.roll_deg
        break

    if enable_altitude:
        altitude_diff = abs(new_altitude - altitude)
    yaw_diff = abs(new_yaw - yaw)
    roll_diff = abs(new_roll - roll)

    if enable_altitude and altitude_diff > altitude_delta:
        failure = True
    elif yaw_diff > other_delta or roll_diff > other_delta:
        failure = True
    else:
        print("straigthFlight_test basarili.\n")
        success += 1

    if failure:
        print(f"straigthFlight_test basarisiz.")
        if enable_altitude:
            print(f"Irtifa farki: {altitude_diff:.2f})")
        print(f"Yon farklari -> yaw: {yaw_diff:.2f} roll: {roll_diff:.2f})\n")
        sys.exit()

    print(f"STRAIGHT FLIGHT TEST SONLANDI. {success}/{test_sayisi}\n")
