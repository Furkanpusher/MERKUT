from mavsdk import System
from mavsdk.offboard import Attitude
import asyncio

# 45 derece donme modu
async def turn_fixed_wing_45(drone):
    await turn_fixed_wing(drone, 45)

# -45 derece donme modu
async def turn_fixed_wing_neg_45(drone):
    await turn_fixed_wing(drone, -45)

# 90 derece donme modu
async def turn_fixed_wing_90(drone):
    await turn_fixed_wing(drone, 90)

# -90 derece donme modu
async def turn_fixed_wing_neg_90(drone):
    await turn_fixed_wing(drone, -90)

async def turn_fixed_wing(drone,
                                angle: int = 90,
                                enable_altitude: bool = False,
                                bank_angle_deg: float = 30.0,
                                high_pitch: float = 0.2,
                                default_pitch: float = 0.0,
                                low_pitch: float = -1.5,
                                normal_throttle: float = 0.7,
                                drop_throttle: float = 0.2,
                                heading_tolerance: float = 3.0,
                                altitude_tolerance: float = 1.0):
    """
    Fixed-wing 90° saga donus manevrasi:
      1) Mevcut pitch ve yaw (heading) acilarini al.
      2) Ucagi bank_angle_deg ile saga yatir (roll = +bank_angle_deg).
      3) Yaw acisi 90° kayana dek (±tolerance) bekle.
      4) Kanatlari yataya indir (roll = 0).
      5) Orijinal pitch ve throttle ile ucusa devam et.

    drone: mavsdk.System instance
    bank_angle_deg: donus icin kullanilacak bank acisi (°)
    throttle: sabit tutulacak throttle degeri (0.0–1.0)
    heading_tolerance: donusu bitirme toleransi (°)
    """

    # 1) Mevcut pitch ve yaw acilarini yakala
    async for att in drone.telemetry.attitude_euler():
        orig_pitch = att.pitch_deg
        orig_yaw   = att.yaw_deg
        break

    if enable_altitude:
        # Anlik irtifa bilgisini al (Z ekseni - Dunya cercevesi)
        async for position in drone.telemetry.position():
            orig_altitude = abs(position.relative_altitude_m)  # Mutlak deger
            break  # Async generator'dan tek olcum al

    # 2) Hedef heading’i (yaw) hesapla ve normalize et
    angle %= 360.0
    if angle > 180.0:
        angle -= 360
    target_yaw = orig_yaw + angle

    print(f"[Manevra] Baslangic Heading: {orig_yaw:.1f}°, Hedef: {target_yaw:.1f}, Test-Angle: {angle}°")
    if enable_altitude:
        print(f"Orijinal Altitude: {orig_altitude:.1f}")

    # 3) Bank acisini uygula (saga yat = pozitif roll)
    bank_angle_deg = bank_angle_deg if angle >= 0 else -bank_angle_deg     # Sagdan ya da soldan donus yapacagini belirler
    await drone.offboard.set_attitude(Attitude(bank_angle_deg, default_pitch, 0.0, normal_throttle))

    # 4) Heading degisimini izle
    while True:
        if enable_altitude:
            # Anlik irtifa bilgisini al (Z ekseni - Dunya cercevesi)
            async for position in drone.telemetry.position():
                altitude = abs(position.relative_altitude_m)  # Mutlak deger
                break  # Async generator'dan tek olcum al
        
            diff = abs(orig_altitude - altitude)
            if orig_altitude < altitude - altitude_tolerance:
                await drone.offboard.set_attitude(Attitude(bank_angle_deg, low_pitch*(diff%2), 0.0, drop_throttle))
            elif orig_altitude > altitude + altitude_tolerance:
                await drone.offboard.set_attitude(Attitude(bank_angle_deg, high_pitch*(diff%2), 0.0, normal_throttle))
            else:
                await drone.offboard.set_attitude(Attitude(bank_angle_deg, default_pitch, 0.0, normal_throttle))

        async for att in drone.telemetry.attitude_euler():
            current_yaw = att.yaw_deg
            break

        # Hesapla aradaki farki en kucuk aci olarak
        diff = (target_yaw - current_yaw + 540) % 360 - 180
        print(f"[Manevra] Mevcut Heading: {current_yaw:.1f}°, Fark: {diff:.1f}°")
        if enable_altitude:
            print(f"Altitude: {altitude:.1f}, Orijinal Altitude: {orig_altitude:.1f}")

        if abs(diff) <= heading_tolerance:
            print("[Manevra] Hedef heading’e ulasildi.")
            break

        # 10 Hz guncelleme
        await asyncio.sleep(0.001)

    # 5) Kanatlari tekrar yataya indir (roll = 0)
    print("[Manevra] Roll sifirlaniyor — kanatlar yataya indiriliyor.")
    await drone.offboard.set_attitude(Attitude(0.0, orig_pitch, 0.0, normal_throttle))

    # 6) Orijinal pitch ve throttle ile ucusa devam
    print("[Manevra] Orijinal pitch ve throttle degerleri korunarak harekete devam ediliyor.")
    await drone.offboard.set_attitude(Attitude(0.0, orig_pitch, 0.0, normal_throttle))