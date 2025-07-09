import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QProgressDialog
# Otomatik oluşturulan arayüz sınıfını içe aktar
from goruntu import Ui_MainWindow

class YerIstasyonuApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Arayüzü hazırla
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Sabit admin kullanıcı bilgileri
        self.ADMIN_USER = "admin"
        self.ADMIN_PASS = "12345"

        # Buton tıklamalarını (sinyalleri) fonksiyonlara (slot'lara) bağla
        self.connect_signals()

        # Başlangıçta uçuş kontrol butonlarını devre dışı bırak
        self.toggle_flight_controls(False)

        # Telemetri ve durum değişkenleri
        self.irtifa = 0
        self.hiz = 0
        self.batarya = 100
        self.aktif_mod = "beklemede" # Başlangıç modu

        # Telemetri güncelleme zamanlayıcısı
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.telemetry_guncelle)
        self.telemetry_timer.start(1000)  # Her saniyede bir güncelle

    def toggle_flight_controls(self, enabled):
        """Uçuş kontrol butonlarını toplu olarak aktif/pasif yapar."""
        self.ui.safeFlyButton.setEnabled(enabled)
        self.ui.combatButton.setEnabled(enabled)
        self.ui.kamikazeButton.setEnabled(enabled)
        self.ui.escapeButton.setEnabled(enabled)
        self.ui.takeOffButton.setEnabled(enabled)
        self.ui.landButton.setEnabled(enabled)
        self.ui.homePositionButton.setEnabled(enabled)

    def telemetry_guncelle(self):
        # Aktif moda göre telemetri verilerini güncelle
        if self.aktif_mod == "guvenli_ucus":
            self.hiz += 2
            self.irtifa += 5
        
        elif self.aktif_mod == "savas":
            self.hiz += 5
            self.irtifa += 2
        
        elif self.aktif_mod == "kacis":
            self.hiz += 10
            self.irtifa += 10
        
        elif self.aktif_mod == "kalkis": 
            if self.irtifa < 50: # Örnek: 50 metreye kadar yüksel
                self.irtifa += 5  # burda başka bir fonksiyonda çağırabiliriz.
                self.hiz += 1
        
        elif self.aktif_mod == "inis":
            if self.irtifa > 0: self.irtifa -= 5
            
            else: self.irtifa = 0
            
            if self.hiz > 0: self.hiz -= 2
            
            else: self.hiz = 0
        
        # Batarya her zaman azalır (eğer uçuş modundaysa)
        if self.aktif_mod != "beklemede" and self.batarya > 0:
            self.batarya -= 1
        
        # Arayüzdeki etiketleri güncelle
        self.ui.height.setText(f"{self.irtifa} m")
        self.ui.speed.setText(f"{self.hiz} km/s")
        self.ui.battery.setText(f"% {self.batarya}")
        self.ui.roll.setText("1.2°")
        self.ui.pitch.setText("-0.5°")
        self.ui.latitude.setText("41.015137")
        self.ui.longitude.setText("28.979530")

    def connect_signals(self):
        """Tüm sinyal-slot bağlantılarını burada yap."""
        # Giriş butonu
        self.ui.pushButton.clicked.connect(self.login_attempt)
        self.ui.lineEdit.returnPressed.connect(self.login_attempt)
        self.ui.lineEdit_3.returnPressed.connect(self.login_attempt)

        # Uçuş kontrol butonları
        self.ui.safeFlyButton.clicked.connect(self.safe_fly_modunu_baslat)
        self.ui.combatButton.clicked.connect(self.savas_modunu_baslat)
        self.ui.takeOffButton.clicked.connect(self.kalkis_yap)
        self.ui.kamikazeButton.clicked.connect(self.kamikaze_modunu_baslat)
        self.ui.escapeButton.clicked.connect(self.kacis_modunu_baslat)
        self.ui.landButton.clicked.connect(self.inis_yap)
        self.ui.homePositionButton.clicked.connect(self.eve_don)  

    # --- SLOT Fonksiyonları ---
    
    def login_attempt(self):
        """Kullanıcı adı ve şifreyi kontrol eder."""
        username = self.ui.lineEdit_3.text()
        password = self.ui.lineEdit.text()

        if username == self.ADMIN_USER and password == self.ADMIN_PASS:
            # Giriş başarılı, animasyonu başlat
            self.ui.lineEdit.setEnabled(False)
            self.ui.lineEdit_3.setEnabled(False)
            self.ui.pushButton.setEnabled(False)

            self.progress_dialog = QProgressDialog(
                "Sistem hazırlanıyor...", "İptal", 0, 100, self)
            self.progress_dialog.setWindowTitle("Lütfen Bekleyin")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.show()

            self.animation_timer = QTimer(self)
            self.animation_timer.timeout.connect(self.update_login_progress)
            self.animation_timer.start(15) # Her 15ms'de bir güncelle
        else:
            # Hatalı girişte bir uyarı penceresi göster
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Hatalı Kullanıcı Adı veya Şifre!")
            msg.setInformativeText("Lütfen bilgilerinizi kontrol edin. Uçuş kontrollerini kullanmak için giriş yapmalısınız.")
            msg.setWindowTitle("Giriş Hatası")
            msg.exec_()

    def update_login_progress(self):
        """Giriş animasyonunun ilerleme çubuğunu günceller."""
        current_value = self.progress_dialog.value() + 1
        self.progress_dialog.setValue(current_value)

        if current_value >= 100:
            self.animation_timer.stop()
            self.progress_dialog.close()
            self.toggle_flight_controls(True) # Animasyon bitince butonları aktif et
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Sisteme Başarıyla Bağlanıldı!")
            msg.setWindowTitle("Bağlantı Başarılı")
            msg.exec_()


    def safe_fly_modunu_baslat(self):
        print("Güvenli Uçuş Modu Aktif!")
        self.aktif_mod = "guvenli_ucus"

    def savas_modunu_baslat(self):
        print("Savaş Modu Aktif!")
        self.aktif_mod = "savas"

    def kamikaze_modunu_baslat(self):
        print("Kamikaze Modu Aktif!")
        self.aktif_mod = "kamikaze"

    def kacis_modunu_baslat(self):
        print("Kaçış Modu Aktif!")
        self.aktif_mod = "kacis"

    def kalkis_yap(self):
        print("İHA kalkış yapıyor...")
        self.aktif_mod = "kalkis"
    
    def inis_yap(self):
        print("İHA iniş yapıyor...")
        self.aktif_mod = "inis"

    def eve_don(self):
        print("İHA eve dönüyor...")
        self.aktif_mod = "guvenli_ucus"
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = YerIstasyonuApp()
    window.show()
    sys.exit(app.exec_())