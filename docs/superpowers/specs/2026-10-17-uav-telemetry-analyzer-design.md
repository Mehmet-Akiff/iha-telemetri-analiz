# İHA Telemetri Analiz ve Görselleştirme Uygulaması - Tasarım Dokümanı (Spec)

## 1. Giriş ve Amaç
Bu proje, CSV formatındaki İHA (İnsansız Hava Aracı) telemetri verilerini okuyabilen, çok katmanlı kurallarla doğrulayabilen, geçerli verileri analiz edip zaman serisi grafikleriyle görselleştirebilen, hatalı kayıtları raporlayan ve kullanıcı dostu bir masaüstü arayüzü sunan bir Python uygulamasıdır.

Uygulama gerçek bir İHA donanımına bağlanmaz; uçuş logları ve sentetik/örnek telemetri dosyaları üzerinden çalışır.

---

## 2. Telemetri Veri Formatı ve Anlamları
CSV dosyasında desteklenmesi zorunlu sütunlar ve havacılık/telemetri anlamları:
- **`timestamp`**: Telemetri paketinin kaydedildiği anı gösteren zaman damgası (ISO-8601 `YYYY-MM-DD HH:MM:SS` veya epoch formatı). Verilerin zamana göre sıralanması, frekansın izlenmesi ve haberleşme kesintilerinin tespiti için kritiktir.
- **`altitude`**: İHA'nın deniz seviyesinden (MSL) veya kalkış noktasından (AGL) olan yüksekliği (metre cinsinden). Uçuş irtifa emniyeti ve tırmanış/süzülüş profili için kullanılır.
- **`speed`**: İHA'nın yer hızı (Ground Speed) veya hava hızı (Airspeed) (m/s cinsinden). Fiziksel olarak skaler hız negatif olamaz (`speed >= 0`).
- **`battery_pct`**: Kalan batarya yüzdesi (`%0 - %100`). Uçuş süresi, kritik eve dönüş (RTH) eşiği ve emniyet için en kritik parametrelerdendir.
- **`longitude` (Boylam)**: WGS84 coğrafi koordinat sisteminde doğu/batı açısı (`-180.0` ile `+180.0` derece arası).
- **`latitude` (Enlem)**: WGS84 coğrafi koordinat sisteminde kuzey/güney açısı (`-90.0` ile `+90.0` derece arası).
- **`pitch` (Yunuslama)**: İHA'nın enine ekseni etrafındaki burun yukarı/aşağı dönme açısı (derece cinsinden, genelde `-90°` ile `+90°` veya `-180°` ile `+180°`).
- **`roll` (Yalpalama)**: İHA'nın boyuna ekseni etrafındaki sağa/sola yatış açısı (derece cinsinden, `-180°` ile `+180°`).
- **`yaw` (Sapma)**: İHA'nın dikey ekseni etrafındaki pusula yönelimi (Heading / Yaw, `0°` - `360°` veya `-180°` - `+180°`).

---

## 3. Mimari ve Bileşen Yapısı

```
+-------------------------------------------------------------+
|                         GUI Layer                           |
|      (CustomTkinter / Tkinter + Matplotlib FigureCanvas)    |
|   - File Picker   - Data Table (Treeview) - Summary Cards   |
|   - Matplotlib Canvas (Altitude, Speed, Battery, Gaps)      |
|   - Error Details Table & Modal Popups                      |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                 TelemetryAnalyzer Layer                     |
|   - min/max/avg altitude                                    |
|   - avg speed                                               |
|   - min battery                                             |
|   - abnormal timestamp gap detection (delta_t > threshold)  |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                 TelemetryValidator Layer                    |
|   - Header validation (required columns)                    |
|   - Row parsing, type conversions, numeric bounds           |
|   - Speed >= 0, 0 <= Battery <= 100                         |
|   - Lat [-90, 90], Lon [-180, 180]                          |
|   - Timestamp parseability                                  |
|   - Partial valid recovery & detailed error logging         |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                 Data Generator / CSV Layer                  |
|   - Generates valid, invalid, mixed, and corrupt datasets   |
+-------------------------------------------------------------+
```

### 3.1. `telemetry_validator.py`
- Girdiler: Dosya yolu veya dosya benzeri nesne / string.
- Çıktılar: `ValidationResult` veri sınıfı:
  - `valid_data`: `pandas.DataFrame` veya doğrulanmış kayıtlar listesi
  - `errors`: Satır numarası ve reddedilme nedenlerini içeren hata listesi `[{"row": int, "column": str, "message": str, "raw_value": str}]`
  - `is_valid`: En az bir geçerli satır var mı ve kritik yapısal hata yok mu boolean flag
  - `summary`: Toplam satır, geçerli satır, geçersiz satır sayısı
- Kurallar:
  1. Dosya varlığı, boş olmama (empty file check) ve CSV format doğrulaması
  2. Başlık satırında 9 zorunlu sütunun eksiksiz bulunması
  3. Satır bazında:
     - Hiçbir zorunlu alanın boş (`NaN`, `None`, `""`, whitespace) bırakılmaması
     - Sayısal olması gereken alanların (`altitude`, `speed`, `battery_pct`, `longitude`, `latitude`, `pitch`, `roll`, `yaw`) float tipine dönüştürülebilirliği
     - `speed >= 0` kontrolü
     - `0.0 <= battery_pct <= 100.0` kontrolü
     - `-90.0 <= latitude <= 90.0` kontrolü
     - `-180.0 <= longitude <= 180.0` kontrolü
     - `timestamp` parse edilebilirlik kontrolü
  4. Hatalı satırlar sessizce silinmez, her birinin satır numarası ve sebebi loglanır. Geçerli satırlar işlenmeye devam eder (Kısmi kurtarma).
  5. Dosyada sıfır geçerli kayıt varsa özel `NoValidRecordsError` fırlatılır/bildirilir.

### 3.2. `telemetry_analyzer.py`
- Girdiler: Doğrulanmış `pandas.DataFrame` (veya dict listesi) ve `time_gap_threshold_sec` (opsiyonel float).
- Analiz Hesaplamaları:
  - `avg_altitude`: Ortalama irtifa
  - `min_altitude`: Minimum irtifa
  - `max_altitude`: Maksimum irtifa
  - `avg_speed`: Ortalama hız
  - `min_battery`: Minimum batarya seviyesi
  - `total_flight_time`: İlk ve son geçerli timestamp arasındaki süre
  - `timestamp_gaps`: Zaman damgaları arasındaki olağan dışı boşluklar:
    - Veriler zaman damgasına göre kronolojik sıralanır.
    - Ardışık iki kayıt arasındaki fark $\Delta t = t_{i} - t_{i-1}$ hesaplanır.
    - Eşik mantığı:
      Telemetri yayınları tipik olarak 1 Hz veya daha yüksek frekansta akar. Eşik değeri varsayılan olarak **3.0 saniye** (veya medyan aralığın 3 katı) olarak tanımlanır. Bu süreyi aşan gecikmeler "Haberleşme/Kayıt Kesintisi (Data Drop)" olarak etiketlenir ve başlangıç zamanı, bitiş zamanı ve boşluk süresi (saniye) listelenir.
- Çıktılar: `AnalysisResult` dataclass / sözlük.

### 3.3. `data_generator.py`
- Test ve gösterim için 5 farklı CSV dosyası üretir:
  1. `telemetry_valid.csv`: 100% geçerli 50 satırlık gerçekçi İHA uçuş verisi.
  2. `telemetry_mixed.csv`: Hem geçerli hem de bilerek enjekte edilmiş geçersiz kayıtlar (negatif hız, %125 batarya, geçersiz koordinat, boş irtifa, bozuk tarih, metin içeren sayı).
  3. `telemetry_corrupted.csv`: Bozuk biçimli / geçersiz karakterli CSV.
  4. `telemetry_missing_columns.csv`: Bazı zorunlu sütunları eksik olan CSV.
  5. `telemetry_empty.csv`: 0 baytlık tamamen boş dosya.

### 3.4. `gui_app.py`
- Arayüz Kütüphanesi: `CustomTkinter` (Modern koyu/açık tema, yüksek çözünürlüklü ekran desteği) + `tkinter` Treeview + `matplotlib.backends.backend_tkagg.FigureCanvasTkAgg`.
- Görsel Bölümler:
  - **Üst Menü / Kontrol Çubuğu:** "CSV Dosyası Seç ve Yükle", "Analiz Et", "Örnek Veri Üret", "Eşik Değeri Ayarı".
  - **Özet Metrik Kartları:** Toplam Kayıt, Geçerli Kayıt, Hatalı Kayıt, Ort. İrtifa, Min/Maks İrtifa, Ort. Hız, Min Batarya, Tespit Edilen Kesinti Sayısı.
  - **Sekmeli Ana Panel:**
    - *Sekme 1 (Zaman Serisi Grafikleri):* İrtifa-Zaman, Hız-Zaman ve Batarya-Zaman grafikleri; anormal zaman boşluklarının grafik üzerinde dikey kesikli çizgiler ve renkli aralıklarla vurgulanması.
    - *Sekme 2 (Veri Tablosu):* Doğrulanmış telemetri verilerinin taranabilir tablosu.
    - *Sekme 3 (Hata ve Doğrulama Raporu):* Hangi satırların hangi nedenle reddedildiğini gösteren detaylı tablo.
  - **Bildirimler:** Hata popup pencereleri (`CTkMessagebox` / `messagebox.showerror`, `showwarning`) ve başarı bilgilendirme pencereleri (`showinfo`).

### 3.5. `tests/test_telemetry.py`
- `pytest` ile çalıştırılacak en az 15 test senaryosu:
  1. `test_valid_csv_loading`: Geçerli CSV'nin tam yüklenmesi
  2. `test_missing_required_column`: Zorunlu sütun eksikliğinde yakalama
  3. `test_empty_mandatory_field`: Zorunlu bir alan boşken satırın yakalanması
  4. `test_invalid_text_in_numeric_field`: Sayısal alana harf/metin girildiğinde hata
  5. `test_battery_bounds_check`: Batarya < 0 veya > 100 olduğunda hata
  6. `test_lat_lon_bounds_check`: Enlem/boylam sınırları dışında hata
  7. `test_empty_or_corrupt_csv`: Boş dosya veya bozuk CSV işleme
  8. `test_zero_valid_records`: Hiç geçerli kayıt içermeyen dosya kontrolü
  9. `test_analysis_metrics_accuracy`: Analiz sonuçlarının beklenen matematiksel değerlerle doğrulanması
  10. `test_timestamp_gap_detection`: Olağan dışı zaman boşluklarının doğru tespiti
  11. `test_mixed_records_partial_recovery`: Hatalı kayıtlar varken geçerli satırların başarıyla işlenmesi
  12. `test_negative_speed_rejection`: Negatif hız değerlerinin reddedilmesi
  13. `test_unparseable_timestamp_rejection`: Bozuk tarih/saat damgalarının reddi
  14. `test_angular_bounds_validation`: Pitch, Roll açı sınırlarının kontrolü
  15. `test_unsorted_timestamp_handling`: Kronolojik sırasız gelen verilerin analizde sıralanması
