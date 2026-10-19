"""
generate_word_report.py
İHA Telemetri Analiz ve Görselleştirme Uygulaması - Kapsamlı Teknik Rapor Üretici.
Can YILMAZ'ın belirttiği tüm kriterleri (Word formatı, Abstract, Tablolar,
Checklist + A-B-C [Araştırma -> İlk Deneme/Eklenenler -> Karşılaşılan Sorunlar ve Çözüm Yolu] kurgusu,
Ekran Görüntüsü Yer Tutucu Kutuları ve Geçerli Akademik Kaynakça) eksiksiz içerir.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def set_cell_background(cell, fill_hex: str):
    """Tablo hücresinin arka plan rengini ayarlar."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Tablo hücresinin iç boşluklarını (padding) ayarlar (dxa cinsinden)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="D0D7DE", sz="4", val="single"):
    """Tabloya ince, modern kenarlıklar ekler."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_formatted_table(doc, headers, rows, col_widths=None, header_bg="0B1526"):
    """Profesyonel biçimlendirilmiş tablo oluşturur."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    # Başlık satırı
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(header_text)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(hdr_cells[i], header_bg)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Veri satırları
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F8F9FA" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = ""
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(cell_value))
            run.font.name = "Calibri"
            run.font.size = Pt(9.5)
            if "☑" in str(cell_value) or "GEÇTİ" in str(cell_value) or "ÇÖZÜLDÜ" in str(cell_value):
                run.font.color.rgb = RGBColor(35, 112, 50)
                if c_idx == 0 or len(str(cell_value)) < 35:
                    run.bold = True
            elif "HATALI" in str(cell_value) or "Kritik" in str(cell_value):
                run.font.color.rgb = RGBColor(180, 35, 24)
            else:
                run.font.color.rgb = RGBColor(33, 37, 41)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=90, bottom=90, left=120, right=120)
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)

    doc.add_paragraph()
    return table


def add_screenshot_placeholder(doc, fig_no: str, title: str, target_screen: str, steps: list, save_filename: str):
    """
    Kullanıcının ekran görüntüsü alıp yapıştırması için çerçeveli, detaylı yönergeli
    ve boş alanı hazır yer tutucu kutu oluşturur.
    """
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="E67700", sz="12", val="dashed")

    cell = table.rows[0].cells[0]
    set_cell_background(cell, "FFF9DB")
    set_cell_margins(cell, top=180, bottom=180, left=220, right=220)

    p_hdr = cell.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_hdr = p_hdr.add_run(f"📸 [EKRAN GÖRÜNTÜSÜ YER TUTUCU ALANI — {fig_no}]\n{title}")
    r_hdr.bold = True
    r_hdr.font.name = "Calibri"
    r_hdr.font.size = Pt(11)
    r_hdr.font.color.rgb = RGBColor(180, 83, 9)

    p_target = cell.add_paragraph()
    r_t1 = p_target.add_run("• Hangi Ekranın Görüntüsü Gelecek: ")
    r_t1.bold = True
    r_t1.font.size = Pt(10)
    r_t2 = p_target.add_run(target_screen)
    r_t2.font.size = Pt(10)

    p_steps_title = cell.add_paragraph()
    r_st = p_steps_title.add_run("• Ekran Görüntüsü Çekilirken Yapılacak İşlem Adımları:")
    r_st.bold = True
    r_st.font.size = Pt(10)

    for idx, step_text in enumerate(steps, 1):
        p_s = cell.add_paragraph()
        p_s.paragraph_format.left_indent = Inches(0.25)
        p_s.paragraph_format.space_after = Pt(2)
        r_s = p_s.add_run(f"{idx}. {step_text}")
        r_s.font.size = Pt(9.5)
        r_s.font.color.rgb = RGBColor(55, 65, 81)

    p_file = cell.add_paragraph()
    r_f1 = p_file.add_run("• Klasör Teslimi İçin Kaydedilecek Dosya Adı: ")
    r_f1.bold = True
    r_f1.font.size = Pt(9.5)
    r_f2 = p_file.add_run(f"screenshots/{save_filename}")
    r_f2.font.name = "Consolas"
    r_f2.font.size = Pt(9.5)
    r_f2.font.color.rgb = RGBColor(25, 113, 194)

    # Boş yapıştırma alanı
    p_space = cell.add_paragraph()
    p_space.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_space.paragraph_format.space_before = Pt(28)
    p_space.paragraph_format.space_after = Pt(28)
    r_sp = p_space.add_run(
        "\n[ EKRAN GÖRÜNTÜSÜNÜ ÇEKTİKTEN SONRA BU YAZIYI SİLİP GÖRSELİ BURAYA YAPIŞTIRINIZ ]\n"
    )
    r_sp.italic = True
    r_sp.font.size = Pt(10)
    r_sp.font.color.rgb = RGBColor(134, 142, 150)

    # Şekil alt yazısı (Caption)
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(4)
    p_cap.paragraph_format.space_after = Pt(14)
    r_cap = p_cap.add_run(f"{fig_no}: {title}")
    r_cap.italic = True
    r_cap.bold = True
    r_cap.font.size = Pt(9.5)
    r_cap.font.color.rgb = RGBColor(73, 80, 87)


def add_section_heading(doc, text: str, level: int = 1):
    """Bölüm başlığı ekler."""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = "Calibri"
        if level == 1:
            run.font.size = Pt(15)
            run.font.color.rgb = RGBColor(11, 21, 38)
        elif level == 2:
            run.font.size = Pt(12.5)
            run.font.color.rgb = RGBColor(25, 113, 194)
        else:
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(43, 138, 62)
    return h


def add_body_p(doc, text: str, bold_prefix: str = None):
    """Gövde paragrafı ekler."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = RGBColor(11, 21, 38)
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(33, 37, 41)
    return p


def build_report(output_path: str):
    doc = Document()

    # Sayfa kenar boşlukları (Standart 2.2 cm)
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)

    # =========================================================================
    # KAPAK BÖLÜMÜ VE BAŞLIK
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("İHA TELEMETRİ ANALİZ VE GÖRSELLEŞTİRME UYGULAMASI:\nLİTERATÜR TARAMASI, SİSTEM MİMARİSİ VE TEKNİK TASARIM RAPORU")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(17)
    r_title.font.color.rgb = RGBColor(11, 21, 38)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run(
        "Uçuş Sonrası (Post-Flight) Veri Doğrulama, Kısmi Kurtarma (Partial Recovery), Zaman Serisi Analizi\n"
        "ve Bağımsız CSV Senaryo Üretici Masaüstü İstasyonu (Sürüm v1.6.0)"
    )
    r_sub.italic = True
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(25, 113, 194)

    # Künye Tablosu
    add_formatted_table(
        doc,
        headers=["Proje Bilgisi", "Detay"],
        rows=[
            ["Hazırlayan", "Mehmet Akif ÜREY"],
            ["Değerlendirici / Yürütücü", "Can YILMAZ"],
            ["Teslim Tarihi", "20 Ekim 2026 Salı"],
            ["Yazılım Sürümü ve Teknoloji Yığını", "v1.6.0 — Python 3.12, CustomTkinter, Pandas, NumPy, Matplotlib, Pillow, Pytest"],
            ["Ana Proje ve Ek Uygulama Yapısı", "İHA Telemetri Analiz İstasyonu (Ana Dizin) & CSV Senaryo Üretici (csv_senaryo_uretici/)"],
            ["Otomatik Test Kapsamı", "35 Otomatik Test (10 Zorunlu Şartname Senaryosu + 5 Ek Senaryo + 20 Birim Testi) — %100 Başarılı"],
        ],
        col_widths=[2.3, 4.4],
        header_bg="1C2D48"
    )

    # =========================================================================
    # ÖZET / ABSTRACT
    # =========================================================================
    add_section_heading(doc, "ÖZET (ABSTRACT)", level=1)

    add_body_p(
        doc,
        "İnsansız Hava Araçları (İHA), görev icrası süresince uçuş kontrol bilgisayarı (otopilot) ile yer kontrol istasyonu (YKİ / GCS) "
        "arasında kesintisiz telemetri akışı üreten siber-fiziksel sistemlerdir [1], [3]. Ancak kablosuz radyo frekans (RF) bağlantılarında "
        "meydana gelen paket kayıpları, gecikme sıçramaları, sensör arızaları ve ayrıştırıcı kusurları, kaydedilen CSV dosyalarında "
        "eksik sütunlara, bozuk satırlara, sınır dışı fiziksel değerlere ve olağan dışı zaman boşluklarına (timestamp gaps) yol açmaktadır [2]. "
        "Bu projede, CSV formatındaki İHA telemetri verilerini okuyan, iki katmanlı deterministik doğrulama süzgecinden geçiren, "
        "kısmen hatalı dosyalarda geçerli kayıtları kurtararak (partial recovery) istatistiksel uçuş analizlerini gerçekleştiren ve "
        "sonuçları zaman serisi grafikleriyle görselleştiren modern bir masaüstü uygulaması (İHA Telemetri Analiz İstasyonu v1.6.0) "
        "geliştirilmiştir. Buna ek olarak, sistemi uçtan uca sınamak amacıyla 14 farklı uçuş ve hata senaryosunu sıralı klasörleme "
        "mimarisiyle üretebilen bağımsız bir 'İHA Telemetri CSV Senaryo Üretici' masaüstü uygulaması tasarlanmıştır. "
        "Bu raporda; gerçekleştirilen literatür araştırması, kütüphane seçim gerekçeleri, geliştirme sürecinde karşılaşılan teknik "
        "zorluklar/hatalar ve bunların çözüm yolları her görev başlığı altında A-B-C kontrol listesi (checklist) disipliniyle sunulmaktadır.",
        bold_prefix="Öz (Türkçe): "
    )

    add_body_p(
        doc,
        "Unmanned Aerial Vehicles (UAVs) are cyber-physical systems that rely on continuous telemetry streams between the flight controller "
        "and the Ground Control Station (GCS) for safety observability [1], [3]. However, wireless RF link limitations such as packet loss, "
        "latency spikes, and sensor glitches frequently introduce schema violations, out-of-bound values, and timestamp gaps into exported "
        "CSV logs [2]. In this project, a modern Python desktop application (UAV Telemetry Analysis Station v1.6.0) was developed using "
        "CustomTkinter, Pandas, NumPy, and Matplotlib to parse, validate, analyze, and visualize UAV telemetry data. The architecture "
        "implements a Two-Tier Validation Pipeline featuring fail-fast schema checking and non-blocking row-level quarantine (partial recovery), "
        "ensuring no silent failures. Additionally, a standalone 'UAV CSV Scenario Generator' desktop tool capable of synthesizing 14 distinct "
        "flight and fault scenarios was built. The system's reliability is verified through 35 automated pytest unit and integration tests "
        "(covering all 10 mandatory and 5 additional edge-case scenarios). Engineering challenges encountered during development—including "
        "antivirus false-positive mitigations via DigiCert-signed portable runtimes, raw vs. filtered data transparency, and chronological "
        "normalization—along with their resolution strategies are systematically documented.",
        bold_prefix="Abstract (English): "
    )

    # =========================================================================
    # GENEL GEREKSİNİM VE TESLİMAT KONTROL LİSTESİ (MASTER CHECKLIST)
    # =========================================================================
    add_section_heading(doc, "PROJE GENEL GEREKSİNİM KONTROL LİSTESİ (MASTER CHECKLIST)", level=1)
    add_body_p(
        doc,
        "Aşağıdaki kontrol listesi, görev şartnamesindeki 7 ana bölümün ve proje yürütücüsü Can YILMAZ tarafından belirtilen "
        "tüm teslimat kriterlerinin karşılanma durumunu özetlemektedir. Raporun devam eden bölümlerinde her bir madde; "
        "(A) Araştırma Sonuçları, (B) İlk Deneme ve Eklenen Özellikler, (C) Karşılaşılan Sorunlar ve Çözüm Yolu yapısıyla detaylandırılmıştır."
    )

    add_formatted_table(
        doc,
        headers=["Bölüm", "Şartname / Değerlendirici Gereksinimi", "Durum", "Kapsanan Modül / Kanıt"],
        rows=[
            ["Bölüm 1", "CSV telemetri okuma, doğrulama, analiz ve görselleştirme masaüstü uygulaması + Ekstra CSV Üretici uygulama", "☑ SAĞLANDI", "gui_app.py & csv_senaryo_uretici/app.py"],
            ["Bölüm 2", "9 zorunlu telemetri alanının (timestamp..yaw) fiziksel/havacılık anlamlarının araştırılması ve örnek CSV üretimi", "☑ SAĞLANDI", "Tablo 2.1, Tablo 2.2 ve 14 Senaryolu CSV Seti"],
            ["Bölüm 3", "Grafik arayüz (Dosya seçme, analiz, tablo, 3x1 grafik, hata raporu, açıklayıcı popup'lar ve Ham CSV sekmesi)", "☑ SAĞLANDI", "CustomTkinter 4 Sekmeli GUI + 7 KPI Kartı"],
            ["Bölüm 4", "9 hata sınıfının tespiti, sessizce atlamama, kısmi kurtarma (partial recovery) ve detaylı satır bazlı hata raporu", "☑ SAĞLANDI", "telemetry_validator.py (İki Katmanlı Doğrulama)"],
            ["Bölüm 5", "İrtifa (ort/min/maks), hız (ort), batarya (min) analizi ve zaman boşluğu (gap) eşiği seçimi + gerekçelendirmesi", "☑ SAĞLANDI", "telemetry_analyzer.py (3.0 sn Eşik + Kırmızı Şerit)"],
            ["Bölüm 6", "En az 10 zorunlu + 3 ek otomatik test (pytest) ve 5 arayüz hata senaryosunun ekran görüntüleriyle doğrulanması", "☑ SAĞLANDI", "tests/ (35 Otomatik Test — %100 PASSED)"],
            ["Bölüm 7", "Kütüphane araştırması (Amaç, Neden, Alternatifler, Avantaj/Dezavantaj) + Karşılaşılan Zorluklar ve Çözüm Yolları", "☑ SAĞLANDI", "Bölüm 3.A, 7.A, Tablo 7.1 ve Tüm (C) Alt Başlıkları"],
        ],
        col_widths=[0.8, 2.9, 1.1, 1.9]
    )

    # =========================================================================
    # BÖLÜM 1: GÖREVİN AMACI, TELEMETRİ MİMARİSİ VE EKSTRA CSV ÜRETİCİ
    # =========================================================================
    add_section_heading(doc, "1. Görevin Amacı, İHA Telemetri Mimarisi ve Ekstra CSV Senaryo Üretici", level=1)

    add_formatted_table(
        doc,
        headers=["Kontrol Kodu", "Bölüm 1 Gereksinim Maddesi", "Durum"],
        rows=[
            ["CHK-1.1", "Gerçek İHA'ya bağlanmadan örnek CSV verileri üzerinden çalışan çevrimdışı masaüstü analiz istasyonu", "☑ SAĞLANDI"],
            ["CHK-1.2", "MAVLink ve STANAG 4586 standartlarına uygun uçuş sonrası (post-flight) tarama ve tanılama mimarisi", "☑ SAĞLANDI"],
            ["CHK-1.3", "Ekstra: Geçerli ve hatalı test verileri üreten bağımsız CSV Senaryo Üretici uygulaması (ayrı klasörde)", "☑ SAĞLANDI"],
        ],
        col_widths=[1.1, 4.4, 1.2]
    )

    add_section_heading(doc, "1.A. Araştırma Sonuçları ve Literatür İncelemesi", level=2)
    add_body_p(
        doc,
        "Akademik ve endüstriyel literatür incelendiğinde, İHA telemetri sistemlerinin iki temel protokol standardı etrafında "
        "şekillendiği görülmektedir: açık kaynaklı otopilot ekosistemlerinde (ArduPilot, PX4) endüstri standardı olan MAVLink "
        "(Micro Air Vehicle Link) protokolü [4], [5] ve askeri/müttefik operasyonlarda birlikte çalışabilirliği tanımlayan "
        "NATO STANAG 4586 standardı [3]. Tipik bir MAVLink telemetri akışında küresel konum mesajları (GLOBAL_POSITION_INT, Mesaj #33) "
        "2–10 Hz, gövde yönelim mesajları (ATTITUDE, Mesaj #30) 10–50 Hz, batarya ve sistem durumu (SYS_STATUS, Mesaj #1) 5–10 Hz "
        "ve bağlantı canlılığını doğrulayan kalp atışı (HEARTBEAT, Mesaj #0) paketleri 1 Hz frekansında yayımlanmaktadır [5]. "
        "NATO STANAG 4586 mimarisinde ise sistem; İnsan-Bilgisayar Arayüzü (HCI), Çekirdek İHA Kontrol Sistemi (CUCS), Veri Bağı "
        "Arayüzü (DLI) ve Araca Özgü Modül (VSM) olmak üzere dört katmana ayrılmakta ve 5 Birlikte Çalışabilirlik Seviyesi (LOI 1–5) "
        "tanımlanmaktadır [3]. Bu proje kapsamında geliştirilen masaüstü yazılımı, STANAG 4586 HCI/CUCS katmanlarının çevrimdışı "
        "görev tekrarı ve uçuş sonrası tanılama (interpretable post-flight screening and diagnostic pipeline) işlevini yerine getirmektedir [1], [2]."
    )
    add_body_p(
        doc,
        "Literatürdeki deneysel çalışmalar [1], [2], yer kontrol istasyonunda kaydedilen telemetri günlüklerinin (.tlog ve bunlardan "
        "dışa aktarılan .csv dosyaları) kablosuz RF radyo kanalının kısıtlarını doğrudan yansıttığını ortaya koymaktadır. RF gölgelenmeleri, "
        "paket kayıpları (packet loss), gecikme sıçramaları (latency spikes) ve ayrıştırıcı kusurları (parser artefacts) CSV kayıtlarında "
        "bozuk satırlara ve zaman boşluklarına neden olmaktadır [2], [10]. Bu nedenle analiz yazılımının ham CSV verisini doğrudan "
        "istatistiksel hesaplamaya sokmadan önce katı bir doğrulama süzgecinden geçirmesi kritik bir uçuş emniyeti gereksinimidir."
    )

    add_section_heading(doc, "1.B. İlk Deneme, Uygulama Geliştirme ve Eklenen Özellikler", level=2)
    add_body_p(
        doc,
        "İlk aşamada yalnızca temel CSV okuma ve grafik çizimi yapan tekil bir prototip oluşturulmuştur. Ancak görev şartnamesinin "
        "2. bölümünde yer alan '(Ekstra CSV dosyası oluşturan bir uygulama yapılmak istenirse yapılabilir)' maddesi doğrultusunda, "
        "projeye ikinci bir bağımsız masaüstü uygulaması olarak 'İHA Telemetri CSV Senaryo Üretici (v1.6.0)' eklenmiştir. "
        "Can Bey'in yönlendirmesiyle bu ekstra uygulama, ana proje ile aynı depo içerisinde 'csv_senaryo_uretici/' alt klasöründe "
        "modüler olarak konumlandırılmıştır. Uygulama; %100 geçerli uçuş, zaman kesintili uçuş, karışık hatalı uçuş, negatif hız, "
        "batarya sınır ihlali, koordinat ihlali, sayısal alanda metin, boş alanlar, bozuk zaman damgası, açısal ihlaller, eksik sütun, "
        "sıfır geçerli kayıt, 0 bayt boş dosya ve bozuk CSV sözdizimi dahil olmak üzere tam 14 farklı senaryoda sentetik veri üretebilmektedir."
    )

    add_section_heading(doc, "1.C. Karşılaşılan Sorunlar, İzlenen Çözüm Yolu ve Sonuç", level=2)
    add_body_p(
        doc,
        "Geliştirme sırasında CSV Senaryo Üretici arayüzünde iki önemli kullanılabilirlik ve dosya yönetimi sorunuyla karşılaşılmıştır:",
        bold_prefix="Karşılaşılan Sorun 1.1 (Önizleme Butonu ve Klasör Numaralandırma Çakışması): "
    )
    add_body_p(
        doc,
        "İlk prototipte kullanıcı açılır menüden yeni bir senaryo seçtiğinde sağdaki tablo kendiliğinden güncellenmiyor, ayrıca 'Veriyi Önizle' "
        "butonuna basılması gerekiyordu. Daha önemlisi, toplu CSV üretimi yapıldığında dosyalar mevcut klasörün üzerine yazılıyor veya "
        "numaralı klasörlerden biri (örneğin 'Üretilen Klasör 1') kullanıcı tarafından silindiğinde klasör sayısı baz alındığı için "
        "numaralandırma sırası bozuluyordu."
    )
    add_body_p(
        doc,
        "1) Açılır kutu (ComboBox) seçim olayına doğrudan otomatik önizleme tetikleyicisi (_on_scenario_changed -> preview_data_action) "
        "bağlanarak senaryo değiştirildiği anda tablonun ve ham CSV metninin milisaniyeler içinde güncellenmesi sağlandı. "
        "2) Klasör numaralandırması için 'get_next_sequence_number()' algoritması geliştirildi. Bu algoritma hedef dizindeki mevcut klasör "
        "isimlerini Düzenli İfadeler (Regex: r'^Üretilen Klasör\\s+(\\d+)') ile tarayarak en büyük sayıyı (max_seq) bulmakta ve her zaman "
        "(max_seq + 1) numarasıyla 'Üretilen Klasör N - YYYY-MM-DD_HH-MM-SS' formatında yeni klasör açmaktadır. Örneğin Klasör 1 ve 2 varken "
        "Klasör 1 silinse bile sıradaki üretim Klasör 3'ten devam etmekte; yeni bir hedef dizine geçildiğinde ise 1'den başlamaktadır.",
        bold_prefix="İzlenen Çözüm Yolu ve Sonuç (☑ Çözüldü): "
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 1.1",
        title="İHA Telemetri Analiz İstasyonu Animasyonlu Açılış Ekranı (Splash Screen) ve CSV Senaryo Üretici Arayüzü",
        target_screen="CSV Senaryo Üretici (v1.6.0) ana penceresi ve sıralı klasörleme ('📌 Sıradaki: Üretilen Klasör X') görünümü.",
        steps=[
            "Masaüstündeki 'CSV Senaryo Uretici v1.6.0 (Imzali)' kısayoluna çift tıklayarak uygulamayı başlatın (1.8 sn'lik İHA açılış ekranını gözlemleyin).",
            "Sol paneldeki Senaryo Seçimi kutusundan '3. Karışık / Kısmi Hatalı Veri' seçeneğini seçin.",
            "Sağdaki 'Canlı Telemetri Veri Önizlemesi' tablosunda ve üstteki turuncu durum rozetinde hata bilgisinin göründüğünü doğrulayın.",
            "Sol altta '📌 Sıradaki: Üretilen Klasör X' rozeti görünürken pencerenin ekran görüntüsünü alıp bu alana yapıştırın."
        ],
        save_filename="01_csv_senaryo_uretici_arayuzu.png"
    )

    # =========================================================================
    # BÖLÜM 2: CSV VERİ FORMATI, KOORDİNAT SİSTEMLERİ VE 6-DOF UÇUŞ DİNAMİĞİ
    # =========================================================================
    add_section_heading(doc, "2. CSV Veri Formatı, Koordinat Sistemleri ve 6-DOF Uçuş Dinamiği", level=1)

    add_formatted_table(
        doc,
        headers=["Kontrol Kodu", "Bölüm 2 Gereksinim Maddesi", "Durum"],
        rows=[
            ["CHK-2.1", "9 zorunlu telemetri sütununun (timestamp, altitude, speed, battery_pct, longitude, latitude, pitch, roll, yaw) desteklenmesi", "☑ SAĞLANDI"],
            ["CHK-2.2", "Her bir telemetri verisinin ne anlama geldiğinin havacılık literatürüne göre araştırılıp açıklanması", "☑ SAĞLANDI"],
            ["CHK-2.3", "Ham CSV verisi ile doğrulama sonrası ayıklanmış geçerli verinin arayüzde şeffaf biçimde ayrıştırılması", "☑ SAĞLANDI"],
        ],
        col_widths=[1.1, 4.4, 1.2]
    )

    add_section_heading(doc, "2.A. Araştırma Sonuçları ve Literatür İncelemesi", level=2)
    add_body_p(
        doc,
        "İHA navigasyon ve telemetri sistemlerinde hava aracının uzaydaki konumunu, hızını ve yönelimini matematiksel olarak tanımlamak için "
        "üç temel referans çerçevesi eşgüdümlü olarak kullanılmaktadır [6]–[8]: "
        "(1) Küresel Jeodezik Çerçeve (WGS-84), GPS/GNSS alıcılarından elde edilen enlem (latitude, φ ∈ [-90°, +90°]), boylam "
        "(longitude, λ ∈ [-180°, +180°]) ve irtifa (altitude) parametrelerinin tanımlandığı küresel elipsoid referans sistemidir [6]. "
        "(2) Yerel Ataletsel Çerçeve (NED - North-East-Down), X ekseninin Kuzey, Y ekseninin Doğu ve Z ekseninin yerçekimi yönünde Aşağıyı "
        "gösterdiği yerel kartezyen sistemdir [7]. "
        "(3) Gövde Eksen Takımı (Body Frame), orijini İHA kütle merkezinde bulunan ve burun (ileri), sağ kanat ve gövde altını işaret eden "
        "hareketli eksen sistemidir [7], [8]."
    )
    add_body_p(
        doc,
        "Hava aracının yerel NED çerçevesine göre 3 boyutlu yönelimi (attitude) üç Euler açısı ile temsil edilir: Roll (φ, boyuna X ekseni "
        "etrafında yatış), Pitch (θ, yanal Y ekseni etrafında yunuslama) ve Yaw (ψ, dikey Z ekseni etrafında sapma/baş açısı) [7], [8]. "
        "Standart havacılık kabullerinde ataletsel çerçeveden gövde çerçevesine geçiş Z-Y-X (Yaw -> Pitch -> Roll) dönüş sırasıyla yapılır. "
        "Gövde açısal hız vektörü ile Euler açılarının türevleri arasındaki dönüşüm matrisinin determinantı det(W) = -cos(θ) olduğundan, "
        "yunuslama açısının θ = ±90° değerine ulaşması durumunda matris tekilleşmekte (Gimbal Lock / Çerçeve Kilitlenmesi) ve Roll ile Yaw "
        "eksenleri çakışmaktadır [7]. Görev kapsamında işlenen 9 telemetri parametresinin teknik spesifikasyonu Tablo 2.1'de sentezlenmiştir."
    )

    add_formatted_table(
        doc,
        headers=["CSV Sütun Adı", "Fiziksel ve Havacılık Tanımı", "İlgili MAVLink Mesajı [5]", "Birim", "Geçerli Değer Sınırı / Kural"],
        rows=[
            ["timestamp", "Telemetri paketinin oluşturulduğu veya YKİ tarafından kaydedildiği zaman damgası.", "GLOBAL_POSITION_INT / SYSTEM_TIME", "ISO-8601 (Tarih/Saat)", "Çözümlenebilir tarih; Δt > 0 (kronolojik)"],
            ["altitude", "Hava aracının referans düzlemden (AGL kalkış noktası veya MSL deniz seviyesi) dikey yüksekliği.", "GLOBAL_POSITION_INT.relative_alt / VFR_HUD.alt", "Metre (m)", "Gerçek sayı; [-500.0, 50000.0] m"],
            ["speed", "Hava aracının yer referans çerçevesindeki bileşke hız büyüklüğü (Ground Speed / Airspeed).", "VFR_HUD.groundspeed", "Metre/sn (m/s)", "speed ≥ 0.0 m/s (Negatif olamaz)"],
            ["battery_pct", "Bataryanın kalan kullanılabilir enerji kapasitesinin yüzdesel oranı (State of Charge - SoC).", "SYS_STATUS.battery_remaining", "Yüzde (%)", "0.0 ≤ battery_pct ≤ 100.0"],
            ["longitude", "Başlangıç Meridyeni'ne (Greenwich) göre doğu-batı küresel açısal konumu (λ).", "GLOBAL_POSITION_INT.lon", "Derece (°)", "-180.0° ≤ longitude ≤ +180.0°"],
            ["latitude", "Ekvator düzlemine göre kuzey-güney küresel açısal konumu (φ).", "GLOBAL_POSITION_INT.lat", "Derece (°)", "-90.0° ≤ latitude ≤ +90.0°"],
            ["pitch", "Gövde yanal (Y) ekseni etrafındaki yunuslama (burun aşağı/yukarı eğilme) açısı (θ).", "ATTITUDE.pitch", "Derece (°)", "-180.0° ≤ pitch ≤ +180.0°"],
            ["roll", "Gövde boyuna (X) ekseni etrafındaki yatış (sağa/sola yatma) açısı (φ).", "ATTITUDE.roll", "Derece (°)", "-180.0° ≤ roll ≤ +180.0°"],
            ["yaw", "Gövde dikey (Z) ekseni etrafındaki sapma / burun doğrultusu (heading) açısı (ψ).", "ATTITUDE.yaw / VFR_HUD.heading", "Derece (°)", "-360.0° ≤ yaw ≤ +360.0°"],
        ],
        col_widths=[1.0, 2.2, 1.4, 0.8, 1.3]
    )

    add_section_heading(doc, "2.B. İlk Deneme, Uygulama Geliştirme ve Eklenen Özellikler", level=2)
    add_body_p(
        doc,
        "Şartnamenin 2. maddesi uyarınca hem %100 geçerli kayıtlar içeren hem de tüm doğrulama kurallarını (negatif hız, %120 batarya, "
        "94.0° enlem, sayısal alanda 'METIN_HATASI' / 'COK_YUKSEK' metinleri, boş hücreler ve zaman kesintileri) tetikleyen örnek CSV "
        "veri setleri oluşturulmuştur. Aşağıdaki Tablo 2.2, karışık hatalı örnek veri setindeki (`03_karisik_hatali_ucus.csv`) satırların "
        "doğrulama motorumuz tarafından nasıl denetlendiğini göstermektedir."
    )

    add_formatted_table(
        doc,
        headers=["Satır", "timestamp", "altitude", "speed", "battery_pct", "latitude", "Doğrulama Motoru Teşhisi ve Karar"],
        rows=[
            ["2", "2026-10-20 14:30:01", "100.0", "15.0", "99.8", "41.015137", "☑ GEÇERLİ (Normal tırmanış kaydı; analize dahil edildi)"],
            ["4", "2026-10-20 14:30:03", "103.0", "-10.0", "99.4", "41.015237", "HATALI — Red Nedeni: Hız negatif olamaz (-10.0)"],
            ["6", "2026-10-20 14:30:05", "106.0", "15.4", "120.0", "41.015337", "HATALI — Red Nedeni: Batarya %0-%100 aralığı dışında (120.0)"],
            ["8", "2026-10-20 14:30:07", "109.0", "15.6", "98.6", "94.000000", "HATALI — Red Nedeni: Geçersiz enlem değeri (-90..+90 dışı: 94.0)"],
            ["10", "2026-10-20 14:30:09", "METIN_HATASI", "15.8", "98.2", "41.015537", "HATALI — Red Nedeni: Sayısal alanda geçersiz metin ('METIN_HATASI')"],
            ["11", "2026-10-20 14:30:10", "113.5", "15.9", "98.0", "41.015587", "☑ GEÇERLİ (Hatalı satır sonrası kısmi kurtarma ile analize devam)"],
        ],
        col_widths=[0.5, 1.3, 0.9, 0.6, 0.8, 0.8, 1.8]
    )

    add_section_heading(doc, "2.C. Karşılaşılan Sorunlar, İzlenen Çözüm Yolu ve Sonuç", level=2)
    add_body_p(
        doc,
        "1) İlk tasarımda Analiz İstasyonu'nda yalnızca 'Geçerli Veri Tablosu' ve 'Hatalı Kayıtlar Raporu' sekmeleri bulunmaktaydı. "
        "Test sırasında bir CSV dosyası yüklendiğinde, 'METIN_HATASI' gibi bozuk satırlar doğrulama motoru tarafından elendiği için "
        "tabloda görünmüyor; bu durum 'Acaba ayıklandıktan sonraki halini mi listeliyoruz? Eğer öyleyse ham CSV nerede?' karışıklığına "
        "yol açıyordu. Ayrıca CSV Senaryo Üretici ilk açıldığında varsayılan olarak '1. %100 Geçerli Uçuş' seçili geldiği için kullanıcı "
        "Ham CSV sekmesine baktığında metin hatası göremiyordu.\n"
        "2) Ham CSV okuyucu için birim testi (test_raw_view.py) yazılırken, Windows işletim sisteminin metin dosyalarında satır sonunu "
        "CRLF (\\r\\n - 2 bayt) olarak kaydetmesi, Python'un metin okumasında ise bunu LF (\\n - 1 bayt) olarak dönüştürmesi nedeniyle "
        "dosya bayt boyutu ile metin uzunluğu farklı çıkıyor ve dosyanın kesildiği (truncated=True) yönünde yanlış alarm üretiliyordu.",
        bold_prefix="Karşılaşılan Sorun 2.1 & 2.2 (Ham CSV Şeffaflığı ve Windows CRLF Bayt Farkı): "
    )
    add_body_p(
        doc,
        "1) İHA Telemetri Analiz İstasyonu'na 4. sekme olarak '📄 Ham CSV Dosyası (Orijinal)' eklendi ve 2. sekmenin adı "
        "'📋 Doğrulanmış / Geçerli Veri Tablosu' olarak değiştirildi. Böylece kullanıcı aynı ekranda hem diskteki el değmemiş "
        "orijinal CSV metnini ('METIN_HATASI' dahil), hem ayıklanmış temiz tabloyu hem de hata raporunu yan yana kıyaslayabilir hale geldi. "
        "Senaryo Üreticiye ise her senaryonun içeriğini açıkça bildiren renkli durum rozetleri eklendi.\n"
        "2) CRLF bayt uyuşmazlığı, bayt boyutu kıyaslaması yerine okuma sınırı sonrasında fazladan bir karakter okuma (extra_char = f.read(1)) "
        "kontrolü yapılarak kalıcı olarak çözüldü.",
        bold_prefix="İzlenen Çözüm Yolu ve Sonuç (☑ Çözüldü): "
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 2.1",
        title="Analiz İstasyonunda '📄 Ham CSV Dosyası (Orijinal)' ve '📋 Doğrulanmış / Geçerli Veri Tablosu' Sekmeleri",
        target_screen="İHA Telemetri Analiz İstasyonu v1.6.0 içinde 4. sekme olan '📄 Ham CSV Dosyası (Orijinal)' ekranı (METIN_HATASI satırı görünürken).",
        steps=[
            "İHA Telemetri Analiz İstasyonu v1.6.0 uygulamasını başlatın.",
            "'📂 CSV Dosyası Seç' butonuna tıklayarak '03_karisik_hatali_ucus.csv' dosyasını seçin ve '⚙️ Analiz Et' butonuna basın.",
            "Açılan uyarı popup'ında Tamam'a bastıktan sonra en sağdaki 4. sekme olan '📄 Ham CSV Dosyası (Orijinal)' sekmesine tıklayın.",
            "Metin kutusunda 10. satırdaki 'METIN_HATASI' ve üstteki yeşil dosya bilgi çubuğu görünürken ekran görüntüsü alıp buraya yapıştırın."
        ],
        save_filename="02_ham_csv_orijinal_sekmesi.png"
    )

    # =========================================================================
    # BÖLÜM 3: UYGULAMA ARAYÜZÜ (GUI) VE KÜTÜPHANE SEÇİMİ
    # =========================================================================
    add_section_heading(doc, "3. Uygulama Arayüzü (GUI) Tasarımı ve Kütüphane Seçimi", level=1)

    add_formatted_table(
        doc,
        headers=["Kontrol Kodu", "Bölüm 3 Gereksinim Maddesi", "Durum"],
        rows=[
            ["CHK-3.1", "CSV dosyası seçme, yükleme ve analiz başlatma kontrolleri", "☑ SAĞLANDI"],
            ["CHK-3.2", "Verileri tablo halinde görüntüleme (Doğrulanmış Veri Tablosu + Hatalı Kayıtlar Tablosu + Ham CSV)", "☑ SAĞLANDI"],
            ["CHK-3.3", "İrtifa, hız ve batarya seviyesinin zamana bağlı grafiklerini (3x1 alt grafik) görüntüleme", "☑ SAĞLANDI"],
            ["CHK-3.4", "Hatalı kayıt sayısını, nedenlerini ve kritik hataları açıklayıcı popup pencerelerle bildirme", "☑ SAĞLANDI"],
            ["CHK-3.5", "Arayüz kütüphanesi seçiminin alternatifleriyle teknik raporda gerekçelendirilmesi", "☑ SAĞLANDI"],
        ],
        col_widths=[1.1, 4.4, 1.2]
    )

    add_section_heading(doc, "3.A. Araştırma Sonuçları ve Arayüz Kütüphanesi Gerekçelendirmesi", level=2)
    add_body_p(
        doc,
        "Python ekosisteminde masaüstü grafik arayüz (GUI) geliştirmek için Tkinter, CustomTkinter, PyQt6/PySide6, wxPython ve Kivy "
        "kütüphaneleri değerlendirilmiştir [13]. Standart Tkinter hafif olmasına karşın Windows 11/10 üzerinde eski bir görsel "
        "ergonomiye sahiptir. PyQt6 zengin bileşenler sunmakla birlikte yüksek paket boyutu ve LGPL/ticari lisans karmaşıklığı "
        "getirmektedir. Bu projede; Python'un yerleşik Tcl/Tk motoru üzerine modern koyu tema (Dark Mode), yuvarlatılmış kenarlı "
        "kart bileşenleri, yüksek DPI ölçekleme desteği ve Matplotlib/ttk.Treeview ile doğrudan uyumluluk sağlayan 'CustomTkinter' "
        "kütüphanesi tercih edilmiştir [13]."
    )

    add_formatted_table(
        doc,
        headers=["Kütüphane", "Değerlendirme Durumu", "Temel Avantajları", "Temel Dezavantajları / Elene Nedeni"],
        rows=[
            ["CustomTkinter + ttk (SEÇİLDİ)", "☑ Ana GUI Çatısı Olarak Seçildi", "Modern koyu tema, hafif mimari, hızlı açılış, ttk.Treeview ve Matplotlib FigureCanvasTkAgg ile %100 uyum.", "Çok karmaşık 3B sahne çizimleri için harici OpenGL bileşeni gerektirir."],
            ["PyQt6 / PySide6", "Alternatif Olarak Değerlendirildi", "Kurumsal QTableView ve zengin widget seti.", "Yüksek kurulum boyutu (~80+ MB), dik öğrenme eğrisi ve C++ bağımlılıkları."],
            ["Standart Tkinter", "Alternatif Olarak Değerlendirildi", "Python ile yerleşik gelir, ek kurulum gerektirmez.", "Görsel olarak eski (Windows 95/XP tarzı) görünüm, modern kart tasarım eksikliği."],
            ["wxPython / Kivy", "Alternatif Olarak Değerlendirildi", "Platformlar arası çalışabilme.", "Bilimsel Matplotlib zaman serisi gömme işlemlerinde ek uyumluluk katmanı gerektirmesi."],
        ],
        col_widths=[1.3, 1.3, 2.1, 2.0]
    )

    add_section_heading(doc, "3.B. İlk Deneme, Uygulama Geliştirme ve Eklenen Özellikler", level=2)
    add_body_p(
        doc,
        "Arayüz mimarisi üç ana katman halinde tasarlanmıştır: (1) Üst Kontrol Çubuğu: İHA ikonu, dosya seçim butonu, seçili dosya etiketi, "
        "kullanıcı tarafından değiştirilebilir 'Zaman Boşluğu Eşiği (sn)' giriş kutusu ve 'Analiz Et' butonu. "
        "(2) Dinamik KPI Özet Kartları: Toplam/Geçerli Kayıt, Hatalı Kayıt Sayısı, Ortalama İrtifa, Min/Maks İrtifa, Ortalama Hız, "
        "Minimum Batarya ve Tespit Edilen Boşluk metriklerini sayaç animasyonuyla gösteren 7 adet bilgi kartı. "
        "(3) 4 Sekmeli Çalışma Alanı: Telemetri Grafikleri, Doğrulanmış Veri Tablosu, Hatalı Kayıtlar Raporu ve Ham CSV Dosyası. "
        "Ayrıca kullanıcı deneyimini zenginleştirmek adına özel çizim İHA/SİHA ikonları, 1.8 saniyelik garantili animasyonlu açılış "
        "paneli (Splash Screen), pencere yumuşak belirme (fade-in) efekti ve sekme geçişlerinde mavi/yeşil çerçeve parlaması (glow pulse) eklenmiştir."
    )

    add_section_heading(doc, "3.C. Karşılaşılan Sorunlar, İzlenen Çözüm Yolu ve Sonuç", level=2)
    add_body_p(
        doc,
        "İlk arayüz denemesinde, tamamen hatasız (%100 geçerli) bir uçuş dosyası analiz edildiğinde bile ekrana modal bir 'Başarılı' "
        "popup penceresi açılıyordu. Ancak ardışık dosya analizlerinde her seferinde hatasız dosya için popup kapatmak operatör "
        "iş akışını yavaşlatmaktaydı. İkinci olarak, uygulama çok hızlı açıldığında açılış ekranı (Splash Screen) saliseler içinde "
        "kaybolup okunamıyordu.",
        bold_prefix="Karşılaşılan Sorun 3.1 (Gereksiz Başarı Popup'ı ve Hızlı Kapanan Splash Ekranı): "
    )
    add_body_p(
        doc,
        "1) Popup mantığı optimize edilerek; %100 geçerli dosyalarda analiz sonuçlarının doğrudan KPI kartlarındaki yeşil vurgularla ve "
        "sayaç animasyonuyla kesintisiz gösterilmesi, modal popup pencerelerinin ise yalnızca uyarı (kısmi hatalı kayıt varlığı) veya "
        "kritik hata (dosya seçilmedi, boş/bozuk dosya, eksik sütun, sıfır geçerli kayıt) durumlarında açılması sağlandı.\n"
        "2) Açılış ekranı için 36 adımlı (36 x 48 ms ≈ 1.8 saniye) asenkron ilerleme çubuğu (progress bar) ve aşama metni döngüsü "
        "kurularak, bilgisayar ne kadar hızlı olursa olsun açılış panelinin en az 1.8 saniye akıcı biçimde gösterilmesi garantilendi.",
        bold_prefix="İzlenen Çözüm Yolu ve Sonuç (☑ Çözüldü): "
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 3.1",
        title="İHA Telemetri Analiz İstasyonu Ana Ekranı — Başarılı Uçuş Analizi, KPI Kartları ve Zaman Serisi Grafikleri",
        target_screen="01_gecerli_ucus.csv yüklendikten sonra KPI kartlarının (60 / 60 Geçerli Kayıt, 0 Hatalı Kayıt) ve 3'lü Telemetri Grafiklerinin görünümü.",
        steps=[
            "İHA Telemetri Analiz İstasyonu v1.6.0 uygulamasını açın.",
            "'📂 CSV Dosyası Seç' butonuna tıklayıp '01_gecerli_ucus.csv' dosyasını seçin ve '⚙️ Analiz Et' butonuna tıklayın.",
            "Üstteki 7 KPI kartının (Toplam/Geçerli: 60/60, Hatalı Kayıt: 0) ve '📈 Telemetri Grafikleri' sekmesindeki İrtifa, Hız ve Batarya grafiklerinin tam göründüğü ana pencerenin ekran görüntüsünü alın.",
            "Görseli bu kutuya yapıştırın ve ayrıca screenshots klasörüne kaydedin."
        ],
        save_filename="03_gecerli_ucus_analiz_ve_grafikler.png"
    )

    # =========================================================================
    # BÖLÜM 4: VERİ DOĞRULAMA, HATA YÖNETİMİ VE KISMİ KURTARMA
    # =========================================================================
    add_section_heading(doc, "4. Veri Doğrulama, Hata Yönetimi ve Kısmi Kurtarma (Partial Recovery)", level=1)

    add_formatted_table(
        doc,
        headers=["Kontrol Kodu", "Bölüm 4 Gereksinim Maddesi", "Durum"],
        rows=[
            ["CHK-4.1", "Gerekli sütunların eksik olması, boş veya bozuk CSV dosyası ve geçerli kayıt içermeyen dosyaların tespiti", "☑ SAĞLANDI"],
            ["CHK-4.2", "Zorunlu alanların boş bırakılması ve sayısal alanlarda metin/geçersiz değer bulunmasının tespiti", "☑ SAĞLANDI"],
            ["CHK-4.3", "Negatif hız, %0–100 dışı batarya, geçersiz enlem/boylam ve çözümlenemeyen zaman damgalarının tespiti", "☑ SAĞLANDI"],
            ["CHK-4.4", "Kısmi kurtarma: Hatalı satırlar raporlanırken geçerli kayıtların işlenmeye devam etmesi (sessizce atlamama)", "☑ SAĞLANDI"],
        ],
        col_widths=[1.1, 4.4, 1.2]
    )

    add_section_heading(doc, "4.A. Araştırma Sonuçları ve İki Katmanlı Doğrulama Mimarisi", level=2)
    add_body_p(
        doc,
        "Uçuş güvenliği kritik sistemlerde veri doğrulama katmanı, hem beklenmedik uygulama çökmelerini (Unhandled Exceptions) "
        "engellemeli hem de kısmen bozulmuş bir uçuş kaydındaki sağlam verileri kurtarabilmelidir (Resilient Parsing) [1], [2]. "
        "Bu doğrultuda 'telemetry_validator.py' modülünde İki Katmanlı Doğrulama Hattı (Two-Tier Validation Pipeline) tasarlanmıştır:\n"
        "• 1. Katman (Dosya ve Şema Kapısı - Fail-Fast Gate): Dosya varlığı, dosya boyutu (> 0 bayt), UTF-8 karakter kodlaması, "
        "CSV ayrıştırılabilirliği ve 9 zorunlu sütunun başlıkta eksiksiz bulunması kontrol edilir. Bu katmandaki bir hata tüm dosyayı "
        "geçersiz kıldığından işlem durdurulur ve kritik hata popup'ı gösterilir.\n"
        "• 2. Katman (Satır Bazlı Karantina Kapısı - Non-Blocking Quarantine Gate): Şema kontrolünü geçen her satır; boş hücre, "
        "tarih çözümlenebilirliği, sayısal tip uyumu ve fiziksel sınır kurallarına göre denetlenir. Kural ihlali içeren satırlar "
        "satır numarası, sütun adı, açık hata mesajı ve ham değeriyle birlikte 'RowError' listesine (karantinaya) alınırken; "
        "hatasız satırlar 'valid_df' veri çerçevesine aktarılarak analiz sürdürülür."
    )

    add_formatted_table(
        doc,
        headers=["No", "Hata Sınıfı (Şartname Bölüm 4)", "Doğrulama Katmanı", "Matematiksel / Mantıksal Kural", "Sistem Tepkisi ve Arayüz Bildirimi"],
        rows=[
            ["1", "Boş veya bozuk CSV dosyaları", "1. Katman (Dosya)", "os.path.getsize == 0 veya ParserError / EmptyDataError", "Analiz durdurulur; Kritik Hata popup penceresi açılır."],
            ["2", "Gerekli sütunların eksik olması", "1. Katman (Şema)", "S_eksik = S_zorunlu - S_dosya ≠ ∅", "Analiz durdurulur; eksik sütunların tam listesi popup ile bildirilir."],
            ["3", "Zorunlu alanların boş bırakılması", "2. Katman (Satır)", "isna(val) veya str(val).strip() == ''", "Satır elenir; boş bırakılan sütun ve satır no 'Hatalı Kayıtlar' sekmesine yazılır."],
            ["4", "Sayısal alanda metin bulunması", "2. Katman (Satır)", "float(val) -> ValueError veya isnan/isinf", "Satır elenir; girilen metin (örn. 'METIN_HATASI') ve satır no raporlanır."],
            ["5", "Negatif hız değerleri", "2. Katman (Satır)", "speed < 0.0 m/s", "Satır elenir; 'Hız negatif olamaz' açıklamasıyla raporlanır."],
            ["6", "%0–100 dışı batarya değerleri", "2. Katman (Satır)", "battery_pct < 0.0 veya battery_pct > 100.0", "Satır elenir; batarya sınır ihlali satır bazında raporlanır."],
            ["7", "Geçersiz enlem ve boylam", "2. Katman (Satır)", "lat ∉ [-90, 90] veya lon ∉ [-180, 180]", "Satır elenir; WGS-84 coğrafi sınır ihlali raporlanır."],
            ["8", "Çözümlenemeyen zaman damgası", "2. Katman (Satır)", "pd.to_datetime(ts, errors='raise') -> Hata", "Satır elenir; bozuk zaman dizgesi raporlanır."],
            ["9", "Geçerli kayıt içermeyen dosya", "2. Katman Sonu", "total_rows > 0 ve valid_rows == 0", "İstatistik/grafik iptal edilir; tüm satırların hatalı olduğu popup ile bildirilir."],
        ],
        col_widths=[0.4, 1.5, 1.1, 1.7, 2.0]
    )

    add_section_heading(doc, "4.B. İlk Deneme, Uygulama Geliştirme ve Eklenen Özellikler", level=2)
    add_body_p(
        doc,
        "Şartnamedeki 8 temel veri kuralına ek olarak, havacılık fiziği gereği İHA'nın irtifa sınırları ([-500 m, +50.000 m]) ve "
        "Euler yönelim açıları (pitch ∈ [-180°, 180°], roll ∈ [-180°, 180°], yaw ∈ [-360°, 360°]) için de sınır denetimleri "
        "eklenmiştir. Ayrıca '⚠️ Hatalı Kayıtlar Raporu' sekmesinde; Satır No, Hatalı Sütun, Red Nedeni / Açıklama ve Girilen "
        "Geçersiz Değer olmak üzere 4 sütunlu detaylı bir denetim (audit) tablosu oluşturulmuştur."
    )

    add_section_heading(doc, "4.C. Karşılaşılan Sorunlar, İzlenen Çözüm Yolu ve Arayüz Hata Senaryoları", level=2)
    add_body_p(
        doc,
        "Pandas `read_csv()` fonksiyonu varsayılan ayarlarla çağrıldığında, sayısal bir sütunda tek bir metin ('METIN_HATASI') veya "
        "boş hücre varsa tüm sütunu `object` (string) veya `NaN` içeren `float` tipine çevirmekte; ayrıca IEEE 754 `inf` / `-inf` "
        "değerleri `float()` dönüşümünden geçerek ortalama hesabını sonsuz (`inf`) olarak bozmaktaydı.",
        bold_prefix="Karşılaşılan Sorun 4.1 (Pandas Tip Zorlaması ve IEEE 754 Sonsuzluk/NaN Sızıntısı): "
    )
    add_body_p(
        doc,
        "1) `pd.read_csv(..., dtype=str, keep_default_na=False)` kullanılarak tüm hücrelerin önce ham metin olarak okunması sağlandı.\n"
        "2) Her hücre özel `_parse_float()` fonksiyonundan geçirilerek `math.isnan(val)` ve `math.isinf(val)` kontrolleri eklendi. "
        "Böylece `inf`, `-inf` ve metin ifadeleri %100 kesinlikle yakalandı ve kurtarılan geçerli satırlar temiz sayısal tipleriyle "
        "`valid_df` içerisine aktarıldı.",
        bold_prefix="İzlenen Çözüm Yolu ve Sonuç (☑ Çözüldü): "
    )

    add_body_p(
        doc,
        "Şartnamenin 6. bölümünde uygulama üzerinden doğrulanması ve ekran görüntülerinin eklenmesi istenen 5 temel arayüz hata "
        "senaryosunun doğrulama protokolü Tablo 4.2'de, ekran görüntüsü yer tutucu kutuları ise hemen altında yer almaktadır."
    )

    add_formatted_table(
        doc,
        headers=["Senaryo", "Kullanıcı Eylemi (Tetikleyici)", "Uygulama ve Arayüz Davranışı", "Gösterilen Popup Başlığı ve Mesajı"],
        rows=[
            ["Senaryo 1: Dosya Seçilmeden Analiz", "Dosya seçmeden doğrudan '⚙️ Analiz Et' butonuna tıklanması.", "Analiz başlatılmaz, uygulama çökmez, mevcut görünüm korunur.", "Dosya Seçilmedi (Uyarı): 'Lütfen analiz başlatmadan önce geçerli bir telemetri CSV dosyası seçiniz.'"],
            ["Senaryo 2: Boş veya Bozuk Dosya", "'13_bos_dosya_0_bayt.csv' veya '14_bozuk_csv_sozdizimi.csv' seçilip analiz edilmesi.", "1. Katman şema kapısı devreye girer, KPI ve grafikler sıfırlanır.", "Doğrulama / Yükleme Hatası (Kritik): 'Dosya işlenemedi! Neden: Seçilen CSV dosyası tamamen boş (0 bayt).'"],
            ["Senaryo 3: Eksik Sütunlu Dosya", "'11_eksik_sutunlu_csv.csv' dosyasının yüklenip analiz edilmesi.", "Eksik sütunlar tespit edilir, analiz durdurulur.", "Doğrulama / Yükleme Hatası (Kritik): 'Zorunlu sütun(lar) eksik: battery_pct, pitch, yaw'"],
            ["Senaryo 4: Kısmen Hatalı Dosya", "'03_karisik_hatali_ucus.csv' (36 geçerli, 24 hatalı satır) analiz edilmesi.", "36 geçerli satır grafik ve tabloya çizilir; 24 hatalı satır hata sekmesine aktarılır.", "Doğrulama Uyarısı: 'Telemetri dosyasında 24 adet hatalı satır tespit edildi ve elendi. İşlenen Geçerli: 36'"],
            ["Senaryo 5: Sıfır Geçerli Kayıt", "'12_sifir_gecerli_kayit.csv' (tüm satırları hatalı) analiz edilmesi.", "Tüm satırlar hata sekmesine yazılır, grafik çizimi engellenir.", "Doğrulama / Yükleme Hatası: 'Dosyada incelenen 60 satırın tamamı hatalıdır. Analiz için geçerli kayıt içermemektedir.'"],
        ],
        col_widths=[1.2, 1.6, 1.8, 2.1]
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 4.1",
        title="Arayüz Hata Senaryosu 1 — Hiç Dosya Seçilmeden Analiz Başlatılması (Uyarı Popup'ı)",
        target_screen="Uygulama ilk açıldığında dosya seçmeden '⚙️ Analiz Et' butonuna basıldığında çıkan 'Dosya Seçilmedi' uyarı penceresi.",
        steps=[
            "İHA Telemetri Analiz İstasyonu v1.6.0 uygulamasını yeni açın (henüz hiçbir CSV dosyası seçmeyin).",
            "Doğrudan sağ üstteki yeşil '⚙️ Analiz Et' butonuna tıklayın.",
            "Ekrana gelen 'Dosya Seçilmedi — Lütfen analiz başlatmadan önce geçerli bir telemetri CSV dosyası seçiniz.' popup penceresi ana ekranın üzerindeyken ekran görüntüsü alın."
        ],
        save_filename="04_hata_dosya_secilmeden_analiz.png"
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 4.2",
        title="Arayüz Hata Senaryosu 2 — Boş (0 Bayt) veya Bozuk CSV Dosyası Seçilmesi (Kritik Hata Popup'ı)",
        target_screen="Boş veya bozuk CSV dosyası analiz edildiğinde açılan 'Doğrulama / Yükleme Hatası' popup penceresi.",
        steps=[
            "'📂 CSV Dosyası Seç' butonuna tıklayın ve Test_CSV_Verileri içindeki '13_bos_dosya_0_bayt.csv' (veya '14_bozuk_csv_sozdizimi.csv') dosyasını seçin.",
            "'⚙️ Analiz Et' butonuna tıklayın.",
            "Ekrana gelen kırmızı çarpı ikonlu 'Doğrulama / Yükleme Hatası — Dosya işlenemedi!' popup penceresi görünürken ekran görüntüsü alın."
        ],
        save_filename="05_hata_bos_veya_bozuk_dosya.png"
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 4.3",
        title="Arayüz Hata Senaryosu 3 — Gerekli Sütunları İçermeyen CSV Dosyası Yüklenmesi (Eksik Sütun Popup'ı)",
        target_screen="Zorunlu sütunları eksik olan CSV dosyası yüklendiğinde eksik sütun isimlerini listeleyen hata popup'ı.",
        steps=[
            "'📂 CSV Dosyası Seç' butonuna tıklayın ve '11_eksik_sutunlu_csv.csv' (veya samples/04_missing_column.csv) dosyasını seçin.",
            "'⚙️ Analiz Et' butonuna tıklayın.",
            "Ekrana gelen 'Zorunlu sütun(lar) eksik: battery_pct, pitch, yaw' mesajını gösteren hata popup'ı görünürken ekran görüntüsü alın."
        ],
        save_filename="06_hata_eksik_sutunlu_dosya.png"
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 4.4",
        title="Arayüz Hata Senaryosu 4A — Kısmen Hatalı Kayıtlar İçeren Dosyanın Yüklenmesi (Kısmi Kurtarma Uyarı Popup'ı)",
        target_screen="03_karisik_hatali_ucus.csv analiz edildiğinde hem arka planda çizilen grafikler hem de önde açılan 'Doğrulama Uyarısı: Hatalı Kayıtlar Bulundu' popup'ı.",
        steps=[
            "'📂 CSV Dosyası Seç' butonuna tıklayıp '03_karisik_hatali_ucus.csv' dosyasını seçin ve '⚙️ Analiz Et' butonuna basın.",
            "Henüz popup'ı kapatmadan; arkada geçerli 36 kaydın grafiği ve KPI kartları (60 / 36, Hatalı Kayıt: 24) görünürken ve önde 'Doğrulama Uyarısı: Hatalı Kayıtlar Bulundu' popup'ı açıkken ekran görüntüsü alın."
        ],
        save_filename="07_kismi_hatali_uyari_popup.png"
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 4.5",
        title="Arayüz Hata Senaryosu 4B — '⚠️ Hatalı Kayıtlar Raporu' Sekmesinde Elenen Satırların ve Nedenlerinin Gösterimi",
        target_screen="03_karisik_hatali_ucus.csv analizinde 3. sekme olan '⚠️ Hatalı Kayıtlar Raporu' tablosu (Negatif hız, batarya > 100, geçersiz enlem ve METIN_HATASI satırları).",
        steps=[
            "Bir önceki adımda açılan uyarı popup'ında 'Tamam' butonuna basın.",
            "3. sekme olan '⚠️ Hatalı Kayıtlar Raporu' sekmesine tıklayın.",
            "Tabloda Satır No (4, 6, 8, 10...), Hatalı Sütun (speed, battery_pct, latitude, altitude), Red Nedeni ve Girilen Geçersiz Değer (-10.0, 120.0, 94.0, METIN_HATASI) listelenirken ekran görüntüsü alın."
        ],
        save_filename="08_hatali_kayitlar_raporu_sekmesi.png"
    )

    # =========================================================================
    # BÖLÜM 5: TELEMETRİ ANALİZİ VE ZAMAN BOŞLUĞU EŞİĞİ (GAP THRESHOLD)
    # =========================================================================
    add_section_heading(doc, "5. Telemetri Analizi ve Zaman Boşluğu Eşiği (Timestamp Gap) Gerekçelendirmesi", level=1)

    add_formatted_table(
        doc,
        headers=["Kontrol Kodu", "Bölüm 5 Gereksinim Maddesi", "Durum"],
        rows=[
            ["CHK-5.1", "Geçerli kayıtlar üzerinden Ortalama, Minimum ve Maksimum İrtifa hesabı", "☑ SAĞLANDI"],
            ["CHK-5.2", "Ortalama Hız ve Minimum Batarya Seviyesi hesabı", "☑ SAĞLANDI"],
            ["CHK-5.3", "Zaman damgaları arasındaki olağan dışı boşlukların (gaps) tespiti ve eşik seçiminin gerekçelendirilmesi", "☑ SAĞLANDI"],
            ["CHK-5.4", "Analiz sonuçlarının arayüzde KPI kartlarıyla ve zaman serisi grafikleriyle desteklenmesi", "☑ SAĞLANDI"],
        ],
        col_widths=[1.1, 4.4, 1.2]
    )

    add_section_heading(doc, "5.A. Araştırma Sonuçları ve Zaman Boşluğu Eşiği (3.0 Saniye) Gerekçelendirmesi", level=2)
    add_body_p(
        doc,
        "Doğrulama katmanından geçen geçerli kayıtlar kümesi üzerinde uçuş zarfını özetleyen temel metrikler vektörel olarak hesaplanmaktadır: "
        "Ortalama irtifa, minimum/maksimum irtifa, ortalama yer hızı ve enerji emniyet marjını gösteren minimum batarya yüzdesi [9]. "
        "ArduPilot ve PX4 uçuş kontrol sistemlerinde kritik batarya hata koruması (FS_BATT_ENABLE) genellikle %15–%20 eşiğinde "
        "otomatik Eve Dönüş (RTL) tetiklediğinden, arayüzümüzde minimum batarya %20'nin altına düştüğünde KPI kartı otomatik olarak "
        "kırmızı uyarı rengine dönüşmektedir [9]."
    )
    add_body_p(
        doc,
        "Şartnamenin 5. bölümünde özellikle istenen 'Timestamp tespiti için eşik belirleme ve gerekçelendirme' kapsamında varsayılan "
        "eşik değeri τ_gap = 3.0 saniye olarak belirlenmiştir. Bu seçimin mühendislik ve literatür gerekçeleri şunlardır:\n"
        "1) Nominal Telemetri Frekansı: MAVLink protokolünde HEARTBEAT mesajları 1 Hz (Δt = 1.0 sn), konum ve durum mesajları ise "
        "1–10 Hz (Δt ∈ [0.1, 1.0] sn) aralığında kaydedilmektedir [3], [5].\n"
        "2) Kablosuz Kanal Jitter Toleransı: 433/915 MHz SiK radyo veya 4G/LTE bağlantılarında tekil bir paketin düşmesi veya "
        "tampon (buffer) gecikmesi Δt = 1.5–2.0 saniyelik anlık dalgalanmalar yaratabilmektedir; bu durum normal operasyonel tolerans içindedir [2].\n"
        "3) Otopilot Failsafe Standardı (FS_GCS_TIMEOUT): ArduPilot ve PX4 otopilotlarında yer istasyonu bağlantı kopukluğu hata koruması "
        "(FS_GCS_TIMEOUT) 3 ila 5 saniye bandında tanımlanmaktadır [9]. Ardışık iki paket arasındaki farkın Δt > 3.0 saniyeyi aşması, "
        "1 Hz yayında en az 3 ardışık paketin kaybolduğunu ve ciddi bir haberleşme kesintisi (Link Loss) başladığını kanıtlamaktadır [4], [9].\n"
        "4) Kullanıcı Yapılandırılabilirliği: Farklı örnekleme periyotlarına uyum sağlamak adına üst kontrol çubuğuna dinamik bir "
        "'Zaman Boşluğu Eşiği (sn)' giriş alanı eklenmiştir."
    )

    add_section_heading(doc, "5.B. İlk Deneme, Uygulama Geliştirme ve Eklenen Özellikler", level=2)
    add_body_p(
        doc,
        "`telemetry_analyzer.py` içerisindeki `TelemetryAnalyzer.analyze()` metodu, ardışık zaman farklarını `df['timestamp'].diff().dt.total_seconds()` "
        "ile hesaplamakta ve eşiği aşan her boşluğu başlangıç zamanı (`start_time`), bitiş zamanı (`end_time`) ve kesinti süresi (`gap_seconds`) "
        "bilgileriyle `TimestampGap` nesnesi olarak kaydetmektedir. Tespit edilen bu boşluklar; Matplotlib üzerindeki İrtifa, Hız ve Batarya "
        "grafiklerinin tamamında `ax.axvspan(gap.start_time, gap.end_time, color='#ff6b6b', alpha=0.35)` komutuyla yarı saydam kırmızı "
        "anomali bölgesi olarak görselleştirilmektedir."
    )

    add_section_heading(doc, "5.C. Karşılaşılan Sorunlar, İzlenen Çözüm Yolu ve Sonuç", level=2)
    add_body_p(
        doc,
        "UDP tabanlı telemetri akışlarında veya birleştirilmiş log dosyalarında paketlerin zaman damgaları bazen kronolojik sırasız "
        "(out-of-order, örn. 10:00:10 satırının 10:00:05 satırından önce gelmesi) olabilmektedir. İlk denemede sırasız veri doğrudan "
        "analize sokulduğunda Δt negatif çıkıyor ve Matplotlib grafik çizgileri zaman ekseninde geriye doğru zikzak çiziyordu.",
        bold_prefix="Karşılaşılan Sorun 5.1 (Kronolojik Sırasız Zaman Damgalarında Negatif Δt ve Grafik Bozulması): "
    )
    add_body_p(
        doc,
        "Hem `TelemetryAnalyzer.analyze()` hem de `TelemetryApp._plot_telemetry()` metodlarının ilk adımına "
        "`df_sorted = df.sort_values(by='timestamp').reset_index(drop=True)` normalizasyonu eklendi. Ayrıca bu davranış "
        "`test_scenario_15_unsorted_timestamps_handling` otomatik testi ile güvence altına alındı.",
        bold_prefix="İzlenen Çözüm Yolu ve Sonuç (☑ Çözüldü): "
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 5.1",
        title="Zaman Boşluğu (Timestamp Gap) İçeren Uçuş Analizi ve Grafiklerde Kırmızı Anomali Bölgesi",
        target_screen="02_zaman_kesintili_ucus.csv analiz edildiğinde KPI kartında 'Tespit Edilen Boşluk: 1 adet' uyarısı ve grafiklerdeki kırmızı kesinti şeridi.",
        steps=[
            "'📂 CSV Dosyası Seç' butonuna tıklayıp '02_zaman_kesintili_ucus.csv' dosyasını seçin ve '⚙️ Analiz Et' butonuna tıklayın.",
            "Sağ üstteki KPI kartında 'Tespit Edilen Boşluk: 1 adet' (sarı renkli) ifadesini ve İrtifa, Hız, Batarya grafiklerinin ortasında beliren kırmızı dikey anomali şeridini gözlemleyin.",
            "Grafikler sekmesi açıkken tam pencere ekran görüntüsü alıp buraya yapıştırın."
        ],
        save_filename="09_zaman_boslugu_gap_grafik_anomalisi.png"
    )

    # =========================================================================
    # BÖLÜM 6: OTOMATİK TESTLER (PYTEST) VE KALİTE GÜVENCESİ
    # =========================================================================
    add_section_heading(doc, "6. Otomatik Testler (Pytest) ve Arayüz Hata Senaryoları Doğrulaması", level=1)

    add_formatted_table(
        doc,
        headers=["Kontrol Kodu", "Bölüm 6 Gereksinim Maddesi", "Durum"],
        rows=[
            ["CHK-6.1", "Şartnamede listelenen 10 zorunlu test senaryosunun tamamının pytest ile kodlanması", "☑ SAĞLANDI (10/10)"],
            ["CHK-6.2", "Uygulama davranışına göre en az 3 ek test senaryosunun belirlenip uygulanması", "☑ SAĞLANDI (5 Ek + 20 Birim = 25 Ek Test)"],
            ["CHK-6.3", "Otomatik testlerin nasıl çalıştırılacağının README.md dosyasında açıklanması", "☑ SAĞLANDI"],
        ],
        col_widths=[1.1, 4.4, 1.2]
    )

    add_section_heading(doc, "6.A. Araştırma Sonuçları ve Test Çatısı Seçimi", level=2)
    add_body_p(
        doc,
        "Kalite güvencesi katmanında Python standart `unittest` modülü ile `pytest` çatısı karşılaştırılmıştır [14]. `unittest` "
        "sınıf tabanlı şablon kod (`class Test...(unittest.TestCase)`) ve `self.assertEqual()` gibi uzun sözdizimleri gerektirirken; "
        "`pytest` yalın `assert` ifadeleri, detaylı değişken içgörü (assertion introspection) raporları ve geçici dosya üretimi sağlayan "
        "`tmp_path` fixture mimarisi sunmaktadır [14]. Bu avantajları nedeniyle projede `pytest` tercih edilmiştir."
    )

    add_section_heading(doc, "6.B. Uygulanan Otomatik Test Senaryoları (10 Zorunlu + 5 Ek + 20 Motor Testi = 35 Test)", level=2)
    add_body_p(
        doc,
        "Şartnamenin 6. bölümünde istenen 10 zorunlu senaryo ve belirlediğimiz 5 ek telemetri senaryosu `tests/test_telemetry.py` "
        "içerisinde birebir numaralandırılarak kodlanmıştır. Ayrıca `test_validator.py`, `test_analyzer.py`, `test_scenario_generator.py`, "
        "`test_data_generator.py` ve `test_raw_view.py` dosyalarıyla birlikte toplam 35 otomatik test bulunmaktadır (Tablo 6.1)."
    )

    add_formatted_table(
        doc,
        headers=["Test Kodu", "Şartname / Ek Senaryo Tanımı", "Test Fonksiyonu Adı (tests/test_telemetry.py)", "Test Sonucu"],
        rows=[
            ["Zorunlu 1", "Geçerli bir CSV dosyasının doğru şekilde yüklenmesi", "test_scenario_01_valid_csv_loading", "☑ PASSED"],
            ["Zorunlu 2", "Gerekli bir sütunun eksik olması (örn. yaw sütunu eksik)", "test_scenario_02_missing_required_column", "☑ PASSED"],
            ["Zorunlu 3", "Zorunlu bir alanın boş olması (örn. speed alanı boş)", "test_scenario_03_empty_mandatory_field", "☑ PASSED"],
            ["Zorunlu 4", "Sayısal bir alanda geçersiz metin bulunması (altitude='YUKSEK')", "test_scenario_04_invalid_text_in_numeric_field", "☑ PASSED"],
            ["Zorunlu 5", "Batarya değerinin alt (<0) ve üst (>100) sınırlarının kontrolü", "test_scenario_05_battery_pct_boundary_limits", "☑ PASSED"],
            ["Zorunlu 6", "Enlem [-90, 90] ve boylam [-180, 180] sınırlarının kontrolü", "test_scenario_06_lat_lon_boundary_limits", "☑ PASSED"],
            ["Zorunlu 7", "Boş (0 bayt) veya bozuk CSV dosyasının işlenmesi", "test_scenario_07_empty_or_corrupt_csv", "☑ PASSED"],
            ["Zorunlu 8", "Hiç geçerli kayıt bulunmayan bir dosyanın işlenmesi", "test_scenario_08_no_valid_records", "☑ PASSED"],
            ["Zorunlu 9", "Analiz sonuçlarının beklenen matematiksel değerlerle karşılaştırılması", "test_scenario_09_analysis_metric_accuracy", "☑ PASSED"],
            ["Zorunlu 10", "Zaman damgaları arasındaki olağan dışı boşlukların doğru tespiti", "test_scenario_10_timestamp_gap_detection", "☑ PASSED"],
            ["Ek Senaryo 1", "Kısmi kurtarma (Hatalı satırlar elenirken geçerlilerin işlenmesi)", "test_scenario_11_mixed_partial_recovery", "☑ PASSED"],
            ["Ek Senaryo 2", "Negatif hız değerlerinin (speed < 0) yakalanması ve raporlanması", "test_scenario_12_negative_speed_detection", "☑ PASSED"],
            ["Ek Senaryo 3", "Çözümlenemeyen / bozuk zaman damgalarının reddedilmesi", "test_scenario_13_unparseable_timestamp", "☑ PASSED"],
            ["Ek Senaryo 4", "Açısal (Pitch, Roll, Yaw) fiziksel sınır ihlallerinin kontrolü", "test_scenario_14_angular_limits", "☑ PASSED"],
            ["Ek Senaryo 5", "Kronolojik sırasız gelen zaman damgalarının sıralanıp analiz edilmesi", "test_scenario_15_unsorted_timestamps_handling", "☑ PASSED"],
            ["Motor Testleri", "Senaryo üretici, ardışık klasörleme (silme korumalı) ve Ham CSV testleri", "20 Ek Birim Testi (test_scenario_generator.py vb.)", "☑ 20/20 PASSED"],
        ],
        col_widths=[1.0, 2.3, 2.2, 1.2]
    )

    add_section_heading(doc, "6.C. Karşılaşılan Sorunlar, İzlenen Çözüm Yolu ve Sonuç", level=2)
    add_body_p(
        doc,
        "Taşınabilir masaüstü paketi (`dist_signed/`) oluşturulduktan sonra proje kök dizininde `pytest` komutu parametresiz "
        "çalıştırıldığında, pytest taşınabilir çalışma zamanı içindeki `site-packages/numpy` ve `pandas` klasörlerinin iç testlerini "
        "de toplamaya çalışmış ve `ModuleNotFoundError: No module named 'hypothesis'` hatası vermiştir.",
        bold_prefix="Karşılaşılan Sorun 6.1 (Pytest Koleksiyon Aşamasında Taşınabilir Runtime Çakışması): "
    )
    add_body_p(
        doc,
        "Test komutu `python -m pytest tests -v` şeklinde doğrudan `tests/` klasörünü hedefleyecek biçimde yapılandırıldı. "
        "Böylece 35 testin tamamı 0.66 saniye içinde %100 başarıyla (`35 passed in 0.66s`) çalışmaktadır.",
        bold_prefix="İzlenen Çözüm Yolu ve Sonuç (☑ Çözüldü): "
    )

    add_screenshot_placeholder(
        doc,
        fig_no="Şekil 6.1",
        title="Terminalde Pytest Otomatik Test Sürecinin Çalıştırılması (35 Passed Çıktısı)",
        target_screen="VS Code veya PowerShell terminalinde 'python -m pytest tests -v' komutunun çalıştırılması ve 35 testin yeşil PASSED çıktısı.",
        steps=[
            "Proje klasöründe PowerShell veya VS Code terminalini açın.",
            "Terminale şu komutu yazıp Enter'a basın:  $env:PYTHONPATH='.'; python -m pytest tests -v",
            "Ekranda 'tests/test_telemetry.py::test_scenario_01...' den başlayarak '35 passed' satırına kadar yeşil PASSED sonuçları görünürken ekran görüntüsü alın."
        ],
        save_filename="10_pytest_35_otomatik_test_ciktisi.png"
    )

    # =========================================================================
    # BÖLÜM 7: TEKNİK ARAŞTIRMA, KÜTÜPHANE MATRİSİ VE ANTİVİRÜS / İMZA ÇÖZÜMÜ
    # =========================================================================
    add_section_heading(doc, "7. Teknik Araştırma, Kütüphane Seçimi ve Masaüstü Dağıtım Mimarisi", level=1)

    add_formatted_table(
        doc,
        headers=["Kontrol Kodu", "Bölüm 7 Gereksinim Maddesi", "Durum"],
        rows=[
            ["CHK-7.1", "Veri işleme, grafik, arayüz ve test kütüphanelerinin hangi amaçla kullanıldığı ve neden tercih edildiği", "☑ SAĞLANDI"],
            ["CHK-7.2", "Her kütüphane için değerlendirilen alternatifler ile avantaj ve dezavantajların belirtilmesi", "☑ SAĞLANDI"],
            ["CHK-7.3", "Masaüstü çalıştırılabilir sürümde karşılaşılan antivirüs / SmartScreen sorununun çözümü", "☑ SAĞLANDI"],
        ],
        col_widths=[1.1, 4.4, 1.2]
    )

    add_section_heading(doc, "7.A. Araştırma Sonuçları ve Kütüphane Karşılaştırma Matrisi", level=2)
    add_body_p(
        doc,
        "Projenin dört temel mühendislik katmanı (Veri İşleme, Görselleştirme, Arayüz ve Otomatik Test) için seçilen kütüphaneler, "
        "kullanım amaçları, tercih nedenleri, değerlendirilen alternatifler ve avantaj/dezavantaj analizleri Tablo 7.1'de eksiksiz "
        "olarak sunulmuştur [11]–[14]."
    )

    add_formatted_table(
        doc,
        headers=["Katman / Araç", "Kullanım Amacı", "Neden Tercih Edildi?", "Değerlendirilen Alternatifler", "Avantajları", "Dezavantajları"],
        rows=[
            [
                "Pandas & NumPy [11]",
                "CSV ayrıştırma, şema kontrolü, zaman damgası dönüşümü, Δt hesabı ve uçuş istatistikleri.",
                "Vektörel veri çerçevesi (DataFrame) yapısı, esnek CSV okuma ve hızlı istatistiksel agregasyon (`mean`, `min`, `max`, `diff`).",
                "Python standart `csv` modülü, Polars, DuckDB, Pymavlink.",
                "Yüksek hesaplama hızı, `to_datetime` ile güçlü tarih çözümleme, Matplotlib ile doğrudan uyum.",
                "Bellek içi (in-memory) çalıştığından çok küçük dosyalarda standart `csv` modülüne göre daha fazla RAM kullanır."
            ],
            [
                "Matplotlib (`TkAgg`) [12]",
                "İrtifa, hız ve batarya seviyesinin zamana bağlı 3x1 alt grafiklerinin ve gap bölgelerinin çizimi.",
                "`FigureCanvasTkAgg` ile masaüstü arayüze doğrudan gömülebilmesi ve `axvspan` ile anomali şeridi çizebilmesi.",
                "Plotly / Dash, PyQtGraph, Seaborn, Bokeh.",
                "Masaüstü Tkinter/CTk ile kusursuz entegrasyon, ortak zaman ekseni (`sharex`), yüksek yayın kalitesi.",
                "Web tabanlı Plotly kadar hazır hover (üzerine gelince kutucuk) animasyonu sunmaması."
            ],
            [
                "CustomTkinter & ttk [13]",
                "Modern masaüstü grafik arayüzü, KPI kartları, sekmeli görünüm, tablolar ve popup pencereleri.",
                "Standart Tkinter kararlılığını modern koyu tema, yuvarlatılmış bileşenler ve DPI ölçekleme ile birleştirmesi.",
                "PyQt6, PySide6, Standart Tkinter, wxPython, Kivy.",
                "Hızlı açılış, düşük kaynak tüketimi, modern havacılık yer istasyonu estetiği, yerleşik modal popup desteği.",
                "Çok karmaşık özel tablo hücre boyamaları için `ttk.Style` yapılandırması gerektirmesi."
            ],
            [
                "Pytest [14]",
                "10 zorunlu + 5 ek telemetri senaryosu ve 20 birim testinin otomatik koşturulması.",
                "Sade `assert` sözdizimi, `tmp_path` ile izole dosya testi ve zengin hata çıktı raporlaması.",
                "`unittest` (standart), `doctest`, `nose2`.",
                "Minimum şablon kod (boilerplate), çok hızlı koşum (35 test / 0.66 sn), yüksek okunabilirlik.",
                "Standart kütüphane dışında olup `pip install pytest` gerektirmesi."
            ],
            [
                "Pillow (PIL)",
                "İHA arayüz ikonlarının (`.ico`, `.png`) ve açılış ekranı görsellerinin işlenmesi.",
                "`CTkImage` nesneleri için yüksek kaliteli yeniden boyutlandırma (`LANCZOS`) sunması.",
                "OpenCV (`cv2`), harici statik resim araçları.",
                "Hafif, hızlı ve çoklu çözünürlükte Windows `.ico` üretim desteği.",
                "Yalnızca 2 boyutlu görüntü işlemeye yönelik olması."
            ],
        ],
        col_widths=[1.0, 1.1, 1.2, 1.0, 1.2, 1.2]
    )

    add_section_heading(doc, "7.B & 7.C. Geliştirme Sürecindeki En Kritik Zorluk: Antivirüs Yanlış Pozitif (False Positive) Sorunu ve Çözüm Yolu", level=2)
    add_body_p(
        doc,
        "Projenin başka bilgisayarlarda Python kurulumu gerektirmeden doğrudan çalışabilmesi için masaüstü paketleme yapıldığında "
        "çok önemli bir güvenlik/dağıtım engeliyle karşılaşılmıştır:",
        bold_prefix="Karşılaşılan Sorun 7.1 (PyInstaller .exe Dosyasının Windows Defender ve Avast Tarafından Engellenmesi): "
    )
    add_body_p(
        doc,
        "1. Deneme: Uygulama ilk olarak `PyInstaller --onefile` ile tekil `.exe` haline getirildi ve `Inno Setup` ile kurulum sihirbazına "
        "dönüştürüldü. Ancak PyInstaller'ın derlediği C-tabanlı önyükleyici (bootloader), ticari bir EV Kod İmzalama Sertifikası (yıllık "
        "maliyeti 300–500 USD olan DigiCert/Sectigo sertifikası) ile imzalanmadığı için Windows Defender (`Program:Win32/Wacapew.C!ml`) "
        "ve Avast (`IDP.HELU.PSD11`) sezgisel tarayıcıları tarafından 'Bilinmeyen/Şüpheli Yayıncı' olarak karantinaya alındı.\n"
        "2. Deneme: PowerShell `New-SelfSignedCertificate` ve `Set-AuthenticodeSignature` ile yerel bir dijital imza oluşturuldu. "
        "Bu yöntem geliştirici bilgisayarında sorunu çözse de, dosya başka bir bilgisayara gönderildiğinde kök sertifika o bilgisayarın "
        "'Güvenilen Kök Sertifika Yetkilileri' deposunda bulunmadığı için tekrar uyarı verdi."
    )
    add_body_p(
        doc,
        "Sorunun kök nedenini (imzasız PyInstaller bootloader'ı) tamamen ortadan kaldırmak için 'DigiCert İmzalı Taşınabilir Çalışma Zamanı "
        "(Signed Portable Runtime)' mimarisi geliştirildi:\n"
        "• Uygulama paketi içerisinde herhangi bir imzasız `.exe` derlemek yerine, doğrudan Python Software Foundation tarafından resmi "
        "`DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1` sertifikasıyla imzalanmış resmi gömülü çalışma zamanı (`pythonw.exe`, "
        "`python312.dll`) kullanıldı.\n"
        "• Windows'un kendi resmi imzalı sistem bileşeni (`wscript.exe`) üzerinden çalışan hafif bir başlatıcı (`Baslat.vbs` / `.lnk`) "
        "ile doğrudan imzalı `pythonw.exe` tetiklendi.\n"
        "• Böylece paket içerisindeki tüm çalıştırılabilir ikili dosyalar (%100 Valid DigiCert & Microsoft imzalı) olduğu için, "
        "başka bir bilgisayara indirildiğinde Windows Defender, SmartScreen veya Avast tarafından hiçbir uyarı verilmeden tek tıkla "
        "güvenle açılması sağlandı.",
        bold_prefix="İzlenen Çözüm Yolu ve Sonuç (☑ Kalıcı Olarak Çözüldü): "
    )

    # =========================================================================
    # BÖLÜM 8: SONUÇ VE DEĞERLENDİRME
    # =========================================================================
    add_section_heading(doc, "8. Sonuç ve Mühendislik Değerlendirmesi", level=1)
    add_body_p(
        doc,
        "Bu proje kapsamında; İHA uçuş sonrası telemetri verilerinin güvenilir biçimde doğrulanması, kısmen bozuk dosyalardan "
        "sağlam verilerin kurtarılması (partial recovery), olağan dışı zaman boşluklarının (timestamp gaps) otopilot standartlarına "
        "göre yakalanması ve kullanıcı dostu bir arayüzde görselleştirilmesi hedeflenmiş ve tüm gereksinimler eksiksiz karşılanmıştır. "
        "Ana uygulama olan 'İHA Telemetri Analiz İstasyonu v1.6.0' ve ekstra olarak geliştirilen 'İHA Telemetri CSV Senaryo Üretici v1.6.0', "
        "35 otomatik pytest senaryosuyla doğrulanmış olup hem kaynak kod hem de imzalı taşınabilir masaüstü paketi olarak teslime hazırdır."
    )

    # =========================================================================
    # BÖLÜM 9: KAYNAKÇA (REFERENCES - IEEE FORMATI)
    # =========================================================================
    add_section_heading(doc, "9. Kaynakça (References)", level=1)

    references = [
        "[1] MDPI Drones, \"Edge-Deployed Anomaly Indicators for UAV Telemetry with Context,\" Drones, vol. 10, no. 9, p. 657, 2024. [Çevrimiçi]. Erişim: https://www.mdpi.com/2504-446X/10/9/657",
        "[2] Advances in Science and Technology Research Journal (ASTRJ), \"Anomaly Detection in Micro Air Vehicle Link Telemetry Logs,\" ASTRJ, 2023. [Çevrimiçi]. Erişim: https://www.astrj.com/pdf-225642-148927",
        "[3] NATO Standardization Office (NSO), \"STANAG 4586: Standard Interfaces of UAV Control System (UCS) for NATO UAV Interoperability,\" STO Educational Notes STO-EN-SCI-271, 2020. [Çevrimiçi]. Erişim: https://publications.sto.nato.int/publications/STO%20Educational%20Notes/STO-EN-SCI-271/EN-SCI-271-03.pdf",
        "[4] J. A. Marty, \"Vulnerability Analysis of the MAVLink Protocol for Command and Control of Unmanned Aircraft,\" M.S. Thesis, Air Force Institute of Technology (AFIT), Wright-Patterson AFB, OH, USA, 2014. [Çevrimiçi]. Erişim: https://scholar.afit.edu/etd/1613/",
        "[5] Dronecode Project, \"MAVLink Common Message Set Specification (GLOBAL_POSITION_INT, ATTITUDE, SYS_STATUS, HEARTBEAT),\" MAVLink Developer Guide, 2025. [Çevrimiçi]. Erişim: https://mavlink.io/en/messages/common.html",
        "[6] National Imagery and Mapping Agency (NIMA), \"Department of Defense World Geodetic System 1984 (WGS 84): Its Definition and Relationships with Local Geodetic Systems,\" Technical Report TR8350.2, 3rd ed., 2000.",
        "[7] M. M. Peet, \"Lecture 9: 6-DOF Equations of Motion and Euler Angles in Aircraft Dynamics,\" Arizona State University, Control Systems Engineering. [Çevrimiçi]. Erişim: https://control.asu.edu/Classes/MMAE441/Aircraft/441Lecture9.pdf",
        "[8] Y. Zeng et al., \"Implementing Tracking Error Control and 6-DOF Kinematics for Quadrotor UAV,\" Eindhoven University of Technology (TU/e), Technical Report. [Çevrimiçi]. Erişim: https://research.tue.nl/files/174244762/1301462_Zeng.pdf",
        "[9] ArduPilot Dev Team, \"ArduCopter Complete Parameter List & Failsafe Documentation (FS_GCS_ENABLE, FS_GCS_TIMEOUT, FS_BATT_ENABLE),\" ArduPilot Official Documentation, v4.7, 2025. [Çevrimiçi]. Erişim: https://ardupilot.org/copter/docs/parameters.html",
        "[10] National Library of Medicine (PMC / NIH), \"An Open Benchmark Dataset for Machine Learning and Intelligent Anomaly Management in Unmanned Aerial Vehicles,\" PMC12982758, 2024. [Çevrimiçi]. Erişim: https://pmc.ncbi.nlm.nih.gov/articles/PMC12982758/",
        "[11] W. McKinney, \"Data Structures for Statistical Computing in Python (Pandas),\" in Proceedings of the 9th Python in Science Conference (SciPy), 2010, pp. 56–61.",
        "[12] J. D. Hunter, \"Matplotlib: A 2D Graphics Environment,\" Computing in Science & Engineering, vol. 9, no. 3, pp. 90–95, IEEE, 2007.",
        "[13] T. Schimansky, \"CustomTkinter: A Modern and Customizable Python UI-Library Based on Tkinter,\" Official Documentation, 2024. [Çevrimiçi]. Erişim: https://customtkinter.tomschimansky.com/",
        "[14] H. Krekel et al., \"pytest: Helps You Write Better Programs — Full-Featured Python Testing Tool,\" Official Documentation, 2025. [Çevrimiçi]. Erişim: https://docs.pytest.org/",
    ]

    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.35)
        p_ref.paragraph_format.first_line_indent = Inches(-0.35)
        p_ref.paragraph_format.space_after = Pt(4)
        r_ref = p_ref.add_run(ref)
        r_ref.font.name = "Calibri"
        r_ref.font.size = Pt(9.5)
        r_ref.font.color.rgb = RGBColor(55, 65, 81)

    doc.save(output_path)
    print(f"Word raporu basariyla olusturuldu: {output_path}")


if __name__ == "__main__":
    out1 = os.path.abspath("IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx")
    build_report(out1)

    desktop_dir = r"C:\Users\PC\Desktop\IHA_Masaustu_Uygulamalari"
    if os.path.exists(desktop_dir):
        out2 = os.path.join(desktop_dir, "IHA_Telemetri_Teknik_Rapor_Mehmet_Akif_Urey.docx")
        build_report(out2)
