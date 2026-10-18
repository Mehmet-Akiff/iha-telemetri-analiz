"""
create_assets.py
İHA Telemetri Analiz ve CSV Senaryo Üretici için profesyonel ikonlar (.ico)
ve açılış ekranı (splash screen .png) görselleri üreten yardımcı araç.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_telemetry_icon(output_path: str):
    """Modern UAV / Radar temalı çok katmanlı .ico dosyası üretir."""
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Arka plan dairesi (Derin mavi / lacivert degradeli)
    draw.ellipse([8, 8, 248, 248], fill=(18, 24, 38, 255), outline=(51, 154, 240, 255), width=6)

    # Radar halkaları
    draw.ellipse([45, 45, 211, 211], outline=(34, 139, 230, 100), width=3)
    draw.ellipse([85, 85, 171, 171], outline=(34, 139, 230, 140), width=2)
    draw.line([128, 20, 128, 236], fill=(34, 139, 230, 80), width=2)
    draw.line([20, 128, 236, 128], fill=(34, 139, 230, 80), width=2)

    # Döner kanatlı İHA (Quadcopter) sembolü
    center = (128, 128)
    # Kollar (X şeklinde)
    draw.line([75, 75, 181, 181], fill=(240, 246, 252, 255), width=8)
    draw.line([75, 181, 181, 75], fill=(240, 246, 252, 255), width=8)

    # Motor merkezleri ve pervaneler
    rotors = [(75, 75), (181, 75), (75, 181), (181, 181)]
    for rx, ry in rotors:
        draw.ellipse([rx - 22, ry - 7, rx + 22, ry + 7], outline=(99, 230, 190, 255), width=3)
        draw.ellipse([rx - 6, ry - 6, rx + 6, ry + 6], fill=(32, 201, 151, 255))

    # Gövde merkezi ve kamera/sensör
    draw.ellipse([108, 108, 148, 148], fill=(24, 100, 171, 255), outline=(77, 171, 247, 255), width=3)
    draw.ellipse([121, 121, 135, 135], fill=(255, 107, 107, 255))

    # Çok katmanlı ICO olarak kaydet
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, format="ICO", sizes=icon_sizes)
    print(f"Telemetry icon created: {output_path}")

def create_generator_icon(output_path: str):
    """CSV ve Simülasyon Test temalı .ico dosyası üretir."""
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Arka plan yuvarlak kare (Yeşil / laboratuvar tonu)
    draw.rounded_rectangle([12, 12, 244, 244], radius=40, fill=(20, 36, 28, 255), outline=(64, 192, 87, 255), width=6)

    # Belge / CSV tablosu sembolü
    draw.rounded_rectangle([55, 45, 201, 211], radius=16, fill=(33, 37, 41, 255), outline=(134, 142, 150, 255), width=4)

    # Tablo satırları ve ızgarası
    draw.line([55, 95, 201, 95], fill=(64, 192, 87, 255), width=4)
    draw.line([105, 45, 105, 211], fill=(73, 80, 87, 255), width=2)
    draw.line([155, 45, 155, 211], fill=(73, 80, 87, 255), width=2)

    for y in [130, 165, 200]:
        draw.line([55, y, 201, y], fill=(73, 80, 87, 255), width=2)

    # Dişli / Üretici çarkı sembolü (sağ alt köşede)
    cx, cy = 180, 190
    draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(43, 138, 62, 255), outline=(178, 242, 187, 255), width=3)
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(20, 36, 28, 255))

    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, format="ICO", sizes=icon_sizes)
    print(f"Generator icon created: {output_path}")

def create_splash_image(output_path: str, title: str, subtitle: str, color_accent=(51, 154, 240)):
    """PyInstaller için açılış yükleme ekranı (Splash Screen PNG) üretir."""
    width, height = 540, 280
    img = Image.new("RGBA", (width, height), (26, 29, 36, 255))
    draw = ImageDraw.Draw(img)

    # Dış çerçeve ve şık köşe
    draw.rectangle([0, 0, width - 1, height - 1], outline=(60, 65, 76, 255), width=2)
    # Üst vurgu çizgisi
    draw.rectangle([0, 0, width, 5], fill=color_accent)

    # Başlık ve logo sembolü
    draw.text((45, 55), "🛸", font=None, fill=(255, 255, 255, 255))
    draw.text((80, 50), title, font=None, fill=(255, 255, 255, 255))
    draw.text((80, 85), subtitle, font=None, fill=(173, 181, 189, 255))

    # Yükleniyor bilgisi
    draw.text((45, 160), "Sistem bileşenleri hazırlanıyor...", font=None, fill=(206, 212, 218, 255))

    # Şık sahte yükleme çubuğu
    bar_x, bar_y, bar_w, bar_h = 45, 195, 450, 10
    draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=5, fill=(45, 49, 58, 255))
    draw.rounded_rectangle([bar_x, bar_y, bar_x + 310, bar_y + bar_h], radius=5, fill=color_accent)

    # Alt sürüm ve güvenli bildirim metni
    draw.text((45, 235), "v1.1.0 • Doğrulanmış Güvenli Windows Uygulaması", font=None, fill=(108, 117, 125, 255))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, format="PNG")
    print(f"Splash screen created: {output_path}")

if __name__ == "__main__":
    # Proje 1 (İME Proje - Analiz)
    create_telemetry_icon("assets/telemetry_icon.ico")
    create_splash_image("assets/splash_telemetry.png", "İHA Telemetri Analiz İstasyonu", "Yükleniyor, lütfen bekleyiniz...", (51, 154, 240))

    # Proje 2 (iha-csv-senaryo-uretici)
    gen_assets = "C:/Users/PC/Desktop/Projects/iha-csv-senaryo-uretici/assets"
    create_generator_icon(os.path.join(gen_assets, "generator_icon.ico"))
    create_splash_image(os.path.join(gen_assets, "splash_generator.png"), "İHA Telemetri CSV Senaryo Üretici", "Test motoru yükleniyor, lütfen bekleyiniz...", (64, 192, 87))
