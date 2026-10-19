# Proje Teslim Paketi, Ekran Görüntüleri ve Kapsamlı Word (.docx) Raporu Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Can Bey'in geri bildirimleri doğrultusunda; gerçek uygulama ekran görüntülerini (`screenshots/`) üretmek, CSV Senaryo Üretici'yi ana repo altında ayrı bir klasöre (`csv_senaryo_uretici/`) entegre etmek, Abstract, Tablolar, Görseller, Karşılaşılan Zorluklar/Çözümler ve Kaynakça içeren profesyonel Word (`.docx`) Teknik Raporunu oluşturmak ve tüm teslimatı tek bir `.zip` arşivi halinde hazırlamak.

**Architecture:**
1. **Alt Klasör Entegrasyonu (`csv_senaryo_uretici/`):** Ana proje dizini (`c:\Users\PC\Desktop\Projects\İME Proje`) içerisine `csv_senaryo_uretici/` klasörü açılarak bağımsız CSV Senaryo Üretici uygulaması (`app.py`, `scenario_engine.py`, `assets/`, `README.md`) buraya yerleştirilir.
2. **Otomatik Ekran Görüntüsü Üretimi (`screenshots/`):** Uygulamanın gerçek arayüzünü ve hata popup senaryolarını (1. Başarılı Uçuş & Grafikler, 2. Zaman Kesintili Uçuş / Gap Anomalisi, 3. Kısmi Hatalı Uçuş & Hatalı Kayıtlar Raporu, 4. Ham CSV Orijinal Sekmesi, 5. Dosya Seçilmeden Analiz Uyarı Popup'ı, 6. Bozuk/Boş Dosya Kritik Hata Popup'ı, 7. Eksik Sütunlu Dosya Hata Popup'ı, 8. Sıfır Geçerli Kayıt Hata Popup'ı, 9. CSV Senaryo Üretici Arayüzü, 10. İHA 6-DOF Eksen Diyagramı) yüksek çözünürlüklü PNG olarak `screenshots/` klasörüne kaydeden bir betik çalıştırılır.
3. **Kapsamlı Word Raporu (`IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx`):** `python-docx` kullanılarak kapak sayfası, Türkçe/İngilizce Abstract, 9 telemetri verisi tablosu, kütüphane seçim ve alternatif karşılaştırma tabloları, sistem mimarisi, zaman boşluğu eşiği (3.0 sn) gerekçelendirmesi, geliştirme sürecinde karşılaşılan 5 gerçek zorluk/hata ve çözüm yolları, gömülü hata senaryosu görselleri, 35 otomatik test tablosu ve IEEE formatında kaynakça içeren Word belgesi üretilir.
4. **Teslimat Arşivi (`.zip`) ve GitHub Senkronizasyonu:** Hem GitHub reposu güncellenir hem de masaüstünde teslim edilmeye hazır `IHA_Telemetri_Proje_Teslimi_Mehmet_Akif_Urey.zip` paketi oluşturulur.

**Tech Stack:** Python 3.12, `python-docx`, `Pillow (PIL)`, `CustomTkinter`, `Matplotlib`, `pytest`.

---

### Task 1: Ana Repo İçinde `csv_senaryo_uretici/` Alt Klasörünün Oluşturulması

**Files:**
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/csv_senaryo_uretici/app.py`
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/csv_senaryo_uretici/scenario_engine.py`
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/csv_senaryo_uretici/README.md`
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/csv_senaryo_uretici/Baslat.bat`

**Steps:**
- [ ] Step 1: `iha-csv-senaryo-uretici` içindeki güncel `v1.6.0` kaynak dosyalarını ve `assets/` klasörünü `İME Proje/csv_senaryo_uretici/` altına kopyala.
- [ ] Step 2: `csv_senaryo_uretici` içindeki modüllerin bağımsız çalışabildiğini doğrula.

---

### Task 2: Arayüz ve Hata Senaryoları Görsellerinin (`screenshots/`) Oluşturulması

**Files:**
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/generate_screenshots.py`
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/screenshots/*.png`

**Steps:**
- [ ] Step 1: Gerçek veri setleriyle (`samples/`) analiz sonuçlarını, grafikleri, tabloları, hata popup pencerelerini ve İHA eksen diyagramını yüksek çözünürlüklü PNG olarak üreten `generate_screenshots.py` betiğini yaz.
- [ ] Step 2: Betiği çalıştır ve `screenshots/` klasöründe tüm 10 görselin oluştuğunu ve boyutlarının geçerli olduğunu doğrula.

---

### Task 3: Profesyonel Word (`.docx`) Teknik Raporunun Oluşturulması

**Files:**
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/generate_word_report.py`
- Create: `c:/Users/PC/Desktop/Projects/İME Proje/IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx`

**Steps:**
- [ ] Step 1: Can Bey'in istediği tüm bölümleri (Abstract, Tablolar, Neler Yapıldı / Neler Eklendi, Nelerde Zorlanıldı ve Hatalar Nasıl Çözüldü, Görselli Hata Senaryoları, 35 Otomatik Test, IEEE Kaynakça) içeren `generate_word_report.py` betiğini yaz.
- [ ] Step 2: Betiği çalıştırarak `.docx` dosyasını üret ve `python-docx` ile paragraf, tablo ve gömülü görsel sayılarını doğrula.

---

### Task 4: README Güncellemesi, GitHub Push ve `.zip` Teslim Paketinin Hazırlanması

**Files:**
- Modify: `c:/Users/PC/Desktop/Projects/İME Proje/README.md`
- Create: `C:/Users/PC/Desktop/IHA_Masaustu_Uygulamalari/IHA_Telemetri_Proje_Teslimi_Mehmet_Akif_Urey.zip`

**Steps:**
- [ ] Step 1: `README.md` dosyasını yeni klasör yapısını (`csv_senaryo_uretici/`, `screenshots/`, `IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx`) ve otomatik test çalıştırma adımlarını içerecek şekilde güncelle.
- [ ] Step 2: Tüm 35 otomatik testi `pytest` ile yeniden çalıştır ve %100 geçtiğini kanıtla.
- [ ] Step 3: GitHub reposuna commit ve push yap.
- [ ] Step 4: Teslim edilecek tüm dosyaları içeren temiz `.zip` arşivini masaüstünde oluştur ve içeriğini doğrula.
