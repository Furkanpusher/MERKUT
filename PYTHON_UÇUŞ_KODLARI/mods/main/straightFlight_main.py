import time
import threading

class ModeStraightFlight(threading.Thread):
    def __init__(self, duration=5.0, enable_altitude=True, thrust=0.6, delta=5):
        super().__init__()
        self.daemon = True
        self.running = threading.Event()
        self.data = None
        self.data_lock = threading.Lock()
        self.result_lock = threading.Lock()  # Eksik olan lock
        
        # Parametreler
        self.duration = duration
        self.enable_altitude = enable_altitude
        self.thrust = thrust
        self.delta = delta
        
        # Sonuçlar
        self.result = {'yaw': 0, 'pitch': 0, 'roll': 0, 'thrust': 0.5}
        self.control_result = None
        
        # Süre kontrolü
        self.start_time = None

    def run(self):
        self.running.set()
        print("[B Modu] Başladı")
        
        # İlk veri gelene kadar bekle
        while self.running.is_set() and self.data is None:
            time.sleep(0.05)
        
        if not self.running.is_set():
            return
            
        # Başlangıç zamanı ve yükseklik kaydet
        self.start_time = time.time()
        with self.data_lock:
            initial_data = self.data.copy() if self.data else {}
            
        orig_altitude = initial_data.get('altitude', 0)
        
        print(f"[B Modu] Düz uçuş başladı - Başlangıç yükseklik: {orig_altitude}")
        
        try:
            # Ana uçuş döngüsü
            while self.running.is_set():
                current_time = time.time()
                
                # Süre kontrolü
                if current_time - self.start_time >= self.duration:
                    print(f"[B Modu] {self.duration} saniye tamamlandı")
                    break
                
                # Güncel veri al
                with self.data_lock:
                    current_data = self.data.copy() if self.data else {}
                
                # Kontrol hesapla
                controls = self.calculate_controls(current_data, orig_altitude)
                
                # Sonuç güncelle
                with self.result_lock:
                    self.result = controls
                    
                time.sleep(0.05)  # 20Hz
                
            self.control_result = "completed"
            print("[B Modu] Düz uçuş tamamlandı")
            
        except Exception as e:
            print(f"[B Modu] Hata: {e}")
            self.control_result = "error"
        finally:
            self.running.clear()

    def calculate_controls(self, data, orig_altitude):
        """Kontrol değerlerini hesapla"""
        pitch = 0
        thrust = self.thrust
        
        if self.enable_altitude and data:
            current_altitude = data.get('altitude', orig_altitude)
            altitude_diff = current_altitude - orig_altitude
            
            if altitude_diff > self.delta:
                pitch = -3  # Aşağı
            elif altitude_diff < -self.delta:
                pitch = 3   # Yukarı
            else:
                pitch = 0   # Dengede
                
        return {
            'yaw': 0, 
            'pitch': pitch, 
            'roll': 0, 
            'thrust': thrust
        }

    def update_data(self, data):
        """Dış thread'den veri güncelle"""
        with self.data_lock:
            self.data = data

    def get_result(self):
        """Güncel kontrol sonucunu döndür"""
        with self.result_lock:
            return self.result.copy()
    
    def is_completed(self):
        """Mod tamamlandı mı?"""
        return self.control_result is not None
    
    def stop(self):
        """Thread'i durdur"""
        print("[B Modu] Durdurma komutu alındı")
        self.running.clear()