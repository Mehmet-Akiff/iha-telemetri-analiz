# 📸 Ekran Görüntüleri Çekim ve Klasör Teslim Rehberi

Can Bey'in belirttiği üzere ekran görüntüleri hem **`IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx`** Word raporunun içindeki sarı kesikli kutulara yapıştırılacak hem de bu **`screenshots/`** klasörü içerisinde teslim edilecektir.

Aşağıdaki 10 ekran görüntüsünü sırasıyla çekip hem Word dosyasındaki ilgili kutuya yapıştırabilir hem de bu klasöre aşağıdaki dosya adlarıyla kaydedebilirsiniz:

| Sıra | Word Raporundaki Yeri | Kaydedilecek Dosya Adı | Ne Yaparken Çekilmeli? |
| :--- | :--- | :--- | :--- |
| **1** | **Şekil 1.1** (Bölüm 1.C sonu) | `01_csv_senaryo_uretici_arayuzu.png` | **CSV Senaryo Üretici** uygulamasını açın, `3. Karışık / Kısmi Hatalı Veri` seçin; sağda canlı tablo ve sol altta `📌 Sıradaki: Üretilen Klasör X` görünürken ekran görüntüsü alın. |
| **2** | **Şekil 2.1** (Bölüm 2.C sonu) | `02_ham_csv_orijinal_sekmesi.png` | **Analiz İstasyonu**nda `03_karisik_hatali_ucus.csv` dosyasını seçip analiz edin, 4. sekme olan **`📄 Ham CSV Dosyası (Orijinal)`** sekmesine tıklayın (`METIN_HATASI` satırı görünürken çekin). |
| **3** | **Şekil 3.1** (Bölüm 3.C sonu) | `03_gecerli_ucus_analiz_ve_grafikler.png` | **Analiz İstasyonu**nda `01_gecerli_ucus.csv` dosyasını analiz edin; üstteki 7 KPI kartı (`60 / 60`, `Hatalı: 0`) ve 3'lü **Telemetri Grafikleri** görünürken çekin. |
| **4** | **Şekil 4.1** (Bölüm 4.C) | `04_hata_dosya_secilmeden_analiz.png` | Uygulamayı yeni açıp **hiç dosya seçmeden** doğrudan `⚙️ Analiz Et` butonuna basın; çıkan **`Dosya Seçilmedi`** uyarı popup'ı ekrandayken çekin. |
| **5** | **Şekil 4.2** (Bölüm 4.C) | `05_hata_bos_veya_bozuk_dosya.png` | `13_bos_dosya_0_bayt.csv` (veya `14_bozuk_csv_sozdizimi.csv`) seçip `⚙️ Analiz Et` deyin; çıkan **`Doğrulama / Yükleme Hatası`** popup'ı ekrandayken çekin. |
| **6** | **Şekil 4.3** (Bölüm 4.C) | `06_hata_eksik_sutunlu_dosya.png` | `11_eksik_sutunlu_csv.csv` seçip `⚙️ Analiz Et` deyin; çıkan **`Zorunlu sütun(lar) eksik: battery_pct, pitch, yaw`** popup'ı ekrandayken çekin. |
| **7** | **Şekil 4.4** (Bölüm 4.C) | `07_kismi_hatali_uyari_popup.png` | `03_karisik_hatali_ucus.csv` seçip `⚙️ Analiz Et` deyin; arkada grafikler çizilmişken ve önde **`Doğrulama Uyarısı: Hatalı Kayıtlar Bulundu`** popup'ı açıkken çekin. |
| **8** | **Şekil 4.5** (Bölüm 4.C) | `08_hatali_kayitlar_raporu_sekmesi.png` | Uyarı popup'ına Tamam dedikten sonra 3. sekme olan **`⚠️ Hatalı Kayıtlar Raporu`** sekmesini açın; elenen 24 satır ve hata nedenleri listelenirken çekin. |
| **9** | **Şekil 5.1** (Bölüm 5.C sonu) | `09_zaman_boslugu_gap_grafik_anomalisi.png` | `02_zaman_kesintili_ucus.csv` seçip `⚙️ Analiz Et` deyin; KPI kartında `Tespit Edilen Boşluk: 1 adet` ve grafiklerin ortasında **kırmızı dikey kesinti şeridi** görünürken çekin. |
| **10** | **Şekil 6.1** (Bölüm 6.C sonu) | `10_pytest_35_otomatik_test_ciktisi.png` | Terminalde `$env:PYTHONPATH="."; python -m pytest tests -v` komutunu çalıştırıp **35 passed** yeşil test çıktısının ekran görüntüsünü alın. |
