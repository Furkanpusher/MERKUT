# Raspberry Pi Kamera Kayıt Sistemi

Bu proje, Raspberry Pi üzerinde sistem açılışında otomatik olarak kamera kaydı başlatan bir Python uygulamasını içerir. Kamera, sürekli olarak görüntüleri yakalar ve belirtilen bir klasöre (`kayitlar`) JPEG dosyaları olarak kaydeder. Proje, ekran bağlı olsun veya olmasın çalışacak şekilde tasarlanmıştır ve `/etc/rc.local` kullanılarak otomatik başlatma sağlanır.

## Özellikler
- **Otomatik Başlatma**: Raspberry Pi açıldığında kamera kaydı otomatik olarak başlar.
- **Sürekli Kayıt**: Kamera, `while True` döngüsü ile sürekli görüntü yakalar ve kaydeder.
- **Hata Toleransı**: Kamera bağlantısı kesilirse, yeniden bağlanma denemeleri yapılır.
- **Loglama**: Kayıt işlemleri ve hatalar bir log dosyasına yazılır.
- **Esnek Çalışma**: Ekran bağlı olmadan (headless) veya ekranla çalışır.

## Otomatik Başlatma Ayarı

- **Dosyayı açın**: sudo nano /etc/rc.local
- **Dosyayı ekleyin**:<pre> ```
# Python scriptlerini sistem açılışında çalıştır
cd /home/pi/raspberry-pi-kamera-kayit && /usr/bin/python3 /home/pi/raspberry-pi-kamera-kayit/kamera_kaydedici.py >> /home/pi/logg.txt 2>&1 &
``` </pre>
- **Dosyayı çalıştırır hale getirin**: ``` sudo chmod +x /etc/rc.local ``` 
