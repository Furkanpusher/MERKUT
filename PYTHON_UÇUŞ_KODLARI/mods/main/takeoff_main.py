
def takeoff(data,
            target_altitude: int = 20,
            delta: int = 5):
    try:
        yaw, pitch, roll, thrust, altitude = data['yaw'], data['pitch'], data['roll'], data['thrust'], data['altitude']
        if target_altitude < altitude:
            print(f"Anlik irtifa({altitude}), hedef irtifadan({target_altitude}) buyuk!")
            exit()

        print(f"Anlık İrtifa: {altitude:.1f}m  Anlık pitch: {pitch:.1f}  Anlık yaw: {yaw:.1f}  Anlık roll: {roll:.1f}")

        if altitude <= target_altitude - delta:
            target_pitch = 4.0
        elif altitude <= target_altitude:
            target_pitch = 1.0
        else:
            print(f"Hedef irtifaya({target_altitude}) ulasildi.")
            target_pitch = 0
            thrust = 0.5

        return {'yaw': yaw, 'pitch': target_pitch, 'roll': roll, 'thrust': thrust, 'altitude': altitude}
    except KeyboardInterrupt:
        print("Kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Takeoff Hatasi: {e}")
