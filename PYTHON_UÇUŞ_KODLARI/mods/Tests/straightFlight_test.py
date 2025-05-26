import sys
from mods.SimpleMovements import straightFlight

test_sayisi = 1
success = 0
failure = False

async def straightFlight_test(drone,
                              altitude_delta: int = 5,
                              other_delta: int = 1):

    global success, test_sayisi, failure

    print("STRAIGHT FLIGHT TEST BASLADI\n")

    async for position in drone.telemetry.position():
        altitude = abs(position.relative_altitude_m)
        break
    async for att in drone.telemetry.attitude_euler():
        pitch = att.pitch_deg
        yaw = att.yaw_deg
        roll = att.roll_deg
        break

    await straightFlight(drone, 5)

    async for position in drone.telemetry.position():
        new_altitude = abs(position.relative_altitude_m)
        break
    async for att in drone.telemetry.attitude_euler():
        new_pitch = att.pitch_deg
        new_yaw = att.yaw_deg
        new_roll = att.roll_deg
        break

    altitude_diff = abs(new_altitude - altitude)
    pitch_diff = abs(new_pitch - pitch)
    yaw_diff = abs(new_yaw - yaw)
    roll_diff = abs(new_roll - roll)

    if altitude_diff > altitude_delta:
        failure = True
    elif pitch_diff > other_delta or yaw_diff > other_delta or roll_diff > other_delta:
        failure = True
    else:
        print("straigthFlight_test basarili.\n")

    if failure:
        print(f"straigthFlight_test basarisiz. (Irtifa farki: {altitude_diff:.2f})\n(Yon farklari -> pitch: {pitch_diff:.2f} yaw: {yaw_diff:.2f} roll: {roll_diff:.2f})\n")
        sys.exit()

    print(f"STRAIGHT FLIGHT TEST SONLANDI. {success}/{test_sayisi}\n")
