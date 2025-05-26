import datetime
import time as t
from mavsdk.offboard import Attitude


async def straightFlight(drone,
                         time,
                         thrust: float = 1.0,
                         delta: int = 5):
    try:
        async for att in drone.telemetry.attitude_euler():
            orig_pitch = att.pitch_deg
            orig_yaw = att.yaw_deg
            orig_roll = att.roll_deg
            break
            
        async for position in drone.telemetry.position():
            orig_altitude = abs(position.relative_altitude_m)
            break
        
        current_time = datetime.datetime.now()
        t.sleep(0.1)
        while (datetime.datetime.now() - current_time).total_seconds() < time:   
            async for position in drone.telemetry.position():
                altitude = abs(position.relative_altitude_m)
                break

            if altitude > orig_altitude + delta:
                pitch = -3
            elif altitude < orig_altitude - delta:
                pitch = 3
            else:
                pitch = 0
            
            await drone.offboard.set_attitude(
                Attitude(0, pitch, 0.0, thrust)  # Roll, Pitch, Yaw, Throttle
            )
                
    except Exception as e:
        print(f"Straight Flight Hatasi: {e}")
    