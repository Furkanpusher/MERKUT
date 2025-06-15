# kamera_kaydedici.py

import cv2
import os
import threading
import time
import re

class KameraRecorder(threading.Thread):
    def __init__(self, klasor="kayitlar"):
        super().__init__()
        self.klasor = klasor
        os.makedirs(self.klasor, exist_ok=True)
        self.cap = None
        self.durdur = False
        self.frame_count = self._bul_son_frame_numarasi()
        self._baglan_kamera()

    def _baglan_kamera(self):
        """Kamerayi bulana kadar tekrar dener."""
        while not self.durdur:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                print("Kamera bulundu ve baglanti kuruldu.")
                break
            print("Kamera acilamadi, tekrar denenecek...")
            self.cap.release()
            time.sleep(1)  # 1 saniye bekleyip tekrar dene

    def _bul_son_frame_numarasi(self):
        """Mevcut klasorde en son frame numarasini bulur."""
        max_num = 0
        pattern = re.compile(r"frame_(\d+)\.jpg")
        for dosya in os.listdir(self.klasor):
            eslesme = pattern.match(dosya)
            if eslesme:
                num = int(eslesme.group(1))
                if num > max_num:
                    max_num = num
        return max_num + 1

    def run(self):
        if not self.cap or not self.cap.isOpened():
            print("Kamera baglantisi basarisiz, kaydedici sonlandiriliyor.")
            return

        while not self.durdur:
            ret, frame = self.cap.read()
            if not ret:
                print("Goruntu alinamadi, tekrar kamera baglantisi deneniyor...")
                self.cap.release()
                self._baglan_kamera()
                if not self.cap.isOpened():
                    continue

            dosya_adi = os.path.join(self.klasor, f"frame_{self.frame_count:05d}.jpg")
            cv2.imwrite(dosya_adi, frame)
            print(f"{dosya_adi} kaydedildi.")
            self.frame_count += 1
            time.sleep(0.05)

        if self.cap:
            self.cap.release()
            print("Kamera kapatildi.")

    def durdur_kayit(self):
        self.durdur = True