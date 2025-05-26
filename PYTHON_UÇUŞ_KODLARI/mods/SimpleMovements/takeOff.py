from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio

async def takeoff(drone, 
                  target_altitude: int = 20,
                  delta: int = 5):
    try:
        # Anlık irtifa bilgisini al (Z ekseni - Dünya çerçevesi)
        async for position in drone.telemetry.position():
            altitude = abs(position.relative_altitude_m)  # Mutlak değer
            break  # Async generator'dan tek ölçüm al
        if target_altitude < altitude:
            print(f"Anlik irtifa({altitude}), hedef irtifadan({target_altitude}) buyuk!")
            exit()
            
        while True:
            async for att in drone.telemetry.attitude_euler():
                pitch = att.pitch_deg
                yaw = att.yaw_deg
                roll = att.roll_deg
                break
            
            async for position in drone.telemetry.position():
                altitude = abs(position.relative_altitude_m)
                break

            print(f"Anlık İrtifa: {altitude:.1f}m  Anlık pitch: {pitch:.1f}  Anlık yaw: {yaw:.1f}  Anlık roll: {roll:.1f}")

            thrust = 1.0

            if altitude <= target_altitude - delta:
                target_pitch = 15.0
            elif altitude <= target_altitude:
                target_pitch = 1.0
            else:
                print(f"Hedef irtifaya({target_altitude}) ulasildi.")
                target_pitch = 0
                thrust = 0.5
                break

            await drone.offboard.set_attitude(
                Attitude(0, target_pitch, 0.0, thrust)  # Roll, Pitch, Yaw, Throttle
            )
            await asyncio.sleep(0.1)  # 10 Hz (PX4 en az 2 Hz istiyor)
    except KeyboardInterrupt:
        print("Kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Takeoff Hatasi: {e}")
