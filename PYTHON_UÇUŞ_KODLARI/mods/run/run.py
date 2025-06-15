import asyncio
from mavsdk.offboard import Attitude, OffboardError
from mavsdk.telemetry import FlightMode
from mods.Build import build
from mods.SimpleMovements import straightFlight, takeoff
from mods.TurnXDegreeMod import turn_fixed_wing

# Global değişkenler
should_run = False  # Uygulamayı başlat/durdur bayrağı
run_task = None     # run fonksiyonu için görev

async def run(drone):
    """Drone'un OFFBOARD modunda çalışmasını sağlayan fonksiyon."""
    global should_run
    try:
        print("Kumanda bekleniyor...")
        await drone.action.arm()
        await asyncio.sleep(1)
        await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 1))

        print("STRAIGHT FLIGHT BAŞLADI")
        await straightFlight(drone, 5)
        print("STRAIGHT FLIGHT TAMAMLANDI")

        print("180 DERECE DÖNÜŞ BAŞLADI")
        await turn_fixed_wing(drone, -15)
        await turn_fixed_wing(drone, 15)
        await turn_fixed_wing(drone, -40)
        await turn_fixed_wing(drone, 40)
        print("180 DERECE DÖNÜŞ TAMAMLANDI")
    except asyncio.CancelledError:
        print("Run görevi iptal edildi.")
        # Gerekirse temizlik işlemleri burada yapılabilir

async def check_offboard_mode(drone):
    """Drone'un OFFBOARD modunda olup olmadığını kontrol eder."""
    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode == FlightMode.OFFBOARD:
            print("Drone OFFBOARD modunda!")
            return True
        else:
            print(f"Drone OFFBOARD modunda değil, mevcut mod: {flight_mode}")
            return False

async def input_listener(drone):
    """Drone'un modunu izler ve run fonksiyonunu başlatır/durdurur."""
    global should_run, run_task

    while True:
        is_offboard = await check_offboard_mode(drone)
        if is_offboard and not should_run:
            should_run = True
            print("Uygulama başlatılıyor...")
            run_task = asyncio.create_task(run(drone))
        elif not is_offboard and should_run:
            should_run = False
            print("Uygulama durduruluyor...")
            if run_task:
                run_task.cancel()
                run_task = None
        await asyncio.sleep(0.1)  # Döngünün çok hızlı çalışmasını önler

async def async_main():
    """Asenkron başlatma fonksiyonu."""
    drone = await build()  # Drone nesnesini oluştur
    asyncio.create_task(input_listener(drone))  # input_listener'ı görev olarak başlat

def main():
    """Senkron ana fonksiyon."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_main())  # async_main'i çalıştır
        loop.run_forever()  # Olay döngüsünü sürekli çalışır halde tut
    except KeyboardInterrupt:
        print("Çıkılıyor...")
    finally:
        loop.stop()
        loop.close()

if __name__ == "__main__":
    main()