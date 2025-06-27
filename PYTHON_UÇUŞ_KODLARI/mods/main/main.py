import asyncio
import threading
import queue
import time
from mavsdk import System
from mavsdk.offboard import Attitude
from mods.main import takeoff

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
            if data.get('thrust', 0) > 0.9:
                safe = False
            self.output_queue.put({'safe': safe})

    def is_active(self):
        return self._active


class ModeThread(threading.Thread):
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

            #controls = {
            #    'yaw': data['yaw'],
            #    'pitch': data['pitch'],
            #    'roll': data['roll'],
            #    'thrust': data['thrust']
            #}
            controls = takeoff(data)
            self.output_queue.put(controls)

    def is_active(self):
        return self._active


# ----------------------------------------
# Async helper functions
# ----------------------------------------
async def connect_drone(drone: System, stop_event: threading.Event, address: str = "udp://:14540"):
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

async def apply_controls(drone: System, controls: dict, stop_event: threading.Event):
    global offboard_started
    if stop_event.is_set():
        return
    await drone.offboard.set_attitude(
        Attitude(controls['roll'], controls['pitch'], controls['yaw'], controls['thrust'])
    )
    if not offboard_started:
        try:
            await drone.offboard.start()
            offboard_started = True
            print("Offboard modu başlatıldı.")
        except Exception as e:
            print(f"Offboard başlatılamadı: {e}")
            return
    await asyncio.sleep(0.1)

# ----------------------------------------
# Main drone loop (runs in separate thread)
# ----------------------------------------
def drone_loop(stop_event: threading.Event):
    """Programın esas drone kontrol döngüsü"""
    # Thread kontrol event
    sec_thread = SecurityThread(stop_event)
    mode_thread = ModeThread(stop_event)

    drone = System()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 1-2: Bağlan
    connected = loop.run_until_complete(connect_drone(drone, stop_event))
    if not connected:
        return  # exit if stopped during connect

    while not stop_event.is_set():
        # 3-4: Telemetry al
        try:
            data = loop.run_until_complete(get_telemetry(drone, stop_event))
            if not data:
                break
        except Exception as e:
            print(f"Telemetry hata: {e}")
            continue

        # 5-6: Güvenlik thread
        if not sec_thread.is_active():
            sec_thread.start()
        sec_thread.input_queue.put(data)

        # 7-8: Mod thread
        if not mode_thread.is_active():
            mode_thread.start()
        mode_thread.input_queue.put(data)

        # 9-10: Güvenlik sonucu
        try:
            sec_res = sec_thread.output_queue.get(timeout=1)
        except queue.Empty:
            continue
        if not sec_res.get('safe', False):
            print("Güvenlik ihlali, mod durduruluyor.")
            stop_event.set()
            break

        # 11-12: Modu uygula
        try:
            controls = mode_thread.output_queue.get(timeout=1)
            loop.run_until_complete(apply_controls(drone, controls, stop_event))
        except queue.Empty:
            continue

        time.sleep(0.1)

    # Cleanup
    print("Drone döngüsü duruyor, threadler sonlanıyor...")
    stop_event.set()
    sec_thread.join(timeout=1)
    mode_thread.join(timeout=1)
    # MAVSDK bağlantısını sonlandırmak için loop kapatılabilir
    loop.stop()
    loop.close()
    drone.offboard.stop()

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
                worker_thread.join()
                worker_thread = None
                # Reset event
                program_event.clear()
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
        if worker_thread:
            program_event.set()
            worker_thread.join()