from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio

import turnXDegree_Test

async def run():
    turned = False
    climb = False
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Bağlantı bekleniyor...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Bağlandı!")
            break

    # ARM etme
    try:
        print("ARM ediliyor...")
        await drone.action.arm()
    except Exception as e:
        print(f"ARM başarısız: {e}")
        exit

    # Offboard modu başlat
    print("Offboard moda geçiliyor...")
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.7))
    await drone.offboard.start()

    try:
        # Sonsuz döngüde sürekli setpoint gönder
        while True:
            # Anlık irtifa bilgisini al (Z ekseni - Dünya çerçevesi)
            async for position in drone.telemetry.position():
                altitude = abs(position.relative_altitude_m)  # Mutlak değer
                break  # Async generator'dan tek ölçüm al

            async for att in drone.telemetry.attitude_euler():
                pitch = att.pitch_deg
                yaw = att.yaw_deg
                roll = att.roll_deg
                break


            print(f"Anlık İrtifa: {altitude:.1f}m  Anlık pitch: {pitch:.1f}  Anlık yaw: {yaw:.1f}  Anlık roll: {roll:.1f}")

            # 10 m’de 90° sağa dönüş yap
            if altitude >= 20.0 and not turned:
                await turnXDegree_Test.test_turns(drone)
                turned = True


            # 10m'ye ulaşıldığında pitch'i 1° yap
            if altitude <= 30.0 and not climb:
                target_pitch = 15.0  # Tırmanış için 15° pitch
            elif altitude <= 30.0:
                target_pitch = 1.0
            else:
                target_pitch = 0.0  # Düz uçuş için 1° pitch
                print(f"",drone.telemetry.attitude_euler())
                climb = True

            # Setpoint gönder
            await drone.offboard.set_attitude(
                Attitude(0, target_pitch, 0.0, 1.0)  # Roll, Pitch, Yaw, Throttle
            )
            await asyncio.sleep(0.1)  # 10 Hz (PX4 en az 2 Hz istiyor)
    except KeyboardInterrupt:
        print("Kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        await drone.offboard.stop()
        await drone.action.disarm()

asyncio.run(run())
