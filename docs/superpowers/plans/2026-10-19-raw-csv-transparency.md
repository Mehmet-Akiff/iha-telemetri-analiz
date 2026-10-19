# Ham CSV Şeffaflığı ve Doğrulanmış Veri Ayrımı Uygulama Planı (v1.6.0)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** İHA Telemetri Analiz İstasyonu'na "📄 Ham CSV Dosyası (Orijinal)" 4. sekmesini eklemek, mevcut tabloyu "📋 Doğrulanmış / Geçerli Veri Tablosu" olarak netleştirmek ve CSV Senaryo Üretici'de senaryo hata durum rozetlerini şeffaflaştırarak v1.6.0 sürümünü yayınlamak.

**Architecture:**
- `gui_app.py`: `CTkTabview` bileşenine 4. sekme (`tab_raw`) eklenir. Dosya seçildiğinde/analiz edildiğinde diskteki orijinal dosya hiçbir filtreleme yapılmaksızın `open(..., encoding='utf-8')` ile okunur ve Consolas yazı tipiyle CTKTextbox içine aktarılır.
- `app.py` (Senaryo Üretici): Senaryo değişiminde ve canlı önizlemede her senaryonun ne tür hata içerdiği (veya 1. senaryonun %100 hatasız olduğu) durum rozetinde ve açıklama panelinde kullanıcıya doğrudan bildirilir.
- `dist_signed` & Masaüstü Dağıtımı: Her iki uygulama v1.6.0'a yükseltilir ve masaüstü klasörüne senkronize edilir.

**Tech Stack:** Python 3.12, CustomTkinter, Matplotlib, Tkinter ttk, pytest.

---

### Task 1: Telemetri Analiz İstasyonu (`gui_app.py`) Ham CSV Sekmesi ve İsimlendirme Güncellemesi

**Files:**
- Modify: `c:/Users/PC/Desktop/Projects/İME Proje/gui_app.py`
- Test: `c:/Users/PC/Desktop/Projects/İME Proje/tests/test_raw_view.py`

**Steps:**
- [ ] Step 1: Ham CSV okuma ve metin sunumu için bir test dosyası (`tests/test_raw_view.py`) yaz.
- [ ] Step 2: Testi çalıştır ve doğrula.
- [ ] Step 3: `gui_app.py` içinde sürümü `v1.6.0` yap; 2. sekmenin adını `"📋 Doğrulanmış / Geçerli Veri Tablosu"` yap; 4. sekme `"📄 Ham CSV Dosyası (Orijinal)"` bileşenini ekle.
- [ ] Step 4: `select_file` ve `run_analysis` fonksiyonlarında ham dosya içeriğini okuyup `txt_raw_csv` bileşenine yükleyen mekanizmayı ekle.
- [ ] Step 5: Testleri çalıştır ve tüm testlerin geçtiğini doğrula.

---

### Task 2: CSV Senaryo Üretici (`app.py`) Hata Durum Rozetleri ve Açıklık İyileştirmesi

**Files:**
- Modify: `c:/Users/PC/Desktop/Projects/iha-csv-senaryo-uretici/app.py`
- Test: `c:/Users/PC/Desktop/Projects/İME Proje/tests/test_scenario_generator.py`

**Steps:**
- [ ] Step 1: `app.py` sürümünü `v1.6.0` yap.
- [ ] Step 2: `preview_data_action` fonksiyonunda `valid`, `with_gaps`, `mixed`, `text_in_numeric` gibi tüm senaryolar için net hata/temiz veri açıklaması durum rozeti ekle.
- [ ] Step 3: Önizleme üst başlığına ve sekme başlıklarına açıklayıcı detaylar ekle.
- [ ] Step 4: Testleri çalıştır.

---

### Task 3: Taşınabilir (Portable) Çalışma Zamanları ve Masaüstü Paketlerinin Güncellenmesi (v1.6.0)

**Files:**
- Modify: `c:/Users/PC/Desktop/Projects/İME Proje/dist_signed/`
- Modify: `c:/Users/PC/Desktop/Projects/iha-csv-senaryo-uretici/dist_signed/`
- Update: `C:/Users/PC/Desktop/IHA_Masaustu_Uygulamalari/`

**Steps:**
- [ ] Step 1: `gui_app.py` ve `app.py` dosyalarını ilgili `dist_signed` çalışma zamanı klasörlerine senkronize et.
- [ ] Step 2: Masaüstündeki `C:/Users/PC/Desktop/IHA_Masaustu_Uygulamalari/` klasöründeki dosyaları `v1.6.0` ile güncelle.
- [ ] Step 3: Her iki uygulamanın başlatılmasını test et ve ekran doğrulaması yap.
- [ ] Step 4: Kullanıcıya net rapor ve kanıt sun.
