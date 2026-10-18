"""
data_generator.py
İHA telemetri verisi üretim motoru.
Genişletilebilir senaryo tabanlı sentetik veri üretimi sağlar.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

SCENARIO_DESCRIPTIONS = {
    "valid": "1. %100 Geçerli Uçuş Verisi (Düzgün tırmanış ve seyir)",
    "with_gaps": "2. Zaman Boşluğu / Kesintili Uçuş (Örn: 8 saniyelik veri kaybı)",
    "mixed": "3. Karışık / Kısmi Hatalı Veri (Geçerli + farklı hata türleri)",
    "negative_speed": "4. Negatif Hız Değerleri İçeren Veri",
    "battery_bounds": "5. Batarya Sınır İhlali (%0 altı ve %100 üstü)",
    "coord_bounds": "6. Geçersiz Enlem/Boylam (Lat [-90,90], Lon [-180,180] dışı)",
    "text_in_numeric": "7. Sayısal Alanda Metin (Örn: altitude='YUKSEK')",
    "empty_fields": "8. Zorunlu Alanları Boş Bırakılmış Satırlar",
    "bad_timestamps": "9. Çözümlenemeyen / Bozuk Zaman Damgaları",
    "bad_angles": "10. Açısal Sınır İhlalleri (Pitch/Roll > 180, Yaw > 360)",
    "missing_columns": "11. Gerekli Sütunları Eksik CSV",
    "all_invalid": "12. Sıfır Geçerli Kayıt (Tüm satırlar hatalı)",
    "empty_file": "13. Boş Dosya (0 bayt)",
    "corrupt_file": "14. Bozuk Biçimli / Sözdizimi Hatalı CSV"
}

class TelemetryScenarioGenerator:
    """Belirlenen senaryoya göre sentetik telemetri verisi üreten motor."""

    def __init__(self):
        self.scenarios = SCENARIO_DESCRIPTIONS

    def get_available_scenarios(self) -> Dict[str, str]:
        return self.scenarios

    def generate_data(
        self,
        scenario_key: str,
        count: int = 50,
        start_time: Optional[datetime] = None,
        gap_duration_sec: float = 7.0,
        initial_altitude: float = 50.0,
        initial_speed: float = 15.0,
        initial_battery: float = 100.0
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Belirtilen senaryo için DataFrame veya ham içerik üretir.
        Döner: (DataFrame, raw_content_str)
        """
        base_time = start_time or datetime(2026, 10, 20, 14, 30, 0)
        lat = 41.015137
        lon = 28.979530
        battery = initial_battery

        if scenario_key == "empty_file":
            return None, ""

        if scenario_key == "corrupt_file":
            raw_str = (
                "timestamp,altitude,speed\n"
                "\"unterminated quote string,100,20\n"
                "\x00\x01\x02\x03\xff\xfe\n"
            )
            return None, raw_str

        if scenario_key == "missing_columns":
            rows = []
            for i in range(count):
                curr_t = base_time + timedelta(seconds=i)
                rows.append({
                    "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                    "altitude": initial_altitude + (i * 1.2),
                    "speed": initial_speed,
                    "longitude": round(lon + (i * 0.0001), 6),
                    "latitude": round(lat + (i * 0.0001), 6),
                    "roll": 0.0
                    # missing: speed, battery_pct, pitch, yaw
                })
            return pd.DataFrame(rows), None

        # Standart satırlar oluşturma
        rows = []
        current_time = base_time
        for i in range(count):
            # Zaman boşluğu senaryosu
            if scenario_key == "with_gaps" and i == int(count // 2):
                current_time += timedelta(seconds=gap_duration_sec)
            else:
                current_time += timedelta(seconds=1)

            alt = initial_altitude + (i * 1.5) if i < (count // 2) else initial_altitude + ((count // 2) * 1.5)
            spd = initial_speed + (i * 0.1)
            battery = max(0.0, battery - 0.2)
            c_lat = lat + (i * 0.00005)
            c_lon = lon + (i * 0.00007)
            pitch = 2.5 if i < (count // 2) else 0.5
            roll = 1.0 if i % 10 < 5 else -1.0
            yaw = (45.0 + (i * 0.8)) % 360.0

            row = {
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "altitude": round(alt, 2),
                "speed": round(spd, 2),
                "battery_pct": round(battery, 2),
                "longitude": round(c_lon, 6),
                "latitude": round(c_lat, 6),
                "pitch": round(pitch, 2),
                "roll": round(roll, 2),
                "yaw": round(yaw, 2)
            }

            # Senaryo spesifik hata enjeksiyonu
            if scenario_key == "negative_speed" and i % 5 == 0:
                row["speed"] = -12.5

            elif scenario_key == "battery_bounds":
                if i % 6 == 0:
                    row["battery_pct"] = 125.0
                elif i % 6 == 3:
                    row["battery_pct"] = -8.0

            elif scenario_key == "coord_bounds":
                if i % 6 == 0:
                    row["latitude"] = 98.5
                elif i % 6 == 3:
                    row["longitude"] = -195.0

            elif scenario_key == "text_in_numeric" and i % 5 == 0:
                row["altitude"] = "COK_YUKSEK"

            elif scenario_key == "empty_fields" and i % 5 == 0:
                row["speed"] = ""

            elif scenario_key == "bad_timestamps" and i % 5 == 0:
                row["timestamp"] = "HATALI_ZAMAN_2026"

            elif scenario_key == "bad_angles":
                if i % 6 == 0:
                    row["pitch"] = 210.0
                elif i % 6 == 3:
                    row["roll"] = -250.0

            elif scenario_key == "all_invalid":
                # Tüm satırlara hata enjekte et
                row["speed"] = -15.0
                row["battery_pct"] = 150.0

            elif scenario_key == "mixed":
                # Karışık senaryoda her 4 satırda bir farklı bir hata türü
                if i % 10 == 2:
                    row["speed"] = -10.0
                elif i % 10 == 4:
                    row["battery_pct"] = 120.0
                elif i % 10 == 6:
                    row["latitude"] = 94.0
                elif i % 10 == 8:
                    row["altitude"] = "METIN_HATASI"

            rows.append(row)

        return pd.DataFrame(rows), None

    def generate_and_save(
        self,
        scenario_key: str,
        output_file_path: str,
        **kwargs
    ) -> str:
        """Veriyi üretir ve belirtilen yola kaydeder."""
        os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
        df, raw_content = self.generate_data(scenario_key, **kwargs)

        if raw_content is not None:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(raw_content)
        elif df is not None:
            df.to_csv(output_file_path, index=False)
        else:
            with open(output_file_path, "w", encoding="utf-8") as f:
                pass

        return output_file_path


def generate_all_samples(output_dir: str = "samples") -> Dict[str, str]:
    """Geriye dönük uyumluluk için varsayılan örnek setleri oluşturur."""
    os.makedirs(output_dir, exist_ok=True)
    gen = TelemetryScenarioGenerator()

    mapping = {
        "valid": "telemetry_valid.csv",
        "mixed": "telemetry_mixed.csv",
        "corrupted": "telemetry_corrupted.csv",
        "missing_columns": "telemetry_missing_columns.csv",
        "empty": "telemetry_empty.csv"
    }

    files = {}
    for key, fname in mapping.items():
        scenario_name = "corrupt_file" if key == "corrupted" else ("empty_file" if key == "empty" else key)
        path = os.path.join(output_dir, fname)
        gen.generate_and_save(scenario_name, path)
        files[key] = path

    return files


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "samples"
    res = generate_all_samples(target)
    print("Örnek CSV dosyaları üretildi:")
    for k, v in res.items():
        print(f" - {k}: {v}")
