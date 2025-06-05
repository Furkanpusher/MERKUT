import time as t
from mavsdk.offboard import Attitude


async def straightFlight(drone,
                         time,
                         enable_altitude: bool = False,
                         thrust: float = 1.0,
                         delta: int = 5):
    try:
        if enable_altitude:
            async for position in drone.telemetry.position():
                orig_altitude = abs(position.relative_altitude_m)
                break
        pitch = -1
        
        current_time = t.time()
        t.sleep(0.1)
        while (t.time() - current_time) < time:  
            if enable_altitude: 
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
    