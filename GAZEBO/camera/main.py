# main.py

from kamera_kaydedici import KameraKaydedici
import RPi.GPIO as GPIO
import time

# GPIO ayarlari
INPUT_PIN = 17  # BCM numarasi (fiziksel pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_PIN, GPIO.IN)

kamera_thread = None
print("GPIO kontrolu baslatildi. Sinyal geldiginde kayit baslayacak.")

try:
    while True:
        pin_durumu = GPIO.input(INPUT_PIN)

        if pin_durumu == GPIO.LOW:
            if kamera_thread is None or not kamera_thread.is_alive():
                print("Sinyal algilandi: Kayit baslatiliyor.")
                kamera_thread = KameraKaydedici()
                kamera_thread.start()
        else:
            if kamera_thread and kamera_thread.is_alive():
                print("Sinyal kesildi: Kayit durduruluyor.")
                kamera_thread.durdur_kayit()
                kamera_thread.join()
                kamera_thread = None

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Cikiliyor...")
    if kamera_thread and kamera_thread.is_alive():
        kamera_thread.durdur_kayit()
        kamera_thread.join()

finally:
    GPIO.cleanup()
