Kalkışta z ekseninden sapmalar önlenecek baştaki z ekseni açısı ile devam etmesi gerekiyor. Sapma olursa açıyı pid ile düzeltecek
Tekerler yerden kesildikten sonra belli bir açı ile yukarı doğru tırmanacak ( açı bilgisi mekanik ekibinden istenecek)
Modlara göre bu işlemler gerçekleştirilecektir.
mod 1: havada düz uçuş (sürekli kumanda thortle verisi veya kumandadan en son alınan thortle verisi ile)
mod 2: 45 derece dönüş yap sonra düz uç
mod 3: 90 derece dönüş yap sonra düz uç
mod 4: 180 derece dönüş yap sonra düz uç
mod 5: havada yuvarlak çizerek uçuş
mod 6: belirli saniye yükseliş sonra yuvarlak çizme
mod 7: uçağın kalkışı belirli bir süre yukarı tırmanma sonra yuvarlak çizme
bu modlar kumandadan rasberry pi ye verilecektir. rasberry pi ile de pixhawka komut verilecektir.


Not: Bu bir taslak, değişiklikler yapılacak.


Çalıştırma Talimatları:

Çalıştırmak için PYTHON_UCUS_KODLARI klasörünün içindeyken,

1- Run

python3 (veya python) -m mods.run.run

Not: İçi istenildiği gibi düzenlenebilir, herhangi bir uçuş programı oluşturulabilir.

2- Test

python3 (veya python) -m mods.Tests.main_test

Not: Bütün testleri çalıştırır (Build, takeoff, straightFlight, turnXDegree) Uçak yerdeyken çalıştırılmalı
ve testlerin sırası değiştirilmemeli. Testlerin argümanları değiştirilebilir.


ÖNEMLİ NOT: Build/build.py içerisindeki connect fonksiyonunda,

await drone.connect(system_address="serial:///dev/ttyACM2:57600")       # Raspberry
await drone.connect(system_address="udp://:14540")                     # Gazebo

bu iki satırdan biri seçilmeli ve diğeri yorum satırı içine alınmalıdır.