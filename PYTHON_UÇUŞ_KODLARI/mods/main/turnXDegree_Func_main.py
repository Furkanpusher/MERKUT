from mavsdk import System
from mavsdk.offboard import Attitude
import threading

import threading
import time

class ModeTurnXDegree(threading.Thread):
    """
    ModeC: Gelen telemetry verisini alır, process_data() ile işler,
    ortaya çıkan `result` değerini dışarıya sunar.
    """

    def __init__(self, 
                 angle = 90, 
                 bank_angle_deg = 30.0,
                 high_pitch: float = 0.2,
                 default_pitch: float = 0.0,
                 low_pitch: float = -1.5,
                 normal_throttle: float = 0.7,
                 drop_throttle: float = 0.2,
                 heading_tolerance: float = 3.0,
                 altitude_tolerance: float = 1.0):
        super().__init__(daemon=True)
        self.running = threading.Event()
        self.running.clear()

        # Gelen veri buraya konacak
        self._data = None
        self._data_lock = threading.Lock()

        # İşlendikten sonra bu alana yazılacak
        self._result = None
        self._result_lock = threading.Lock()

        self.angle = angle
        self.bank_angle_deg = bank_angle_deg
        self.high_pitch = high_pitch
        self.default_pitch = default_pitch
        self.low_pitch = low_pitch
        self.normal_throttle = normal_throttle
        self.drop_throttle = drop_throttle
        self.heading_tolerance = heading_tolerance
        self.altitude_tolerance = altitude_tolerance

    def run(self):
        self.running.set()
        print("[C Modu] Başladı.")

        # İlk veri gelene kadar bekle
        while self.running.is_set() and self._data is None:
            time.sleep(0.05)

        with self._data_lock:
            initial_data = self._data.copy() if self._data else {}
        
        orig_yaw, orig_pitch, orig_altitude = initial_data.get('yaw'), initial_data.get('pitch'), initial_data.get('altitude')

        # Hedef heading’i (yaw) hesapla ve normalize et
        self.angle %= 360.0
        if self.angle > 180.0:
            self.angle -= 360
        target_yaw = orig_yaw + self.angle
        self.bank_angle_deg = self.bank_angle_deg if self.angle >= 0 else -self.bank_angle_deg     # Sagdan ya da soldan donus yapacagini belirler

        print(f"[Manevra] Başlangıç Heading: {orig_yaw:.1f}°, Hedef: {target_yaw:.1f}, Test-Angle: {self.angle}°")
        print(f"Orijinal Altitude: {orig_altitude:.1f}")
        while self.running.is_set():
            # Veri varsa al
            with self._data_lock:
                data = self._data

            if data is not None:
                altitude = data.get('altitude')
                    
                alt_diff = abs(orig_altitude - altitude)
                if orig_altitude < altitude - self.altitude_tolerance:
                    processed = {'roll': self.bank_angle_deg, 'pitch': self.low_pitch*(alt_diff%2), 'yaw': 0.0, 'thrust': self.drop_throttle}
                elif orig_altitude > altitude + self.altitude_tolerance:
                    processed = {'roll': self.bank_angle_deg, 'pitch': self.high_pitch*(alt_diff%2), 'yaw': 0.0, 'thrust': self.normal_throttle}
                else:
                    processed = {'roll': self.bank_angle_deg, 'pitch': self.default_pitch, 'yaw': 0.0, 'thrust': self.normal_throttle}

                current_yaw = data.get('yaw')

                # Hesapla aradaki farkı en küçük açı olarak
                diff = (target_yaw - current_yaw + 540) % 360 - 180
                print(f"[Manevra] Mevcut Heading: {current_yaw:.1f}°, Fark: {diff:.1f}°")
                print(f"Altitude: {altitude:.1f}, Orijinal Altitude: {orig_altitude:.1f}")

                if abs(diff) <= self.heading_tolerance:
                    print("[Manevra] Hedef heading’e ulaşıldı.")
                    break

                # Sonucu kaydet
                with self._result_lock:
                    self._result = processed

            # CPU yükünü azaltmak için kısa uyku
            time.sleep(0.05)

        start_time = time.time()

        while self.running.is_set():
            
            if start_time + 2 <= time.time():
                break

            # Orijinal pitch ve throttle ile uçuşa devam
            print("[Manevra] Orijinal pitch ve throttle değerleri korunarak harekete devam ediliyor.")
            processed = {'roll': 0.0, 'pitch': orig_pitch, 'yaw': 0.0, 'thrust': self.normal_throttle}

            # Sonucu kaydet
            with self._result_lock:
                self._result = processed

        print("[C Modu] Durduruldu.")

    def update_data(self, data: dict):
        """Dışarıdan thread'e veri beslemek için çağrılır."""
        with self._data_lock:
            self._data = data

    def get_result(self):
        """Dışarıdan en son işlenmiş sonucu al."""
        with self._result_lock:
            return self._result

    def stop(self):
        """Thread'i güvenli şekilde sonlandır."""
        self.running.clear()
