# İHA Telemetri Analiz ve Görselleştirme Uygulaması

Python kullanılarak geliştirilmiş, CSV formatındaki İHA telemetri verilerini doğrulayan, kısmi veri kurtarma (partial recovery) yapan, istatistiksel analizler üreten ve zaman serisi grafikleriyle görselleştiren modern masaüstü uygulaması.

---

## 🚀 Özellikler

- **Modern Grafik Arayüz:** CustomTkinter tabanlı şık koyu tema ve Matplotlib destekli gömülü grafikler.
- **Kapsamlı Veri Doğrulama:**
  - Zorunlu sütunların ve boş alanların denetimi
  - Sayısal tip ve sınır kontrolleri (Negatif hız tespiti, %0-100 batarya aralığı, enlem/boylam ve açı kontrolleri)
  - Bozuk tarih damgalarının tespiti
  - **Kısmi Veri Kurtarma:** Hatalı satırlar listelenip raporlanırken, geçerli kayıtlar işlenmeye devam eder.
- **Telemetri Analiz Motoru:**
  - Ortalama, minimum ve maksimum irtifa
  - Ortalama hız ve minimum batarya seviyesi
  - **Zaman Boşluğu Tespiti (Anomali Analizi):** Eşik süresini aşan veri kesintilerinin tespiti ve grafik üzerinde kırmızı uyarı şeritleriyle vurgulanması.
- **Test ve Örnek Veri Üreteci:** Tek tıkla geçerli, hatalı, karışık, bozuk ve eksik sütunlu 5 farklı senaryo dosyasının üretimi.
- **Yüksek Test Kapsamı:** PDF'teki 10 zorunlu senaryo ve 5 ek senaryoyu kapsayan 24 adet otomatik birim/entegrasyon testi.

---

## 📥 Doğrudan İndir ve Çalıştır (Python GEREKTİRMEZ!)

Uygulamanın çalışması için bilgisayarınızda Python yüklü olmasına veya terminal komutları yazmanıza gerek yoktur:

1. **[GitHub Releases Sayfasından İndirin (v1.0.0)](https://github.com/Mehmet-Akiff/iha-telemetri-analiz/releases/tag/v1.0.0)**
   - `IHA_Telemetri_Istasyonu_v1.0.0_Windows.zip` dosyasını indirin ve bir klasöre çıkartın.
   - Klasör içerisindeki **`IHA_Telemetri_Istasyonu.exe`** dosyasına çift tıklayarak uygulamayı anında başlatabilirsiniz!

---

## 💻 Geliştirici Modunda Çalıştırma (Python ile)

Eğer kaynak kodlar üzerinden çalıştırmak isterseniz:

1. Proje ana dizinindeki **`Baslat.bat`** dosyasına çift tıklayarak terminal ekranı görmeden uygulamayı açabilirsiniz.
2. Veya terminal üzerinden:
   ```bash
   pip install -r requirements.txt  # veya: pip install customtkinter matplotlib pandas numpy pytest
   python gui_app.py
   ```

### 🛸 Uygulama 1: İHA Telemetri Analiz İstasyonu
- **Tek Tık Başlatıcı:** Proje dizinindeki **`Baslat.bat`** dosyasına çift tıklayın.
- **Kaynak Koddan:** `python gui_app.py`
- **Kullanım:**
  1. "CSV Dosyası Seç" butonuyla analiz etmek istediğiniz telemetri dosyasını yükleyin.
  2. "Analiz Et" butonuna tıklayarak metrikleri, grafikleri ve hata raporunu inceleyin.

---

### 🧪 Uygulama 2: İHA Telemetri CSV Senaryo Üretici
Test ve doğrulama süreçleri için özel olarak geliştirilmiş ikinci masaüstü uygulamasıdır.
- **Tek Tık Başlatıcı:** Proje dizinindeki **`Uretici_Baslat.bat`** dosyasına çift tıklayın.
- **Kaynak Koddan:** `python generator_gui.py`
- **Desteklenen 14 Senaryo:**
  1. %100 Geçerli Uçuş (Normal seyir profili)
  2. Zaman Boşluğu / Kesintili Uçuş (Data drop simülasyonu)
  3. Karışık / Kısmi Hatalı Veri (Kısmi kurtarma testi için)
  4. Negatif Hız Değerleri
  5. Batarya Sınır İhlalleri (< %0 ve > %100)
  6. Geçersiz Enlem/Boylam (WGS84 sınır dışı)
  7. Sayısal Alanda Metin İçeren Veri
  8. Zorunlu Alanı Boş Bırakılmış Satırlar
  9. Çözümlenemeyen / Bozuk Zaman Damgaları
  10. Açısal Sınır İhlalleri (Pitch/Roll/Yaw)
  11. Gerekli Sütunları Eksik CSV
  12. Sıfır Geçerli Kayıt (Tüm satırlar hatalı)
  13. Boş Dosya (0 bayt)
  14. Bozuk Biçimli / Geçersiz CSV Sözdizimi
- **Özellikler:** Satır sayısı, kesinti süresi, irtifa, hız ve batarya parametrelerini özelleştirebilme, canlı tablo önizlemesi ve doğrudan istenen konuma CSV kaydetme.

---

## 🧪 Otomatik Testlerin Çalıştırılması

Projede PDF gereksinimlerini ve sınır durumları test eden 24 adet pytest testi bulunmaktadır.

Tüm testleri ayrıntılı olarak çalıştırmak için:

```bash
python -m pytest -v
```

Sadece telemetri senaryo testlerini çalıştırmak için:

```bash
python -m pytest tests/test_telemetry.py -v
```

Sadece doğrulama (validator) testlerini çalıştırmak için:

```bash
python -m pytest tests/test_validator.py -v
```

---

## 📁 Proje Dosya Yapısı

```
İME Proje/
├── gui_app.py                   # CustomTkinter Masaüstü Arayüzü
├── telemetry_validator.py       # Doğrulama ve Kısmi Kurtarma Motoru
├── telemetry_analyzer.py        # İstatistik ve Zaman Boşluğu Analiz Motoru
├── data_generator.py            # Örnek CSV Üretim Scripti
├── TEKNIK_RAPOR.md              # Kapsamlı Teknik Araştırma ve Karar Raporu
├── README.md                    # Kullanım ve Kurulum Kılavuzu
├── samples/                     # Örnek CSV Test Dosyaları
│   ├── telemetry_valid.csv      # %100 geçerli uçuş verisi
│   ├── telemetry_mixed.csv      # Geçerli + kasıtlı hatalı kayıtlar
│   ├── telemetry_corrupted.csv  # Bozuk biçimli CSV
│   ├── telemetry_missing_columns.csv # Eksik başlıklı CSV
│   └── telemetry_empty.csv      # 0 bayt boş dosya
├── tests/                       # Otomatik Testler (pytest)
│   ├── test_telemetry.py        # 10 Zorunlu + 5 Ek Senaryo (15 Test)
│   ├── test_validator.py        # Doğrulayıcı birim testleri (5 Test)
│   ├── test_analyzer.py         # Analiz motoru testleri (3 Test)
│   └── test_data_generator.py   # Veri üreteci testleri (1 Test)
└── docs/                        # Tasarım (Spec) ve Plan Dokümantasyonu
```
