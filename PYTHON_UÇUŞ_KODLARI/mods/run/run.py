import asyncio
from mavsdk.offboard import Attitude, OffboardError
from mavsdk.telemetry import FlightMode
from mods.Build import build
from mods.SimpleMovements import straightFlight, takeoff
from mods.TurnXDegreeMod import turn_fixed_wing

# Global degiskenler
should_run = False  # Uygulamayi baslat/durdur bayragi
run_task = None     # run fonksiyonu icin gorev

async def run(drone):
    """Drone'un OFFBOARD modunda calismasini saglayan fonksiyon."""
    global should_run
    try:
        print("Kumanda bekleniyor...")
        await drone.action.arm()
        await asyncio.sleep(1)
        await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 1))

        print("STRAIGHT FLIGHT BASLADI")
        await straightFlight(drone, 5)
        print("STRAIGHT FLIGHT TAMAMLANDI")

        print("180 DERECE DONUS BASLADI")
        await turn_fixed_wing(drone, -15)
        await turn_fixed_wing(drone, 15)
        await turn_fixed_wing(drone, -40)
        await turn_fixed_wing(drone, 40)
        print("180 DERECE DONUS TAMAMLANDI")
    except asyncio.CancelledError:
        print("Run gorevi iptal edildi.")
        # Gerekirse temizlik islemleri burada yapilabilir

async def check_offboard_mode(drone):
    """Drone'un OFFBOARD modunda olup olmadigini kontrol eder."""
    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode == FlightMode.OFFBOARD:
            print("Drone OFFBOARD modunda!")
            return True
        else:
            print(f"Drone OFFBOARD modunda degil, mevcut mod: {flight_mode}")
            return False

async def input_listener(drone):
    """Drone'un modunu izler ve run fonksiyonunu baslatir/durdurur."""
    global should_run, run_task

    while True:
        is_offboard = await check_offboard_mode(drone)
        if is_offboard and not should_run:
            should_run = True
            print("Uygulama baslatiliyor...")
            run_task = asyncio.create_task(run(drone))
        elif not is_offboard and should_run:
            should_run = False
            print("Uygulama durduruluyor...")
            if run_task:
                run_task.cancel()
                run_task = None
        await asyncio.sleep(0.1)  # Dongunun cok hizli calismasini onler

async def async_main():
    """Asenkron baslatma fonksiyonu."""
    drone = await build()  # Drone nesnesini olustur
    asyncio.create_task(input_listener(drone))  # input_listener'i gorev olarak baslat

def main():
    """Senkron ana fonksiyon."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_main())  # async_main'i calistir
        loop.run_forever()  # Olay dongusunu surekli calisir halde tut
    except KeyboardInterrupt:
        print("Cikiliyor...")
    finally:
        loop.stop()
        loop.close()

if __name__ == "__main__":
    main()