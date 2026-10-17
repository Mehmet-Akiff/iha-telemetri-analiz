"""
data_generator.py
Test ve gösterim amacıyla örnek İHA telemetri CSV dosyaları üreten modül.
Geçerli, hatalı, karışık, bozuk ve eksik sütunlu test verileri oluşturur.
"""

import os
from datetime import datetime, timedelta
from typing import Dict
import pandas as pd

def generate_all_samples(output_dir: str = "samples") -> Dict[str, str]:
    """
    Belirtilen dizin altında 5 farklı senaryoyu test eden CSV dosyalarını üretir.
    Dönen sözlük dosya yollarını içerir.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = {}

    base_time = datetime(2026, 10, 20, 14, 30, 0)

    # -------------------------------------------------------------
    # 1. telemetry_valid.csv: Gerçekçi ve %100 geçerli 60 saniyelik uçuş
    # -------------------------------------------------------------
    valid_rows = []
    lat = 41.015137
    lon = 28.979530
    battery = 100.0
    
    current_time = base_time
    for i in range(60):
        # 30. saniyede 6 saniyelik bir simüle telemetri boşluğu enjekte ediyoruz
        if i == 30:
            current_time += timedelta(seconds=6)
        else:
            current_time += timedelta(seconds=1)

        # Uçuş profili: tırmanış ve düz uçuş
        altitude = 50.0 + (i * 1.5) if i < 30 else 95.0 + ((i % 5) * 0.2)
        speed = 12.0 + (i * 0.15) if i < 20 else 18.0 + ((i % 3) * 0.3)
        battery = max(0.0, battery - 0.18)
        lat += 0.00005
        lon += 0.00007
        pitch = 3.5 if i < 30 else 0.2
        roll = 1.0 if i % 10 < 5 else -1.0
        yaw = (45.0 + (i * 0.5)) % 360.0

        valid_rows.append({
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "altitude": round(altitude, 2),
            "speed": round(speed, 2),
            "battery_pct": round(battery, 2),
            "longitude": round(lon, 6),
            "latitude": round(lat, 6),
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
            "yaw": round(yaw, 2)
        })

    valid_path = os.path.join(output_dir, "telemetry_valid.csv")
    pd.DataFrame(valid_rows).to_csv(valid_path, index=False)
    generated_files["valid"] = valid_path

    # -------------------------------------------------------------
    # 2. telemetry_mixed.csv: Geçerli + Bilerek Hatalı Enjekte Edilmiş Kayıtlar
    # -------------------------------------------------------------
    mixed_rows = []
    current_time = base_time
    # 20 geçerli kayıt
    for i in range(20):
        current_time += timedelta(seconds=1)
        mixed_rows.append({
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "altitude": 100.0 + i,
            "speed": 15.0,
            "battery_pct": 90.0 - (i * 0.5),
            "longitude": 29.001 + (i * 0.0001),
            "latitude": 41.001 + (i * 0.0001),
            "pitch": 1.5,
            "roll": -0.5,
            "yaw": 180.0
        })

    # 10 kasıtlı hatalı kayıt ekle (PDF 4. bölümdeki kural ihlalleri)
    error_injections = [
        # 1. Negatif hız
        {"timestamp": (current_time + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": 120.0, "speed": -10.5, "battery_pct": 80.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
        # 2. %100 üstü batarya
        {"timestamp": (current_time + timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": 120.0, "speed": 15.0, "battery_pct": 130.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
        # 3. Negatif batarya
        {"timestamp": (current_time + timedelta(seconds=3)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": 120.0, "speed": 15.0, "battery_pct": -5.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
        # 4. Geçersiz enlem (> 90)
        {"timestamp": (current_time + timedelta(seconds=4)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": 120.0, "speed": 15.0, "battery_pct": 78.0, "longitude": 29.01, "latitude": 98.4, "pitch": 0, "roll": 0, "yaw": 0},
        # 5. Geçersiz boylam (< -180)
        {"timestamp": (current_time + timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": 120.0, "speed": 15.0, "battery_pct": 77.0, "longitude": -195.0, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
        # 6. Sayısal olması gereken alanda metin
        {"timestamp": (current_time + timedelta(seconds=6)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": "COK_YUKSEK", "speed": 15.0, "battery_pct": 76.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
        # 7. Zorunlu alan boş (speed boş)
        {"timestamp": (current_time + timedelta(seconds=7)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": 120.0, "speed": "", "battery_pct": 75.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
        # 8. Bozuk / çözümlenemeyen zaman damgası
        {"timestamp": "HATALI_ZAMAN_DAMGASI", "altitude": 120.0, "speed": 15.0, "battery_pct": 74.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
        # 9. Açı sınırı ihlali (roll > 180)
        {"timestamp": (current_time + timedelta(seconds=9)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": 120.0, "speed": 15.0, "battery_pct": 73.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 250.0, "yaw": 0},
        # 10. İrtifa boş
        {"timestamp": (current_time + timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S"), "altitude": "", "speed": 15.0, "battery_pct": 72.0, "longitude": 29.01, "latitude": 41.01, "pitch": 0, "roll": 0, "yaw": 0},
    ]
    mixed_rows.extend(error_injections)

    # Arkasından 10 adet daha geçerli kayıt ekle (Kısmi kurtarmanın devam ettiğini kanıtlamak için)
    current_time += timedelta(seconds=11)
    for i in range(10):
        current_time += timedelta(seconds=1)
        mixed_rows.append({
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "altitude": 130.0 + i,
            "speed": 16.0,
            "battery_pct": 70.0 - (i * 0.4),
            "longitude": 29.005 + (i * 0.0001),
            "latitude": 41.005 + (i * 0.0001),
            "pitch": 0.5,
            "roll": 0.0,
            "yaw": 185.0
        })

    mixed_path = os.path.join(output_dir, "telemetry_mixed.csv")
    pd.DataFrame(mixed_rows).to_csv(mixed_path, index=False)
    generated_files["mixed"] = mixed_path

    # -------------------------------------------------------------
    # 3. telemetry_corrupted.csv: Bozuk CSV / geçersiz sözdizimi
    # -------------------------------------------------------------
    corrupted_path = os.path.join(output_dir, "telemetry_corrupted.csv")
    with open(corrupted_path, "w", encoding="utf-8") as f:
        f.write("timestamp,altitude,speed\n"
                "\"unterminated quote string,100,20\n"
                "\x00\x01\x02\x03\xff\xfe\n")
    generated_files["corrupted"] = corrupted_path

    # -------------------------------------------------------------
    # 4. telemetry_missing_columns.csv: Gerekli sütunları eksik dosya
    # -------------------------------------------------------------
    missing_cols_path = os.path.join(output_dir, "telemetry_missing_columns.csv")
    # Missing yaw, battery_pct, pitch
    incomplete_df = pd.DataFrame([{
        "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"),
        "altitude": 100.0,
        "speed": 15.0,
        "longitude": 29.0,
        "latitude": 41.0,
        "roll": 0.0
    }])
    incomplete_df.to_csv(missing_cols_path, index=False)
    generated_files["missing_columns"] = missing_cols_path

    # -------------------------------------------------------------
    # 5. telemetry_empty.csv: 0 baytlık boş dosya
    # -------------------------------------------------------------
    empty_path = os.path.join(output_dir, "telemetry_empty.csv")
    with open(empty_path, "w", encoding="utf-8") as f:
        pass
    generated_files["empty"] = empty_path

    return generated_files

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "samples"
    files = generate_all_samples(target)
    print("Örnek CSV dosyaları başarıyla üretildi:")
    for k, v in files.items():
        print(f" - [{k}]: {v}")
