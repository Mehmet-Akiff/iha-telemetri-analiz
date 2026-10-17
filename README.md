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

## 🛠️ Kurulum

Gereksinimler: Python 3.10 veya üzeri.

Gerekli kütüphaneleri yüklemek için:

```bash
pip install customtkinter matplotlib pandas numpy pytest
```

---

## 💻 Uygulamanın Başlatılması

Masaüstü grafik arayüzünü çalıştırmak için:

```bash
python gui_app.py
```

### Arayüz Kullanımı:
1. **"Örnek CSV Üret"** butonuna basarak `samples/` dizini altına test dosyalarını oluşturabilirsiniz.
2. **"CSV Dosyası Seç"** butonuyla istediğiniz `.csv` dosyasını seçin.
3. İsteğe bağlı olarak **"Zaman Boşluğu Eşiği (sn)"** kutusundan eşiği ayarlayın (varsayılan: 3.0 saniye).
4. **"Analiz Et"** butonuna tıklayın.
5. Sonuçlar;
   - Üst kartlarda (KPI),
   - **📈 Telemetri Grafikleri** sekmesinde (İrtifa, Hız, Batarya ve kesinti aralıkları),
   - **📋 Geçerli Veri Tablosu** sekmesinde,
   - **⚠️ Hatalı Kayıtlar Raporu** sekmesinde (hangi satırın neden reddedildiği) anında görüntülenir.

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
