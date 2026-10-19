# 🛸 İHA Telemetri Analiz ve Görselleştirme İstasyonu (v1.6.0)

[![Version](https://img.shields.io/badge/Sürüm-v1.6.0-00d2ff?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-telemetri-analiz)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-telemetri-analiz)
[![Security](https://img.shields.io/badge/Güvenlik-DigiCert%20İmzalı%20Motor-2b8a3e?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-telemetri-analiz)
[![Tests](https://img.shields.io/badge/Pytest-35%2F35%20Başarılı-51cf66?style=for-the-badge)](#8-otomatik-testler-ve-senaryo-doğrulaması)

**İHA Telemetri Analiz ve Görselleştirme İstasyonu**, İnsansız Hava Araçlarından (İHA / SİHA) elde edilen CSV formatındaki uçuş telemetri kayıtlarını doğrulayan, hatalı satırları ayıklayıp **kısmi veri kurtarma (partial recovery)** uygulayan, kritik uçuş metriklerini ve **haberleşme kesintisi (timestamp gap)** anomalilerini hesaplayan modern bir masaüstü uygulamasıdır. Ayrıca aynı depo altında **`csv_senaryo_uretici/`** klasöründe 14 farklı uçuş ve hata senaryosu üretebilen bağımsız **İHA Telemetri CSV Senaryo Üretici (v1.6.0)** masaüstü uygulaması yer almaktadır.

> 📄 **Kapsamlı Word (`.docx`) Teknik Raporu:** Literatür taraması, kütüphane karşılaştırmaları, telemetri fiziği, karşılaşılan zorluklar/çözüm yolları ve test sonuçlarının tamamı için **[`IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx`](IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx)** (veya Markdown özeti olan [`TEKNIK_RAPOR.md`](TEKNIK_RAPOR.md)) belgesini inceleyebilirsiniz.

---

## 📌 İçindekiler
1. [Öne Çıkan Özellikler](#1-öne-çıkan-özellikler)
2. [Doğrudan İndir ve Çalıştır (Python Gerektirmez)](#2-doğrudan-indir-ve-çalıştır-python-gerektirmez)
3. [Antivirüs Uyumluluğu ve DigiCert İmzalı Mimari](#3-antivirüs-uyumluluğu-ve-digicert-imzalı-mimari)
4. [Telemetri Veri Yapısı ve Fiziksel Doğrulama Kuralları](#4-telemetri-veri-yapısı-ve-fiziksel-doğrulama-kuralları)
5. [Analiz Motoru ve Zaman Boşluğu (Gap) Tespiti](#5-analiz-motoru-ve-zaman-boşluğu-gap-tespiti)
6. [Kullanıcı Arayüzü (GUI) ve 4 Sekmeli Mimari](#6-kullanıcı-arayüzü-gui-ve-4-sekmeli-mimari)
7. [Geliştirici Kurulumu (Kaynak Koddan Çalıştırma)](#7-geliştirici-kurulumu-kaynak-koddan-çalıştırma)
8. [Otomatik Testler ve Senaryo Doğrulaması (35 Test)](#8-otomatik-testler-ve-senaryo-doğrulaması-35-test)
9. [Proje Dizin Yapısı](#9-proje-dizin-yapısı)

---

## 1. Öne Çıkan Özellikler

* **🎯 9 Eksende Çok Katmanlı Veri Doğrulama:** `timestamp`, `altitude`, `speed`, `battery_pct`, `longitude`, `latitude`, `pitch`, `roll`, `yaw` sütunlarının eksiksizliğini, veri tiplerini ve fiziksel sınırlarını denetler.
* **♻️ Kısmi Veri Kurtarma (Partial Recovery):** Dosyada bozuk veya sınır dışı satırlar bulunsa dahi geçerli satırları kurtararak analize devam eder; reddedilen her satırı **Satır Numarası, Sütun Adı, Hata Nedeni ve Girilen Ham Değer** ile birlikte raporlar.
* **📄 Ham CSV ve Ayıklanmış Veri Şeffaflığı:** Kullanıcı hem diskteki el değmemiş orijinal CSV metnini (`📄 Ham CSV Dosyası (Orijinal)` sekmesinde), hem de doğrulama motorundan geçen temiz verileri (`📋 Doğrulanmış / Geçerli Veri Tablosu` sekmesinde) yan yana inceleyebilir.
* **🧪 Bağımsız CSV Senaryo Üretici (`csv_senaryo_uretici/`):** 14 farklı uçuş ve hata senaryosunu canlı önizleme ve akıllı sıralı klasörleme (`Üretilen Klasör N - Tarih`) mimarisiyle üretir.
* **🔔 Akıllı Bildirim (Popup) Yönetimi:** Kullanıcı deneyimini bozmamak adına **yalnızca hata veya veri kaybı tespit edildiğinde** açıklayıcı uyarı penceresi (popup) açılır; %100 geçerli dosyalarda gereksiz popup gösterilmez.
* **📈 Zaman Serisi ve Kesinti (Gap) Görselleştirme:** İrtifa, Hız ve Batarya değişimlerini zamana bağlı alt alta 3 senkronize grafikte çizer; veri kesintisi ($\Delta t > \text{Eşik}$) yaşanan zaman aralıklarını grafik üzerinde **kırmızı yarı saydam anomali bölgesi (`axvspan`)** ile vurgular.

---

## 2. Doğrudan İndir ve Çalıştır (Python Gerektirmez!)

Bilgisayarınızda Python veya herhangi bir kütüphane kurulu olmasına gerek yoktur:

1. Taşınabilir paket klasörü içerisindeki **`IHA_Telemetri_Analiz Baslat.vbs`** (veya `Baslat.bat`) dosyasına çift tıklayın.
2. CSV Senaryo Üretici için **`csv_senaryo_uretici/Baslat.bat`** (veya taşınabilir kısayoluna) çift tıklayın.
3. Özel İHA açılış ekranı (Splash) belirecek ve 1.8 saniye içinde ana istasyon ekranı açılacaktır!

---

## 3. Antivirüs Uyumluluğu ve DigiCert İmzalı Mimari

Standart `PyInstaller --onefile` ile derlenen `.exe` dosyaları, imzasız bir önyükleyici (`runw.exe`) kullandıkları için Windows Defender (`Program:Win32/Wacapew.C!ml`) ve Avast (`IDP.HELU.PSD11`) tarafından yanlış pozitif (false positive) olarak engellenebilmektedir.

Bu projede bu sorunu kökten çözmek için **%100 DigiCert Kriptografik İmzalı Taşınabilir Çalışma Zamanı (Signed Embedded Runtime)** mimarisi kullanılmıştır:
* Paketin içerisindeki tüm çalıştırılabilir dosyalar (`pythonw.exe`, `python.exe`, `python312.dll`) bizzat **Python Software Foundation (`DigiCert Trusted G4 Code Signing RSA4096 SHA384`)** tarafından resmi olarak imzalanmıştır (`Status: Valid`).
* Paket içerisinde **sıfır (0) adet imzasız `.exe`** bulunur. Bu sayede hiçbir bilgisayarda antivirüs veya SmartScreen uyarısı tetiklenmez.

---

## 4. Telemetri Veri Yapısı ve Fiziksel Doğrulama Kuralları

Uygulama, yüklenen CSV dosyasında aşağıdaki **9 zorunlu sütunu** ve fiziksel sınırları denetler:

| Sütun Adı | Veri Tipi | Birim / Format | Kabul Edilen Fiziksel Sınır | Reddedilme Durumu (Örnek) |
| :--- | :--- | :--- | :--- | :--- |
| **`timestamp`** | Tarih/Zaman | `YYYY-MM-DD HH:MM:SS` | Geçerli ISO-8601 / Tarih-Saat | `"HATALI_ZAMAN_2026"`, boş değer |
| **`altitude`** | Sayısal (`float`) | Metre ($m$) | $[-500.0,\ 50000.0]$ | Metin (`"METIN_HATASI"`), boş hücre |
| **`speed`** | Sayısal (`float`) | Metre/Saniye ($m/s$) | $\ge 0.0\ m/s$ *(Negatif olamaz)* | Negatif hız (`-10.0`), metin, boş hücre |
| **`battery_pct`** | Sayısal (`float`) | Yüzde ($\%$) | $[0.0,\ 100.0]$ | `120.0`, `-8.0`, metin, boş hücre |
| **`longitude`** | Sayısal (`float`) | Derece ($^\circ$) | $[-180.0,\ +180.0]$ (WGS-84) | `-195.0`, `185.0`, boş hücre |
| **`latitude`** | Sayısal (`float`) | Derece ($^\circ$) | $[-90.0,\ +90.0]$ (WGS-84) | `94.0`, `-95.0`, boş hücre |
| **`pitch`** | Sayısal (`float`) | Derece ($^\circ$) | $[-180.0,\ +180.0]$ | `210.0`, boş hücre |
| **`roll`** | Sayısal (`float`) | Derece ($^\circ$) | $[-180.0,\ +180.0]$ | `-250.0`, boş hücre |
| **`yaw`** | Sayısal (`float`) | Derece ($^\circ$) | $[-360.0,\ +360.0]$ | `450.0`, boş hücre |

---

## 5. Analiz Motoru ve Zaman Boşluğu (Gap) Tespiti

Doğrulamadan geçen geçerli kayıtlar kronolojik olarak sıralanır ve şu analizler gerçekleştirilir:
1. **İrtifa Analizi:** Minimum İrtifa ($\min$), Maksimum İrtifa ($\max$) ve Ortalama İrtifa ($\mu_{\text{alt}}$).
2. **Hız Analizi:** Uçuş boyunca kaydedilen Ortalama Hız ($\mu_{\text{speed}}$).
3. **Batarya Analizi:** Uçuş sırasında görülen En Düşük Batarya Yüzdesi ($\min_{\text{bat}}$).
4. **Zaman Boşluğu (Timestamp Gap) Tespiti:**
   * Ardışık iki geçerli telemetri paketi arasındaki zaman farkı hesaplanır: $\Delta t_i = t_i - t_{i-1}$.
   * Eğer $\Delta t_i > \text{Eşik Değeri}$ (Varsayılan: **3.0 saniye**) ise bu aralık bir **Haberleşme / Veri Kaybı Anomalisi** olarak kaydedilir ve grafiklerde kırmızı bölgeyle işaretlenir.

---

## 6. Kullanıcı Arayüzü (GUI) ve 4 Sekmeli Mimari

* **Üst Kontrol Çubuğu:** Özel SİHA/İHA ikonu, CSV Dosyası Seçici, Dinamik Zaman Boşluğu Eşiği girişi (varsayılan `3.0` sn) ve Analiz Et butonu.
* **7'li KPI Özet Kartları:** Toplam/Geçerli Kayıt, Hatalı Kayıt Sayısı, Ortalama İrtifa, Min/Maks İrtifa, Ortalama Hız, Min Batarya ve Tespit Edilen Boşluk sayısı.
* **4 Sekmeli Çalışma Alanı:**
  1. `📈 Telemetri Grafikleri`: İrtifa, Hız ve Batarya zaman serileri + Kırmızı kesinti (gap) bölgeleri.
  2. `📋 Doğrulanmış / Geçerli Veri Tablosu`: Doğrulamadan geçen tüm satırların temiz tablo görünümü.
  3. `⚠️ Hatalı Kayıtlar Raporu`: Elenen hatalı satırların satır numarası, sütunu, red nedeni ve girilen geçersiz değeri.
  4. `📄 Ham CSV Dosyası (Orijinal)`: Seçilen CSV dosyasının diskteki filtrelenmemiş, el değmemiş orijinal metin içeriği ve kopyalama aracı.

---

## 7. Geliştirici Kurulumu (Kaynak Koddan Çalıştırma)

Kaynak kod üzerinden çalıştırmak veya geliştirmek için:

```bash
# 1. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 2. Ana Telemetri Analiz İstasyonunu başlatın
python gui_app.py

# 3. Ekstra CSV Senaryo Üretici Uygulamasını başlatın
python csv_senaryo_uretici/app.py
```

---

## 8. Otomatik Testler ve Senaryo Doğrulaması (35 Test)

Projede görev dokümanındaki **10 zorunlu senaryoyu**, **5 ek sınır senaryosunu** ve **20 motor/klasörleme/ham veri testini** doğrulayan toplam **35 adet otomatik `pytest` birim ve entegrasyon testi** bulunmaktadır.

Testleri çalıştırmak için proje ana dizininde şu komutu yürütün:

```powershell
# PowerShell:
$env:PYTHONPATH="."; python -m pytest tests -v

# CMD veya Bash:
python -m pytest tests -v
```

---

## 9. Proje Dizin Yapısı

```text
iha-telemetri-analiz/
├── gui_app.py                                           # Ana İHA Telemetri Analiz İstasyonu Arayüzü (v1.6.0)
├── telemetry_validator.py                               # 9 Sütun Doğrulama ve Kısmi Veri Kurtarma Motoru
├── telemetry_analyzer.py                                # İstatistik ve Zaman Boşluğu (Gap) Analiz Motoru
├── data_generator.py                                    # Sentetik Veri ve Senaryo Üretim Motoru
├── IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx     # Kapsamlı Word Teknik Tasarım ve Literatür Raporu
├── TEKNIK_RAPOR.md                                      # Teknik Rapor Markdown Özeti
├── README.md                                            # Proje ve Otomatik Test Kullanım Kılavuzu
├── requirements.txt                                     # Python Kütüphane Bağımlılıkları
├── csv_senaryo_uretici/                                 # Ekstra Uygulama: Bağımsız CSV Senaryo Üretici (v1.6.0)
│   ├── app.py                                           # Senaryo Üretici Masaüstü Arayüzü
│   ├── scenario_engine.py                               # 14 Senaryo ve Akıllı Sıralı Klasörleme Motoru
│   ├── assets/                                          # Senaryo Üretici İkonları
│   └── README.md                                        # Senaryo Üretici Kılavuzu
├── screenshots/                                         # Arayüz ve Hata Senaryoları Ekran Görüntüleri Klasörü
├── assets/                                              # Ana Uygulama İkonları (telemetry_icon.ico / .png)
├── samples/                                             # Örnek Test CSV Dosyaları
└── tests/                                               # 35 Adet Otomatik Pytest Birim ve Senaryo Testi
```

