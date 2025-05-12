from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio

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
                await test_turns(drone)
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



async def turn_right_90_fixed_wing(drone,
                                   angle: int = 90,
                                   bank_angle_deg: float = 30.0,
                                   high_pitch: float = 0.2,
                                   default_pitch: float = 0.0,
                                   low_pitch: float = -1.5,
                                   normal_throttle: float = 0.7,
                                   drop_throttle: float = 0.2,
                                   heading_tolerance: float = 2.0,
                                   altitude_tolerance: float = 1.0):
    """
    Fixed-wing 90° sağa dönüş manevrası:
      1) Mevcut pitch ve yaw (heading) açılarını al.
      2) Uçağı bank_angle_deg ile sağa yatır (roll = +bank_angle_deg).
      3) Yaw açısı 90° kayana dek (±tolerance) bekle.
      4) Kanatları yataya indir (roll = 0).
      5) Orijinal pitch ve throttle ile uçuşa devam et.

    drone: mavsdk.System instance
    bank_angle_deg: dönüş için kullanılacak bank açısı (°)
    throttle: sabit tutulacak throttle değeri (0.0–1.0)
    heading_tolerance: dönüşü bitirme toleransı (°)
    """

    # 1) Mevcut pitch ve yaw açılarını yakala
    async for att in drone.telemetry.attitude_euler():
        orig_pitch = att.pitch_deg
        orig_yaw   = att.yaw_deg
        break

    # Anlık irtifa bilgisini al (Z ekseni - Dünya çerçevesi)
    async for position in drone.telemetry.position():
        orig_altitude = abs(position.relative_altitude_m)  # Mutlak değer
        break  # Async generator'dan tek ölçüm al

    # 2) Hedef heading’i (yaw) hesapla ve normalize et
    angle %= 360.0
    if angle > 180.0:
        angle -= 360
    target_yaw = orig_yaw + angle

    print(f"[Manevra] Başlangıç Heading: {orig_yaw:.1f}°, Hedef: {target_yaw:.1f}°, Orijinal Altitude: {orig_altitude}")

    # 3) Bank açısını uygula (sağa yat = pozitif roll)
    bank_angle_deg = bank_angle_deg if angle >= 0 else -bank_angle_deg     # Sagdan ya da soldan donus yapacagini belirler
    await drone.offboard.set_attitude(Attitude(bank_angle_deg, default_pitch, 0.0, normal_throttle))

    # 4) Heading değişimini izle
    while True:
        # Anlık irtifa bilgisini al (Z ekseni - Dünya çerçevesi)
        async for position in drone.telemetry.position():
            altitude = abs(position.relative_altitude_m)  # Mutlak değer
            break  # Async generator'dan tek ölçüm al
        
        diff = abs(orig_altitude - altitude)

        if orig_altitude < altitude - altitude_tolerance:
            await drone.offboard.set_attitude(Attitude(bank_angle_deg, low_pitch*(diff%2), 0.0, drop_throttle))
            print("LOW")
        elif orig_altitude > altitude + altitude_tolerance:
            await drone.offboard.set_attitude(Attitude(bank_angle_deg, high_pitch*(diff%2), 0.0, normal_throttle))
            print("HIGH")

        async for att in drone.telemetry.attitude_euler():
            current_yaw = att.yaw_deg
            current_pitch = att.pitch_deg
            break

        # Hesapla aradaki farkı en küçük açı olarak
        diff = (target_yaw - current_yaw + 540) % 360 - 180
        print(f"[Manevra] Mevcut Heading: {current_yaw:.1f}°, Fark: {diff:.1f}°, Altitude: {altitude}, Orijinal Altitude: {orig_altitude}")
        print(f"Orig_Pitch: {orig_pitch}, Pitch: {current_pitch}")

        if abs(diff) <= heading_tolerance:
            print("[Manevra] Hedef heading’e ulaşıldı.")
            break

        # 10 Hz güncelleme
        await asyncio.sleep(0.1)

    # 5) Kanatları tekrar yataya indir (roll = 0)
    print("[Manevra] Roll sıfırlanıyor — kanatlar yataya indiriliyor.")
    await drone.offboard.set_attitude(Attitude(0.0, orig_pitch, 0.0, normal_throttle))

    # 6) Orijinal pitch ve throttle ile uçuşa devam
    print("[Manevra] Orijinal pitch ve throttle değerleri korunarak harekete devam ediliyor.")
    await drone.offboard.set_attitude(Attitude(0.0, orig_pitch, 0.0, normal_throttle))


async def test_turns(drone):
    turns = [90, 90, 180, 180, 325, 35, 772, -52, 0, 1, -1]
    differences = []

    for turn in turns:
        async for att in drone.telemetry.attitude_euler():
            orig_pitch = att.pitch_deg
            break
        
        await turn_right_90_fixed_wing(drone, turn)

        async for att in drone.telemetry.attitude_euler():
            new_pitch = att.pitch_deg
            break

        differences.append(orig_pitch-new_pitch)

        await asyncio.sleep(2)

    i = 1
    for diff in differences:
        print(f"Fark {i} ({turns[i]}): {diff}")

asyncio.run(run())
