# İHA Telemetri Analiz ve Görselleştirme Uygulaması - Teknik Rapor

**Sürüm:** v1.5.0  
**Proje Adı:** İHA Telemetri Analiz ve Görselleştirme İstasyonu & CSV Senaryo Üretici  
**Hazırlayan:** Mehmet Akif Ürey  


---

## 1. Giriş ve Görevin Kapsamı
Bu çalışma, CSV formatındaki İnsansız Hava Aracı (İHA) telemetri verilerini okuyan, yapısal ve fiziksel sınır kurallarına göre doğrulayan, **kısmi veri kurtarma (partial recovery)** yeteneğine sahip, uçuş dinamiklerini analiz eden ve sonuçları kullanıcı dostu modern bir masaüstü arayüzünde görselleştiren bir sistemin tasarım ve uygulamasını kapsamaktadır. Ayrıca sistemi uçtan uca test edebilmek amacıyla 14 farklı uçuş ve hata senaryosu üretebilen bağımsız bir **İHA Telemetri CSV Senaryo Üretici** masaüstü uygulaması geliştirilmiştir.

---

## 2. Telemetri Veri Alanlarının Araştırılması ve Fiziksel Anlamları
İHA sistemlerinde telemetri, hava aracının uçuş kontrol bilgisayarından (Autopilot / FCU) yer kontrol istasyonuna (GCS) veya kara kutu hafızasına periyodik olarak iletilen durum bilgisidir. Sistemde doğrulanan 9 zorunlu telemetri parametresi aşağıda detaylandırılmıştır:

1. **`timestamp` (Zaman Damgası - `YYYY-MM-DD HH:MM:SS`):**
   - **Anlamı:** Veri paketinin üretildiği/kaydedildiği anı gösterir (ISO-8601 standardı).
   - **Mühendislik Önemi:** Uçuş süresinin hesaplanması, sistem olaylarının kronolojik korelasyonu ve telemetri yayınında paket kaybı/kesintisi (packet drop) olup olmadığının anlaşılması için birincil referanstır.

2. **`altitude` (İrtifa - Metre $[m]$):**
   - **Anlamı:** İHA'nın deniz seviyesine (MSL) veya kalkış noktasına (AGL) göre dikey yüksekliğidir ($[-500, 50000]\ m$).
   - **Mühendislik Önemi:** Coğrafi engellerle çarpışmayı önleme, tırmanış/alçalış hızlarını (Climb/Descent Rate) hesaplama ve uçuş tavanı sınırlarını denetleme amacıyla kullanılır.

3. **`speed` (Hız - Metre/Saniye $[m/s]$):**
   - **Anlamı:** İHA'nın yer hızı (Ground Speed) veya düzeltilmiş hava hızıdır (Airspeed).
   - **Mühendislik Önemi:** Skaler büyüklük olan hız fiziksel olarak negatif olamaz ($\text{speed} \ge 0$). Negatif değerler pitot-statik tüp veya GPS hız vektörü hesaplama hatasını gösterir.

4. **`battery_pct` (Batarya Yüzdesi - $[\%]$):**
   - **Anlamı:** Bataryanın kullanılabilir şarj durumunu (State of Charge - SoC) yüzde olarak ($[0.0, 100.0]$) ifade eder.
   - **Mühendislik Önemi:** Kritik eve dönüş (Return-to-Home - RTH) kararlarının verilmesi ve acil iniş protokollerinin tetiklenmesi için en kritik parametredir. $\%0$'ın altı veya $\%100$'ün üstü fiziksel olarak geçersizdir.

5. **`latitude` (Enlem) & `longitude` (Boylam - Derece $[^\circ]$):**
   - **Anlamı:** WGS-84 elipsoidinde İHA'nın küresel coğrafi koordinatlarıdır.
   - **Sınırlar:** Enlem $[-90.0, +90.0]^\circ$, Boylam $[-180.0, +180.0]^\circ$ aralığında tanımlıdır. Bu sınırların dışındaki değerler GPS alıcısı arızası veya veri paketi bozulması (bit-flip) anlamına gelir.

6. **`pitch` (Yunuslama), `roll` (Yalpalama) ve `yaw` (Sapma / Baş Açısı - Derece $[^\circ]$):**
   - **Anlamı:** İHA'nın 3 boyutlu uzaydaki Euler yönelim açılarıdır (Attitude).
   - **Sınırlar:** `pitch` $\in [-90, 90]^\circ$, `roll` $\in [-180, 180]^\circ$, `yaw` $\in [-360, 360]^\circ$.

---

## 3. Zaman Boşluğu Eşiği (Timestamp Gap Threshold) Seçimi ve Gerekçelendirilmesi

### Belirlenen Varsayılan Eşik Değeri: **3.0 Saniye**

### Gerekçelendirme:
1. **İHA Telemetri Frekansı:** Standart İHA otopilotlarında (ArduPilot, PX4 vb.) temel durum telemetrisi (MAVLink `GLOBAL_POSITION_INT`, `ATTITUDE`, `SYS_STATUS`) yer istasyonuna genellikle **1 Hz – 10 Hz** (saniyede 1 ila 10 paket) frekansında iletilir.
2. **Kabul Edilebilir Gecikme:** Kablosuz RF linklerde veya 4G/LTE tabanlı telemetride tekil paket kayıpları veya 1–2 saniyelik tampon (buffer) gecikmeleri normal operasyonel dalgalanma kabul edilebilir.
3. **Anomali Eşiği:** Ardışık iki paket arasındaki sürenin $\Delta t > 3.0\text{ sn}$ olması, 1 Hz yayında en az 3 ardışık paketin kaçırıldığını veya veri hattında ciddi bir kesinti (GCS Link Loss Failsafe başlangıcı) meydana geldiğini gösterir.
4. **Dinamik Yapı:** Kullanıcı arayüzünde bu eşik dinamik bir giriş kutusu olarak sunulmuş olup, farklı görev profillerine göre (örneğin `1.0` sn veya `5.0` sn) anında değiştirilebilir.

---

## 4. Teknik Araştırma ve Kütüphane Seçimi Analizi

Uygulama mimarisinde 5 ana görev alanı için seçilen kütüphaneler, değerlendirilen alternatifler ve tercih nedenleri aşağıda özetlenmiştir:

| Alan | Seçilen Teknoloji | Değerlendirilen Alternatifler | Neden Tercih Edildi? | Avantajları | Dezavantajları |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Arayüz (GUI)** | **CustomTkinter** (+ Tkinter/ttk) | PyQt6, PySide6, Kivy, WxPython | Python standardı Tkinter üzerine modern koyu tema, yuvarlatılmış bileşenler ve DPI ölçekleme katmanı eklemesi. | Hızlı açılış, şık koyu tema, hafif mimari, yerleşik `ttk.Treeview` ile tam uyum. | Çok karmaşık 3B sahne animasyonları için harici kütüphane gerektirmesi. |
| **Veri Doğrulama & Analiz** | **Pandas** & **NumPy** | Standart `csv` modülü, Polars, DuckDB | Esnek CSV ayrıştırma, eksik veri (`NaN`) tespiti, `to_datetime` ile tarih çözümleme ve zaman serisi türev ($\Delta t$) hesaplama kolaylığı. | Çok yüksek performans, zengin istatistiksel fonksiyonlar (`mean`, `min`, `max`, `diff`). | Küçük boyutlu dosyalar için standart `csv` modülüne kıyasla daha yüksek bellek ayak izi. |
| **Grafik Görselleştirme** | **Matplotlib** (`FigureCanvasTkAgg`) | Plotly, PyQtGraph, Bokeh, Seaborn | Masaüstü Tkinter arayüzlerine doğrudan gömülebilmesi ve kesinti aralıklarını `axvspan` ile kırmızı şerit olarak işaretleyebilmesi. | Tkinter ile kusursuz gömülü entegrasyon, yüksek çözünürlüklü çizim. | Web tabanlı kütüphaneler kadar hazır etkileşimli araç çubuğu sunmaması. |
| **Görsel Varlık & İkon** | **Pillow (PIL)** | İkincil harici çizim programları | İHA/SİHA ikonlarının (`.ico` ve `.png`) ve açılış ekranı görsellerinin doğrudan kodla vektörel hassasiyette üretilmesi. | Çoklu çözünürlük (`16x16` - `256x256`) `.ico` desteği, `CTkImage` uyumu. | Karmaşık 3B render işlemlerine uygun olmaması. |
| **Otomatik Testler** | **Pytest** | `unittest`, `doctest` | Sade `assert` yapısı, hızlı hata raporlama ve modüler test organizasyonu. | Minimum kod tekrarı, yüksek okunabilirlik (30/30 test). | Harici paket olarak kurulması. |

---

## 5. Doğrulama, Kısmi Kurtarma (Partial Recovery) ve Popup Politikası
1. **Kritik (Fatal) Hatalar:** Dosyanın 0 bayt (boş) olması, CSV formatının tamamen bozuk olması, 9 zorunlu sütundan birinin eksik olması veya dosyada **hiç geçerli satır kalmaması** durumunda analiz durdurulur ve kullanıcıya `showerror` popup penceresi ile neden açıklanır.
2. **Satır Bazlı Hatalar ve Kısmi Kurtarma:** Negatif hız, batarya sınır ihlali ($<0$ veya $>100$), geçersiz koordinat veya boş hücre içeren satırlar elenirken, kalan geçerli satırlar kurtarılır ve analize sokulur.
3. **Sadece Hata Durumunda Popup:** Görev gereksinimine uygun olarak, dosya %100 geçerli olduğunda kullanıcıyı rahatsız eden bir popup açılmaz; yalnızca elenen hatalı satırlar varsa uyarı popup'ı gösterilir.

---

## 6. Güvenli Dağıtım ve DigiCert İmzalı Çalışma Zamanı Mimarisi (v1.4.0)
Masaüstü dağıtımında son kullanıcıların (ve değerlendiricilerin) bilgisayarlarında Avast (`IDP.HELU.PSD11`) veya Windows Defender SmartScreen yanlış alarmlarıyla karşılaşmaması için **%100 DigiCert İmzalı Taşınabilir Çalışma Zamanı** mimarisi tasarlanmıştır:
- Paket içerisindeki çalıştırılabilir motor (`pythonw.exe`, `python.exe`, `python312.dll`) doğrudan **Python Software Foundation (`DigiCert Trusted G4 Code Signing RSA4096 SHA384`)** dijital imzasına (`Status: Valid`) sahiptir.
- Paket içinde hiçbir imzasız `.exe` bulunmadığından tüm antivirüs taramalarından %100 güvenli olarak geçer ve tıklandığında **1.8 saniyelik animasyonlu İHA Açılış Ekranı (Splash Screen)** ile başlar.
