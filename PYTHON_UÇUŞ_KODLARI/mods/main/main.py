import asyncio
import threading
import queue
import time
from mavsdk import System
from mavsdk.offboard import Attitude
from mods.main import takeoff
from mods.main.straightFlight_main import ModeStraightFlight
from mods.main.turnXDegree_Func_main import ModeTurnXDegree

offboard_started = False

# ----------------------------------------
# Thread definitions
# ----------------------------------------
class SecurityThread(threading.Thread):
    def __init__(self, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self._stop_event = stop_event
        self._active = False

    def run(self):
        self._active = True
        while not self._stop_event.is_set():
            try:
                data = self.input_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            safe = True
            yaw, pitch, roll, thrust, altitude = data.get('yaw'), data.get('pitch'), data.get('roll'), data.get('thrust'), data.get('altitude')
            
            self.output_queue.put({'safe': safe})

    def is_active(self):
        return self._active


class ModeThread(threading.Thread):
    def __init__(self, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.input_queue = queue.Queue()  # Queue kullan
        self.output_queue = queue.Queue()  # Çıkış için queue ekle
        self._stop_event = stop_event
        self.current_mode = "A"
        self._active = False
        self.lock = threading.Lock()
        self.controls = None
        
        # Mode-specific threads
        self.mode_b_thread = None
        self.mode_c_thread = None

    def run(self):
        self._active = True
        while not self._stop_event.is_set():
            try:
                data = self.input_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            controls = None
            
            if self.current_mode == "A":
                controls = takeoff(data)
                if controls and controls.get('control_result'):
                    print("YENI MODA GECILIYOR")
                    self.start_mode_straight_flight()
            elif self.current_mode == "B":
                if self.mode_b_thread and self.mode_b_thread.is_alive():
                    # Thread'e güncel veri gönder
                    self.mode_b_thread.update_data(data)
                    # Sonuç al
                    controls = self.mode_b_thread.get_result()
                else:
                    print("[B Modu] Bitti.")
                    self.start_mode_turn_x_degree()
            elif self.current_mode == "C":
                if self.mode_c_thread and self.mode_c_thread.is_alive():
                    self.mode_c_thread.update_data(data)
                    controls = self.mode_c_thread.get_result()
                else:
                    print("[C Modu] Bitti.")
                    # Başka mod başlat veya döngüyü kır

            if controls:
                print(f"\n{self.current_mode} Result Data: {controls}\n")
                self.output_queue.put(controls)

    def update_input(self, data):
        """Ana döngüden veri al"""
        self.input_queue.put(data)

    def is_active(self):
        return self._active
    
    def start_mode_straight_flight(self):
        print(">> B Modu Başlatılıyor")
        self.current_mode = "B"
        self.mode_b_thread = ModeStraightFlight()
        self.mode_b_thread.start()

    def start_mode_turn_x_degree(self):
        print(">> C Modu Başlatılıyor")
        self.current_mode = "C"
        self.mode_c_thread = ModeTurnXDegree()
        self.mode_c_thread.start()

    def stop(self):
        self._stop_event.set()
        if self.mode_b_thread and self.mode_b_thread.is_alive():
            self.mode_b_thread.stop()
        if self.mode_c_thread and self.mode_c_thread.is_alive():
            self.mode_c_thread.stop()


# ----------------------------------------
# Async helper functions
# ----------------------------------------
async def connect_drone(drone, stop_event: threading.Event, address: str = "udp://:14540"):
    while not stop_event.is_set():
        try:
            await drone.connect(system_address=address)
            async for health in drone.telemetry.health():
                if stop_event.is_set():
                    return False
                if health.is_global_position_ok:
                    print("Bağlantı ve GPS OK.")
                    return True
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Bağlantı hatası: {e}, yeniden deneniyor...")
            await asyncio.sleep(2)
    return False

async def get_telemetry(drone: System, stop_event: threading.Event) -> dict:
    if stop_event.is_set():
        return {}
    
    try:
        async for att in drone.telemetry.attitude_euler():
            yaw, pitch, roll = att.yaw_deg, att.pitch_deg, att.roll_deg
            break
        
        if stop_event.is_set():
            return {}
            
        async for vel in drone.telemetry.position_velocity_ned():
            thrust = vel.velocity.down_m_s
            break
            
        if stop_event.is_set():
            return {}
            
        async for pos in drone.telemetry.position():
            altitude = pos.absolute_altitude_m
            break
            
        return {'yaw': yaw, 'pitch': pitch, 'roll': roll, 'thrust': thrust, 'altitude': altitude}
    except Exception as e:
        print(f"Telemetry okuma hatası: {e}")
        return {}

async def apply_controls(drone, controls: dict, stop_event: threading.Event):
    global offboard_started
    if stop_event.is_set():
        return
        
    print("------------------------------------------------------")
    print("ATTITUDE DEGISTIRILIYOR SUANDA")
    print(f"Thrust: {controls.get('thrust', 0)}")
    print("------------------------------------------------------")

    try:
        # Kontrolleri uygula
        attitude = Attitude(
            controls.get('roll', 0), 
            controls.get('pitch', 0), 
            controls.get('yaw', 0), 
            controls.get('thrust', 0.5)
        )
        
        await drone.offboard.set_attitude(attitude)

        if not offboard_started:
            await drone.action.arm()
            await drone.offboard.start()
            offboard_started = True
            print("Offboard modu başlatıldı.")
            
    except Exception as e:
        print(f"Kontrol uygulama hatası: {e}")

    await asyncio.sleep(0.05)  # 20Hz

# ----------------------------------------
# Main drone loop (runs in separate thread)
# ----------------------------------------
def drone_loop(stop_event: threading.Event):
    """Programın esas drone kontrol döngüsü"""
    sec_thread = SecurityThread(stop_event)
    mode_thread = ModeThread(stop_event)

    drone = System()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Bağlan
    connected = loop.run_until_complete(connect_drone(drone, stop_event))
    if not connected:
        print("Bağlantı başarısız!")
        return

    # Thread'leri başlat
    sec_thread.start()
    mode_thread.start()

    while not stop_event.is_set():
        try:
            # Telemetry al
            data = loop.run_until_complete(get_telemetry(drone, stop_event))
            if not data:
                break

            # Güvenlik kontrolü
            sec_thread.input_queue.put(data)
            
            # Mode thread'e veri gönder
            mode_thread.update_input(data)

            # Güvenlik sonucu kontrol et
            try:
                sec_res = sec_thread.output_queue.get(timeout=0.1)
                if not sec_res.get('safe', True):
                    print("Güvenlik ihlali!")
                    stop_event.set()
                    break
            except queue.Empty:
                pass

            # Kontrol komutlarını al ve uygula
            try:
                controls = mode_thread.output_queue.get(timeout=0.1)
                loop.run_until_complete(apply_controls(drone, controls, stop_event))
            except queue.Empty:
                pass

        except Exception as e:
            print(f"Ana döngü hatası: {e}")
            continue

        time.sleep(0.05)  # 20Hz

    # Cleanup
    print("Drone döngüsü duruyor...")
    stop_event.set()
    
    # Offboard'u durdur
    try:
        loop.run_until_complete(drone.offboard.stop())
    except:
        pass
    
    # Thread'leri bekle
    sec_thread.join(timeout=2)
    mode_thread.join(timeout=2)
    
    loop.close()

# ----------------------------------------
# Program kontrol (enter ile başlat/durdur)
# ----------------------------------------
if __name__ == "__main__":
    program_event = threading.Event()
    worker_thread = None

    print("-- Drone kontrol programı --")
    print("Enter tuşuna basarak başlat/durdur")

    try:
        while True:
            input()  # Enter bekle
            if worker_thread and worker_thread.is_alive():
                # Durdur
                print("Program durduruluyor...")
                program_event.set()
                worker_thread.join(timeout=5)
                worker_thread = None
                program_event.clear()
                offboard_started = False
                print("Program durduruldu.")
            else:
                # Başlat
                print("Program başlatılıyor...")
                program_event.clear()
                worker_thread = threading.Thread(target=drone_loop, args=(program_event,), daemon=True)
                worker_thread.start()
                print("Program başlatıldı.")
    except KeyboardInterrupt:
        print("Çıkış yapılıyor...")
        if worker_thread and worker_thread.is_alive():
            program_event.set()
            worker_thread.join(timeout=5)