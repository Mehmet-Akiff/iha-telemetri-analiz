"""
create_assets.py
İHA Telemetri Analiz İstasyonu ve İHA CSV Senaryo Üretici için
yüksek çözünürlüklü, belirgin İHA/SİHA (Taktik Drone & Sabit Kanat İHA) ikonları (.ico ve .png)
ve açılış görselleri üreten yardımcı modül (v1.4.0).
"""

import os
import math
from PIL import Image, ImageDraw


def draw_uav_analyzer_icon(output_ico: str, output_png: str = None):
    """
    Analiz İstasyonu için:
    Taktik SİHA / İHA (Bayraktar/MQ-9 tarzı V-kuyruk ve geniş kanatlı İHA silüeti)
    + Radar tarama halkaları + Telemetri sinyal dalgaları içeren belirgin ikon.
    """
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Dış Kalkan / Kokpit Radar Çerçevesi (Koyu Gece Mavisi & Parlak Siyan Çerçeve)
    draw.rounded_rectangle([8, 8, 248, 248], radius=54, fill=(11, 21, 38, 255), outline=(0, 210, 255, 255), width=7)
    draw.rounded_rectangle([18, 18, 238, 238], radius=44, fill=(15, 29, 52, 255), outline=(25, 113, 194, 180), width=2)

    # 2. Radar Halkaları ve Eksen Çizgileri
    draw.ellipse([42, 42, 214, 214], outline=(0, 210, 255, 75), width=2)
    draw.ellipse([78, 78, 178, 178], outline=(0, 210, 255, 110), width=2)
    draw.line([128, 26, 128, 230], fill=(0, 210, 255, 60), width=2)
    draw.line([26, 128, 230, 128], fill=(0, 210, 255, 60), width=2)

    # 3. Üstte Telemetri Radyo Dalgaları (Altın/Turuncu Sinyal Yayları)
    draw.arc([88, 22, 168, 82], start=210, end=330, fill=(255, 192, 56, 255), width=4)
    draw.arc([72, 10, 184, 90], start=215, end=325, fill=(255, 192, 56, 190), width=3)

    # 4. Belirgin Taktik İHA / SİHA Silüeti (Merkezde yukarı doğru uçan sabit kanatlı İHA)
    # Ana Kanatlar (Geniş aerodinamik swept-wing)
    wing_polygon = [
        (128, 86),   # Kanat ön birleşim
        (28, 134),   # Sol kanat ucu ön
        (28, 148),   # Sol kanat ucu arka
        (114, 126),  # Sol kanat kök arka
        (142, 126),  # Sağ kanat kök arka
        (228, 148),  # Sağ kanat ucu arka
        (228, 134),  # Sağ kanat ucu ön
    ]
    draw.polygon(wing_polygon, fill=(225, 240, 255, 255), outline=(0, 210, 255, 255))

    # V-Kuyruk / Arka Kanatçıklar (Bayraktar TB2 / Akıncı tarzı kuyruk)
    tail_polygon = [
        (128, 166),
        (78, 206),
        (84, 216),
        (128, 192),
        (172, 216),
        (178, 206),
    ]
    draw.polygon(tail_polygon, fill=(165, 216, 255, 255), outline=(0, 210, 255, 255))

    # İHA Gövdesi (Burundan kuyruğa aerodinamik fuselaj)
    fuselage_polygon = [
        (128, 42),   # Sivri burun / Radom
        (114, 78),   # Sol ön gövde
        (116, 178),  # Sol arka gövde
        (128, 208),  # Kuyruk motor ucu
        (140, 178),  # Sağ arka gövde
        (142, 78),   # Sağ ön gövde
    ]
    draw.polygon(fuselage_polygon, fill=(255, 255, 255, 255), outline=(51, 154, 240, 255))

    # Kokpit / Uydu Haberleşme Kubbesi (SatCom Dome - Parlak Mavi/Turkuaz)
    draw.ellipse([119, 60, 137, 94], fill=(0, 180, 240, 255), outline=(255, 255, 255, 255), width=2)

    # Kanat Altı Sensör / Faydalı Yük Noktaları (Yeşil/Kırmızı Navigasyon Işıkları)
    draw.ellipse([42, 136, 54, 148], fill=(255, 82, 82, 255))    # İskele (Sol) kırmızı ışık
    draw.ellipse([202, 136, 214, 148], fill=(81, 207, 102, 255)) # Sancak (Sağ) yeşil ışık

    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    os.makedirs(os.path.dirname(os.path.abspath(output_ico)), exist_ok=True)
    img.save(output_ico, format="ICO", sizes=icon_sizes)
    if output_png:
        img.save(output_png, format="PNG")
    print(f"[OK] UAV Analyzer icon created: {output_ico}")


def draw_uav_generator_icon(output_ico: str, output_png: str = None):
    """
    CSV Senaryo Üretici için:
    Döner Kanatlı Taktik İHA (Quadcopter Drone) + Altında Canlı Telemetri Veri Akışı / CSV Dalgaları
    içeren belirgin İHA simülatör ikonu.
    """
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Arka Plan Kalkanı (Zümrüt Yeşili & Koyu Siber Gri)
    draw.rounded_rectangle([8, 8, 248, 248], radius=54, fill=(12, 32, 24, 255), outline=(43, 218, 114, 255), width=7)
    draw.rounded_rectangle([18, 18, 238, 238], radius=44, fill=(18, 44, 34, 255), outline=(32, 201, 151, 160), width=2)

    # 2. Alt Kısımda CSV Veri Akışı / Telemetri Sinyal Çizgileri
    draw.rounded_rectangle([38, 168, 218, 224], radius=12, fill=(10, 24, 18, 230), outline=(43, 218, 114, 180), width=2)
    # Sinyal/CSV grafik çizgisi
    signal_pts = [(48, 205), (72, 185), (95, 208), (122, 178), (148, 198), (175, 180), (206, 195)]
    draw.line(signal_pts, fill=(81, 255, 148, 255), width=4)
    for px, py in signal_pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 212, 59, 255))

    # 3. Üst/Orta Kısımda Belirgin Quadcopter İHA (Drone) Tasarımı
    cx, cy = 128, 98
    arm_offsets = [(-54, -42), (54, -42), (-54, 42), (54, 42)]

    # Drone Kolları
    for ox, oy in arm_offsets:
        draw.line([cx, cy, cx + ox, cy + oy], fill=(210, 235, 220, 255), width=10)

    # 4 Rotor ve Dönen Pervane Halkaları
    for ox, oy in arm_offsets:
        rx, ry = cx + ox, cy + oy
        # Pervane dönüş diski
        draw.ellipse([rx - 28, ry - 14, rx + 28, ry + 14], fill=(43, 218, 114, 90), outline=(105, 255, 170, 255), width=3)
        # Pervane kanadı
        draw.line([rx - 22, ry, rx + 22, ry], fill=(255, 255, 255, 255), width=4)
        # Motor göbeği
        draw.ellipse([rx - 8, ry - 8, rx + 8, ry + 8], fill=(20, 50, 35, 255), outline=(255, 212, 59, 255), width=3)

    # Drone Merkez Gövdesi (Sekizgenimsi yuvarlak kokpit)
    draw.rounded_rectangle([cx - 26, cy - 32, cx + 26, cy + 32], radius=14, fill=(235, 250, 240, 255), outline=(43, 218, 114, 255), width=4)
    # Kamera / Sensör Lensi
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(15, 35, 28, 255), outline=(0, 210, 255, 255), width=3)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 107, 107, 255))

    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    os.makedirs(os.path.dirname(os.path.abspath(output_ico)), exist_ok=True)
    img.save(output_ico, format="ICO", sizes=icon_sizes)
    if output_png:
        img.save(output_png, format="PNG")
    print(f"[OK] UAV Generator icon created: {output_ico}")


if __name__ == "__main__":
    # 1. Analiz İstasyonu İkonları
    draw_uav_analyzer_icon("assets/telemetry_icon.ico", "assets/telemetry_icon.png")

    # 2. CSV Senaryo Üretici İkonları
    gen_assets = r"C:\Users\PC\Desktop\Projects\iha-csv-senaryo-uretici\assets"
    os.makedirs(gen_assets, exist_ok=True)
    draw_uav_generator_icon(
        os.path.join(gen_assets, "generator_icon.ico"),
        os.path.join(gen_assets, "generator_icon.png"),
    )
