# 🛸 İHA Telemetri Analiz ve Görselleştirme İstasyonu (v1.4.0)

[![Version](https://img.shields.io/badge/Sürüm-v1.4.0-00d2ff?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-telemetri-analiz/releases/tag/v1.4.0)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-telemetri-analiz/releases)
[![Security](https://img.shields.io/badge/Güvenlik-DigiCert%20İmzalı%20Motor-2b8a3e?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-telemetri-analiz/releases/tag/v1.4.0)
[![Tests](https://img.shields.io/badge/Pytest-30%2F30%20Başarılı-51cf66?style=for-the-badge)](#8-otomatik-testler-ve-senaryo-doğrulaması)

**İHA Telemetri Analiz ve Görselleştirme İstasyonu**, İnsansız Hava Araçlarından (İHA / SİHA) elde edilen CSV formatındaki uçuş telemetri kayıtlarını doğrulayan, hatalı satırları ayıklayıp **kısmi veri kurtarma (partial recovery)** uygulayan, kritik uçuş metriklerini ve **haberleşme kesintisi (timestamp gap)** anomalilerini hesaplayan modern bir masaüstü uygulamasıdır.

> 📄 **Akademik ve Mühendislik Raporu:** Kütüphane karşılaştırmaları, telemetri fiziği ve eşik değeri gerekçelendirmelerinin tamamı için depodaki **[`TEKNIK_RAPOR.md`](TEKNIK_RAPOR.md)** belgesini inceleyebilirsiniz.

---

## 📌 İçindekiler
1. [Öne Çıkan Özellikler](#1-öne-çıkan-özellikler)
2. [Doğrudan İndir ve Çalıştır (Python Gerektirmez)](#2-doğrudan-indir-ve-çalıştır-python-gerektirmez)
3. [Antivirüs Uyumluluğu ve DigiCert İmzalı Mimari](#3-antivirüs-uyumluluğu-ve-digicert-imzalı-mimari)
4. [Telemetri Veri Yapısı ve Fiziksel Doğrulama Kuralları](#4-telemetri-veri-yapısı-ve-fiziksel-doğrulama-kuralları)
5. [Analiz Motoru ve Zaman Boşluğu (Gap) Tespiti](#5-analiz-motoru-ve-zaman-boşluğu-gap-tespiti)
6. [Kullanıcı Arayüzü (GUI) ve Animasyon Sistemi](#6-kullanıcı-arayüzü-gui-ve-animasyon-sistemi)
7. [Geliştirici Kurulumu (Kaynak Koddan Çalıştırma)](#7-geliştirici-kurulumu-kaynak-koddan-çalıştırma)
8. [Otomatik Testler ve Senaryo Doğrulaması](#8-otomatik-testler-ve-senaryo-doğrulaması)
9. [Proje Dizin Yapısı](#9-proje-dizin-yapısı)

---

## 1. Öne Çıkan Özellikler

* **🎯 9 Eksende Çok Katmanlı Veri Doğrulama:** `timestamp`, `altitude`, `speed`, `battery_pct`, `longitude`, `latitude`, `pitch`, `roll`, `yaw` sütunlarının eksiksizliğini, veri tiplerini ve fiziksel sınırlarını denetler.
* **♻️ Kısmi Veri Kurtarma (Partial Recovery):** Dosyada bozuk veya sınır dışı satırlar bulunsa dahi geçerli satırları kurtararak analize devam eder; reddedilen her satırı **Satır Numarası, Sütun Adı, Hata Nedeni ve Girilen Ham Değer** ile birlikte raporlar.
* **🔔 Akıllı Bildirim (Popup) Yönetimi:** Kullanıcı deneyimini bozmamak adına **yalnızca hata veya veri kaybı tespit edildiğinde** açıklayıcı uyarı penceresi (popup) açılır; %100 geçerli dosyalarda gereksiz popup gösterilmez.
* **📈 Zaman Serisi ve Kesinti (Gap) Görselleştirme:** İrtifa, Hız ve Batarya değişimlerini zamana bağlı alt alta 3 senkronize grafikte çizer; veri kesintisi ($\Delta t > \text{Eşik}$) yaşanan zaman aralıklarını grafik üzerinde **kırmızı yarı saydam anomali bölgesi (`axvspan`)** ile vurgular.
* **✨ Profesyonel Arayüz ve Animasyonlar:**
  * İlk tıklamada kullanıcıya geri bildirim veren **1.8 saniyelik animasyonlu İHA Açılış Ekranı (Splash Screen)**.
  * Ana pencere açılışında yumuşak **Fade-In** geçişi.
  * Sekmeler (Grafik / Tablo / Hata Raporu) arasında geçiş yaparken **Siyan Parlama (Glow Pulse)** animasyonu.
  * Analiz tamamlandığında KPI kartlarında **canlı sayı sayacı (Counter Animation)** efekti.

---

## 2. Doğrudan İndir ve Çalıştır (Python Gerektirmez!)

Bilgisayarınızda Python veya herhangi bir kütüphane kurulu olmasına gerek yoktur:

1. **[GitHub Releases (v1.4.0) Sayfasına Gidin](https://github.com/Mehmet-Akiff/iha-telemetri-analiz/releases/tag/v1.4.0)**
2. **`IHA_Telemetri_Analiz_DigiCert_Signed_v1.4.0.zip`** dosyasını indirin ve bir klasöre çıkartın.
3. Klasör içerisindeki **`IHA_Telemetri_Analiz Baslat.vbs`** (veya `IHA_Telemetri_Analiz Baslat.bat`) dosyasına çift tıklayın.
4. Özel İHA açılış ekranı (Splash) belirecek ve 1.8 saniye içinde ana istasyon ekranı açılacaktır!

---

## 3. Antivirüs Uyumluluğu ve DigiCert İmzalı Mimari

Standart `PyInstaller --onefile` ile derlenen `.exe` dosyaları, imzasız bir önyükleyici (`runw.exe`) kullandıkları ve her açılışta `%TEMP%` klasörüne `.dll` çıkarttıkları için Avast (`IDP.HELU.PSD11`) ve Windows Defender SmartScreen tarafından "Bilinmeyen Yayımcı / Dropper" olarak engellenebilmektedir.

Bu projede (`v1.3.0+` ve `v1.4.0`) bu sorunu kökten çözmek için **%100 DigiCert Kriptografik İmzalı Taşınabilir Çalışma Zamanı (Signed Embedded Runtime)** mimarisi kullanılmıştır:
* Paketin içerisindeki tüm çalıştırılabilir dosyalar (`pythonw.exe`, `python.exe`, `python312.dll`) bizzat **Python Software Foundation (`DigiCert Trusted G4 Code Signing RSA4096 SHA384`)** tarafından resmi olarak imzalanmıştır (`Status: Valid`).
* Paket içerisinde **sıfır (0) adet imzasız `.exe`** bulunur. Bu sayede hiçbir bilgisayarda antivirüs veya SmartScreen uyarısı tetiklenmez.

---

## 4. Telemetri Veri Yapısı ve Fiziksel Doğrulama Kuralları

Uygulama, yüklenen CSV dosyasında aşağıdaki **9 zorunlu sütunu** ve fiziksel sınırları denetler:

| Sütun Adı | Veri Tipi | Birim / Format | Kabul Edilen Fiziksel Sınır | Reddedilme Durumu (Örnek) |
| :--- | :--- | :--- | :--- | :--- |
| **`timestamp`** | Tarih/Zaman | `YYYY-MM-DD HH:MM:SS` | Geçerli ISO-8601 / Tarih-Saat | `"bozuk_tarih"`, `"2026-13-45"`, boş değer |
| **`altitude`** | Sayısal (`float`) | Metre ($m$) | $[-500.0,\ 50000.0]$ | Metin (`"abc"`), aşırı uç değer, boş hücre |
| **`speed`** | Sayısal (`float`) | Metre/Saniye ($m/s$) | $\ge 0.0\ m/s$ *(Negatif olamaz)* | Negatif hız (`-10.5`), metin, boş hücre |
| **`battery_pct`** | Sayısal (`float`) | Yüzde ($\%$) | $[0.0,\ 100.0]$ | `105.0`, `-5.0`, metin, boş hücre |
| **`longitude`** | Sayısal (`float`) | Derece ($^\circ$) | $[-180.0,\ +180.0]$ (WGS-84) | `195.4`, `-185.0`, boş hücre |
| **`latitude`** | Sayısal (`float`) | Derece ($^\circ$) | $[-90.0,\ +90.0]$ (WGS-84) | `95.2`, `-91.0`, boş hücre |
| **`pitch`** | Sayısal (`float`) | Derece ($^\circ$) | $[-90.0,\ +90.0]$ | `110.0`, `-95.0`, boş hücre |
| **`roll`** | Sayısal (`float`) | Derece ($^\circ$) | $[-180.0,\ +180.0]$ | `200.0`, `-190.0`, boş hücre |
| **`yaw`** | Sayısal (`float`) | Derece ($^\circ$) | $[-360.0,\ +360.0]$ | `400.0`, `-370.0`, boş hücre |

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

## 6. Kullanıcı Arayüzü (GUI) ve Animasyon Sistemi

* **Üst Kontrol Çubuğu:** Özel SİHA/İHA ikonu, CSV Dosyası Seçici, Dinamik Zaman Boşluğu Eşiği girişi (varsayılan `3.0` sn) ve Analiz Et butonu.
* **7'li KPI Özet Kartları:** Toplam/Geçerli Kayıt, Hatalı Kayıt Sayısı, Ortalama İrtifa, Min/Maks İrtifa, Ortalama Hız, Min Batarya ve Tespit Edilen Boşluk sayısı.
* **3 Sekmeli Çalışma Alanı:**
  1. `📈 Telemetri Grafikleri`: İrtifa, Hız ve Batarya zaman serileri + Kırmızı kesinti (gap) bölgeleri.
  2. `📋 Geçerli Veri Tablosu`: Doğrulamadan geçen tüm satırların temiz tablo görünümü.
  3. `⚠️ Hatalı Kayıtlar Raporu`: Elenecek hatalı satırların satır numarası, sütunu ve detaylı red nedeni.

---

## 7. Geliştirici Kurulumu (Kaynak Koddan Çalıştırma)

Kaynak kod üzerinden çalıştırmak veya geliştirmek için:

```bash
# 1. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 2. Uygulamayı başlatın
python gui_app.py
```

---

## 8. Otomatik Testler ve Senaryo Doğrulaması

Projede görev dokümanındaki 10 zorunlu senaryoyu ve ek sınır durumlarını (edge-cases) doğrulayan **30 adet otomatik `pytest` birim ve entegrasyon testi** bulunmaktadır:

```bash
python -m pytest -v
```

---

## 9. Proje Dizin Yapısı

```text
iha-telemetri-analiz/
├── gui_app.py                   # CustomTkinter + Matplotlib Masaüstü Arayüzü (v1.4.0)
├── telemetry_validator.py       # 9 Sütun Doğrulama ve Kısmi Veri Kurtarma Motoru
├── telemetry_analyzer.py        # İstatistik ve Zaman Boşluğu (Gap) Analiz Motoru
├── create_assets.py             # Özel İHA/SİHA İkon (.ico/.png) Üretim Betiği
├── build_signed_dist.py         # DigiCert İmzalı Taşınabilir Paket Oluşturucu
├── README.md                    # Kapsamlı Proje ve Kullanım Dokümantasyonu
├── TEKNIK_RAPOR.md              # Mühendislik Araştırması, Kütüphane ve Mimari Raporu
├── requirements.txt             # Python Kütüphane Bağımlılıkları
├── assets/                      # Uygulama İkonları (telemetry_icon.ico / .png)
├── samples/                     # Örnek Test CSV Dosyaları
└── tests/                       # 30 Adet Otomatik Pytest Birim ve Senaryo Testi
```
