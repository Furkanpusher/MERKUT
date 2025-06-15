from kamera_kaydedici import KameraKaydedici
import time

# Start the recording thread immediately
kamera_thread = KameraKaydedici()
print("Kayit baslatiliyor...")
kamera_thread.start()

try:
    # Keep the application running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Cikiliyor...")
    # Stop the recording thread gracefully
    kamera_thread.durdur_kayit()
    kamera_thread.join()
    print("Kayit durduruldu ve program sonlandi.")