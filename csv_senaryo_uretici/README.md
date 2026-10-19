# 🧪 İHA Telemetri CSV Senaryo Üretici (v1.5.0)

[![Version](https://img.shields.io/badge/Sürüm-v1.5.0-2bda72?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-csv-senaryo-uretici/releases/tag/v1.5.0)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-csv-senaryo-uretici/releases)
[![Security](https://img.shields.io/badge/Güvenlik-DigiCert%20İmzalı%20Motor-2b8a3e?style=for-the-badge)](https://github.com/Mehmet-Akiff/iha-csv-senaryo-uretici/releases/tag/v1.5.0)

**İHA Telemetri CSV Senaryo Üretici**, İHA yer kontrol istasyonlarını ve telemetri analiz yazılımlarını uçtan uca test etmek amacıyla geliştirilmiş, **14 farklı uçuş, sensör arızası ve veri bozulması senaryosunu** üretebilen bağımsız bir masaüstü simülasyon uygulamasıdır.

---

## 🌟 Öne Çıkan Yenilikler (v1.5.0)

* **⚡ Anında Canlı Önizleme (Instant Auto-Preview):**
  * Sol paneldeki açılır listeden bir senaryo seçtiğiniz anda tablo ve ham CSV metni **otomatik olarak anında güncellenir**. Artık önizleme için ekstra bir şey yapmanıza gerek kalmaz.
  * Önizleme durum çubuğu senaryonun geçerli uçuş mu yoksa kasıtlı hata mı içerdiğini renkli durum rozetleriyle açıkça gösterir.
* **🗂️ Akıllı Sıralı Klasörleme (`Üretilen Klasör N - Tarih`):**
  * **Otomatik Numaralandırma:** Her "Üret" tıklandığında hedef dizindeki en büyük klasör numarası taranır ve **daima 1 fazlası** alınarak `Üretilen Klasör 1 - Tarih`, `Üretilen Klasör 2 - Tarih` şeklinde izole klasör oluşturulur.
  * **Silinme Koruması:** Eğer dizinden Klasör 1 silinirse ve Klasör 2 duruyorsa, sistem en büyük sayıyı (2) baz alarak otomatik olarak **3**'ten devam eder (`Üretilen Klasör 3`).
  * **Yeni Klasör Desteği:** Farklı veya yeni bir klasöre geçildiğinde otomatik olarak **1**'den başlar.
  * Arayüz üzerinde sıradaki klasör numarası (`📌 Sıradaki: Üretilen Klasör X`) ve seçili hedef dizin anlık olarak canlı gösterilir.
* **📦 Esnek Üretim Kapsamı:**
  1. **Temel Test Seti (5 Temel CSV):** Hızlı ve etkili testler için en kritik 5 senaryo (Geçerli Uçuş, Kesintili Uçuş, Karışık Hatalı Uçuş, Negatif Hız, Batarya Sınır İhlali).
  2. **Tüm Senaryolar (14 Test CSV'si):** Tüm sınır ve anomali senaryolarını içeren eksiksiz paket.
  3. **Yalnızca Seçili Senaryo (1 CSV):** O an önizlenen spesifik senaryo.
* **🚀 Tek Tıkla Üretim & Otomatik Açılış:**
  * Büyük yeşil `YENİ KLASÖRDE ÜRET` butonuna basıldığında herhangi bir kafa karıştırıcı pencere sormadan klasör açılır, dosyalar içine yazılır ve klasör Windows Gezgini'nde kullanıcının önüne açılır.
* **🛡️ %100 DigiCert İmzalı Çalışma Zamanı:**
  * Paket içerisindeki tüm çalıştırılabilir dosyalar resmi **Python Software Foundation (DigiCert)** dijital imzasına sahiptir; Avast ve Windows Defender tarafından sıfır uyarıyla (%100 güvenli) çalışır.

---

## 📥 Doğrudan İndir ve Çalıştır (Python Gerektirmez!)

1. **[GitHub Releases (v1.5.0) Sayfasına Gidin](https://github.com/Mehmet-Akiff/iha-csv-senaryo-uretici/releases/tag/v1.5.0)**
2. **`CSV_Senaryo_Uretici_DigiCert_Signed_v1.5.0.zip`** arşivini indirin ve bir klasöre çıkartın.
3. Klasör içerisindeki **`CSV_Senaryo_Uretici Baslat.vbs`** (veya `.bat`) dosyasına çift tıklayarak uygulamayı hemen başlatın!

---

## 🧪 Desteklenen 14 Telemetri Senaryosu

| # | Senaryo Kodu | Senaryo Açıklaması ve Test Amacı |
| :--- | :--- | :--- |
| **01** | `valid` | **%100 Geçerli Uçuş Verisi:** Kusursuz, gerçekçi tırmanış/seyir telemetri kaydı. |
| **02** | `with_gaps` | **Zaman Boşluğu (Kesintili Uçuş):** Belirtilen saniye kadar haberleşme kesintisi (data drop) içerir. |
| **03** | `mixed` | **Karışık / Kısmi Hatalı Veri:** Geçerli verilerin arasına serpiştirilmiş 5 farklı tipte hatalı satır (Kısmi kurtarma testi). |
| **04** | `negative_speed` | **Negatif Hız Hatası:** Fiziksel olarak imkansız negatif hız (`-12.5 m/s` vb.) içeren satırlar. |
| **05** | `battery_bounds` | **Batarya Sınır İhlali:** `%0`'ın altında (`-8%`) veya `%100`'ün üzerinde (`125%`) batarya değerleri. |
| **06** | `coord_bounds` | **Coğrafi Koordinat İhlali:** WGS-84 sınırları dışında enlem (`>90°`) ve boylam (`>180°`) değerleri. |
| **07** | `text_in_numeric` | **Sayısal Alanda Metin:** İrtifa, hız ve batarya sütunlarında bozuk metin (`"COK_YUKSEK"`) ifadeleri. |
| **08** | `empty_fields` | **Boş Zorunlu Hücreler:** Zorunlu telemetri sütunlarında eksik (`NaN`/boş) bırakılmış hücreler. |
| **09** | `bad_timestamps` | **Çözümlenemeyen Zaman Damgası:** Bozuk tarih/saat formatları (`"HATALI_ZAMAN_2026"`). |
| **10** | `bad_angles` | **Açısal Sınır İhlalleri:** Pitch, Roll ve Yaw açılarında fiziksel sınır dışı değerler. |
| **11** | `missing_columns` | **Eksik Zorunlu Sütunlar:** `speed` ve `battery_pct` sütunları eksik bırakılmış CSV yapısı. |
| **12** | `all_invalid` | **Sıfır Geçerli Kayıt:** Başlıkları doğru ancak içindeki tüm satırları hatalı olan dosya. |
| **13** | `empty_file` | **Boş Dosya (0 Bayt):** Tamamen boş dosya sınır durumu testi. |
| **14** | `corrupt_file` | **Bozuk CSV Sözdizimi:** Sütun sayısı tutarsız, ayrıştırılamayan bozuk metin yapısı. |

---

## 💻 Geliştirici Kurulumu (Kaynak Koddan Çalıştırma)

```bash
pip install -r requirements.txt
python app.py
```

---

## 📁 Proje Dizin Yapısı

```text
iha-csv-senaryo-uretici/
├── app.py                  # CustomTkinter Masaüstü Arayüzü (v1.5.0 - Akıllı Sıralı Üretim & Canlı Önizleme)
├── scenario_engine.py      # 14 Senaryolu Akıllı Numaralandırma ve Üretim Motoru
├── README.md               # Kapsamlı Kullanım ve Senaryo Kılavuzu
├── requirements.txt        # Python Bağımlılıkları
└── assets/                 # Özel İHA/Drone İkonları (generator_icon.ico / .png)
```
