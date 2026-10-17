# İHA Telemetri Analiz ve Görselleştirme Uygulaması - Teknik Rapor

**Teslim Tarihi:** 20 Ekim 2026  
**Proje Adı:** İHA Telemetri Analiz ve Görselleştirme Uygulaması  

---

## 1. Giriş ve Görevin Kapsamı
Bu çalışma, CSV formatındaki İnsansız Hava Aracı (İHA) telemetri verilerini okuyan, yapısal ve fiziksel sınır kurallarına göre doğrulayan, kısmi veri kurtarma (partial recovery) yeteneğine sahip, uçuş dinamiklerini analiz eden ve sonuçları kullanıcı dostu modern bir masaüstü arayüzünde görselleştiren bir sistemin tasarım ve uygulamasını kapsamaktadır.

---

## 2. Telemetri Veri Alanlarının Araştırılması ve Anlamları
İHA sistemlerinde telemetri, hava aracının uçuş kontrol bilgisayarından (Autopilot / FCU) yer kontrol istasyonuna (GCS) veya kara kutu hafızasına periyodik olarak iletilen durum bilgisidir. Desteklenen telemetri parametreleri aşağıda detaylandırılmıştır:

1. **`timestamp` (Zaman Damgası):**
   - **Anlamı:** Veri paketinin üretildiği/kaydedildiği anı gösterir (ISO-8601 `YYYY-MM-DD HH:MM:SS` standardı).
   - **Önemi:** Uçuş süresinin hesaplanması, sistem olaylarının kronolojik korelasyonu ve telemetri yayınında paket kaybı/kesintisi (packet drop) olup olmadığının anlaşılması için birincil referanstır.

2. **`altitude` (İrtifa - Metre):**
   - **Anlamı:** İHA'nın deniz seviyesine (MSL) veya kalkış noktasına (AGL) göre dikey yüksekliğidir.
   - **Önemi:** Coğrafi engellerle çarpışmayı önleme, tırmanış/süzülüş oranlarını (Climb/Descent Rate) hesaplama ve uçuş tavanı sınırlarını denetleme amacıyla kullanılır.

3. **`speed` (Hız - m/s):**
   - **Anlamı:** İHA'nın yer hızı (Ground Speed) veya düzeltilmiş hava hızıdır (Airspeed).
   - **Önemi:** Skaler hız fiziksel olarak negatif olamaz ($speed \ge 0$). Stall (tutunma kaybı) hızının altına düşülmemesi ve yapısal hız sınırının (Vne) aşılmaması için izlenir.

4. **`battery_pct` (Batarya Yüzdesi - %):**
   - **Anlamı:** Bataryanın kullanılabilir şarj durumunu (State of Charge - SoC) yüzde olarak (%0 - %100) ifade eder.
   - **Önemi:** Kritik eve dönüş (Return-to-Home - RTH) kararlarının verilmesi ve acil iniş protokollerinin tetiklenmesi için en kritik parametredir. %0'ın altı veya %100'ün üstü fiziksel olarak geçersizdir.

5. **`latitude` (Enlem - Derece) & `longitude` (Boylam - Derece):**
   - **Anlamı:** WGS-84 elipsoidinde İHA'nın küresel coğrafi koordinatlarıdır.
   - **Sınırlar:** Enlem $[-90.0, +90.0]^\circ$, Boylam $[-180.0, +180.0]^\circ$ aralığında tanımlıdır. Bu sınırların dışındaki değerler GPS sensör arızası veya veri bozulması anlamına gelir.

6. **`pitch` (Yunuslama Açısı - Derece):**
   - **Anlamı:** İHA'nın enine ekseni (lateral axis) etrafındaki burun yukarı / burun aşağı hareket açısıdır.

7. **`roll` (Yalpalama Açısı - Derece):**
   - **Anlamı:** İHA'nın boyuna ekseni (longitudinal axis) etrafındaki sağa / sola yatış açısıdır.

8. **`yaw` (Sapma / Baş Açısı - Derece):**
   - **Anlamı:** İHA'nın dikey ekseni (vertical axis) etrafındaki pusula yönelimidir (Heading).

---

## 3. Zaman Boşluğu Eşiği (Timestamp Gap Threshold) Seçimi ve Gerekçelendirilmesi

### Belirlenen Eşik Değeri: **3.0 Saniye**

### Gerekçelendirme:
1. **İHA Telemetri Frekansı:** Standart İHA otopilotlarında (ArduPilot, PX4 vb.) temel durum telemetrisi (MAVLink `GLOBAL_POSITION_INT`, `ATTITUDE`, `SYS_STATUS`) yer istasyonuna genellikle **1 Hz - 10 Hz** (saniyede 1 ila 10 paket) frekansında iletilir.
2. **Kabul Edilebilir Gecikme:** Kablosuz RF linklerde veya GSM tabanlı telemetride tekil paket kayıpları veya 1-2 saniyelik buffer gecikmeleri normal operasyonel dalgalanma kabul edilebilir.
3. **Anomali Eşiği:** Ardışık iki paket arasındaki sürenin $\Delta t > 3.0$ saniye olması, en az 3 ardışık paketin kaçırıldığını veya veri hattında ciddi bir kesinti (Failsafe eşiği başlangıcı) meydana geldiğini gösterir. Bu nedenle 3.0 saniye, yanlış pozitifleri (false positive) filtreleyip gerçek kesintileri yakalayan optimal bir eşiktir.
4. **Esneklik:** Kullanıcı arayüzünde bu eşik dinamik bir giriş kutusu (Entry) olarak sunulmuş olup, istenildiğinde farklı yayın frekanslarına göre (örneğin 0.5 saniye veya 5.0 saniye) anında değiştirilebilir.

---

## 4. Teknik Araştırma ve Kütüphane Seçimi Analizi

Uygulama mimarisinde 4 ana görev alanı için seçilen kütüphaneler, değerlendirilen alternatifler ve tercih nedenleri aşağıda özetlenmiştir:

| Alan | Seçilen Kütüphane | Değerlendirilen Alternatifler | Neden Tercih Edildi? | Avantajları | Dezavantajları |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Arayüz (GUI)** | **CustomTkinter** (+ Tkinter/ttk) | PyQt6, PySide6, Kivy, WxPython | Python standardı Tkinter üzerine modern ve zarif (dark/light mode, yuvarlatılmış kartlar, high-DPI) bir tasarım katmanı eklemesi. Ekstra C++ derleyici ve ağır DLL bağımlılıkları gerektirmemesi. | Hızlı başlatma süresi, modern koyu tema desteği, platformlar arası sorunsuz çalışma, Python yerleşik Tkinter ile %100 uyum. | Saf PyQt kadar geniş QML animasyon ekosistemine sahip olmaması. |
| **Veri Analizi & Doğrulama** | **Pandas** & **NumPy** | Standart `csv` modülü, Polars, DuckDB | Vektörel veri işleme, eksik veri (NaN) tespiti, `to_datetime` ile esnek tarih parse etme kabiliyeti ve zaman serisi türev ($\Delta t$) hesaplama kolaylığı. | Çok yüksek performans, gelişmiş zaman serisi desteği, zengin istatistiksel fonksiyonlar (`mean`, `min`, `max`). | Küçük boyutlu CSV'ler için standart kütüphaneye kıyasla hafif bellek yükü. |
| **Grafik Görselleştirme** | **Matplotlib** (`FigureCanvasTkAgg`) | Plotly, PyQtGraph, Bokeh, Seaborn | Masaüstü Tkinter arayüzlerine doğrudan gömülebilmesi (Canvas entegrasyonu), statik ve etkileşimli zaman serisi grafiklerini stabil şekilde render etmesi, anomali aralıklarını dikey renklendirme (`axvspan`) ile çizme gücü. | Tkinter ile kusursuz gömülü entegrasyon, yaygın dokümantasyon, yüksek çözünürlüklü grafik çizimi. | Plotly kadar varsayılan olarak web etkileşimli (hover tooltip) olmaması, özelleştirme için kod gerektirmesi. |
| **Otomatik Testler** | **Pytest** | `unittest`, `doctest` | Parametrik test tanımlama, sade `assert` sözdizimi, detaylı hata izleme (traceback) ve fixture mekanizması sayesinde temiz ve okunabilir test kodu yazılması. | Minimum boilerplate kod, zengin eklenti desteği, mükemmel hata raporlama. | Python standart kütüphanesine harici bir paket olarak eklenmesi. |

---

## 5. Doğrulama ve Kısmi Kurtarma (Partial Recovery) Stratejisi
Gerçek telemetri kayıtlarında birkaç hatalı satır yüzünden tüm dosyanın çöpe atılması kabul edilemez. Bu nedenle sistem şu ilkeyle çalışır:
1. **Kritik Hatalar:** Dosyanın boş olması, okunamaması veya 9 zorunlu sütundan birinin eksik olması durumunda işlem durdurulur ve kullanıcıya popup ile bildirilir.
2. **Satır Hataları:** Negatif hız, batarya sınır ihlali, geçersiz koordinat veya boş hücre içeren satırlar reddedilir.
3. **Kayıt ve Rapor:** Reddedilen satırın dosyadaki satır numarası, sütun adı ve nedeni `RowError` veri yapısıyla kaydedilerek arayüzdeki "Hatalı Kayıtlar Raporu" sekmesinde kullanıcıya şeffafça sunulur.
4. **Geçerli Verilerin İşlenmesi:** Dosyada tek bir geçerli kayıt dahi kalsa, bu kayıtlar temiz bir DataFrame olarak analize ve grafiklere aktarılır.
