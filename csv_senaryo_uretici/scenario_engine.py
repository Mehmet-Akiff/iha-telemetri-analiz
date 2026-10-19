"""
scenario_engine.py
İHA telemetri verisi senaryo üretim motoru (v1.5.0).
14 farklı uçuş, sınır ve hata senaryosu üretir.
Her üretim periyodunu hedef klasördeki en büyük numarayı takip ederek
'Üretilen Klasör N - Tarih' formatında sıralı ve izole klasörlerde depolar.
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
import pandas as pd

SCENARIO_DESCRIPTIONS = {
    "valid": "1. %100 Geçerli Uçuş Verisi (Düzgün tırmanış ve seyir profili)",
    "with_gaps": "2. Zaman Boşluğu / Kesintili Uçuş (Örn: 8 saniyelik telemetri kaybı)",
    "mixed": "3. Karışık / Kısmi Hatalı Veri (Geçerli kayıtlar + farklı hata türleri)",
    "negative_speed": "4. Negatif Hız Değerleri İçeren Veri (speed < 0)",
    "battery_bounds": "5. Batarya Sınır İhlali (%0 altı ve %100 üstü)",
    "coord_bounds": "6. Geçersiz Enlem/Boylam (Lat [-90,90], Lon [-180,180] dışı)",
    "text_in_numeric": "7. Sayısal Alanda Metin (Örn: altitude='COK_YUKSEK')",
    "empty_fields": "8. Zorunlu Alanları Boş Bırakılmış Satırlar",
    "bad_timestamps": "9. Çözümlenemeyen / Bozuk Zaman Damgaları",
    "bad_angles": "10. Açısal Sınır İhlalleri (Pitch/Roll > 180, Yaw > 360)",
    "missing_columns": "11. Gerekli Sütunları Eksik CSV",
    "all_invalid": "12. Sıfır Geçerli Kayıt (Tüm satırlar hatalı)",
    "empty_file": "13. Boş Dosya (0 bayt)",
    "corrupt_file": "14. Bozuk Biçimli / Sözdizimi Hatalı CSV"
}

# 5 Temel Senaryo Paketi (Hızlı ve etkili test için 5 temel CSV)
TEMEL_SCENARIOS = {
    "valid": "01_gecerli_ucus.csv",
    "with_gaps": "02_zaman_kesintili_ucus.csv",
    "mixed": "03_karisik_hatali_ucus.csv",
    "negative_speed": "04_negatif_hiz_hatasi.csv",
    "battery_bounds": "05_batarya_sinir_ihlali.csv",
}

# 14 Senaryonun Tamamı
TUM_SCENARIOS = {
    "valid": "01_gecerli_ucus.csv",
    "with_gaps": "02_zaman_kesintili_ucus.csv",
    "mixed": "03_karisik_hatali_ucus.csv",
    "negative_speed": "04_negatif_hiz_hatasi.csv",
    "battery_bounds": "05_batarya_sinir_ihlali.csv",
    "coord_bounds": "06_koordinat_sinir_ihlali.csv",
    "text_in_numeric": "07_sayisal_alanda_metin.csv",
    "empty_fields": "08_bos_zorunlu_alanlar.csv",
    "bad_timestamps": "09_bozuk_zaman_damgasi.csv",
    "bad_angles": "10_acisal_sinir_ihlalleri.csv",
    "missing_columns": "11_eksik_sutunlu_csv.csv",
    "all_invalid": "12_sifir_gecerli_kayit.csv",
    "empty_file": "13_bos_dosya_0_bayt.csv",
    "corrupt_file": "14_bozuk_csv_sozdizimi.csv",
}


class TelemetryScenarioGenerator:
    """Belirlenen senaryoya göre sentetik telemetri verisi üreten motor."""

    def __init__(self):
        self.scenarios = SCENARIO_DESCRIPTIONS

    def get_available_scenarios(self) -> Dict[str, str]:
        return self.scenarios

    def get_next_sequence_number(self, base_output_dir: str) -> int:
        """
        Hedef klasördeki mevcut alt klasörleri tarar ve bulunan EN BÜYÜK sayıdan 1 fazlasını döner.
        - Eğer klasörde hiç numaralı klasör yoksa: 1 döner.
        - Eğer klasörde 1 ve 2 varsa: 2 + 1 = 3 döner.
        - Eğer 1 silinmiş ancak 2 duruyorsa: max(2) + 1 = 3 döner (en büyük sayıdan devam eder).
        - Eğer yeni/farklı bir boş klasöre geçilirse: 1 döner.
        """
        if not os.path.exists(base_output_dir):
            return 1

        seq_nums = []
        pattern = re.compile(r"(?:Üretilen[ _]Klasör[ _]|Uretim[ _]|Klasor[ _]|^)(\d+)", re.IGNORECASE)

        for item in os.listdir(base_output_dir):
            full_path = os.path.join(base_output_dir, item)
            if os.path.isdir(full_path):
                match = pattern.search(item)
                if match:
                    try:
                        num = int(match.group(1))
                        seq_nums.append(num)
                    except ValueError:
                        pass

        if seq_nums:
            return max(seq_nums) + 1
        return 1

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
                })
            return pd.DataFrame(rows), None

        rows = []
        current_time = base_time
        for i in range(count):
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
                row["speed"] = -15.0
                row["battery_pct"] = 150.0
            elif scenario_key == "mixed":
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

    def generate_numbered_folder(
        self,
        base_output_dir: str,
        mode: str = "temel",
        selected_scenario_key: str = "valid",
        **kwargs
    ) -> Tuple[str, int, int]:
        """
        Hedef klasördeki en büyük sayıyı bulur, 1 fazlasını alarak
        'Üretilen Klasör N - Tarih' formatında izole klasör açar ve CSV'leri üretir.
        Döner: (target_folder_path, sequence_number, file_count)
        """
        os.makedirs(base_output_dir, exist_ok=True)
        seq_num = self.get_next_sequence_number(base_output_dir)
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = f"Üretilen Klasör {seq_num} - {now_str}"
        target_dir = os.path.join(base_output_dir, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        if mode == "temel":
            scenarios_to_gen = TEMEL_SCENARIOS
            mode_title = "Temel Test Paketi (5 Senaryo)"
        elif mode == "tum":
            scenarios_to_gen = TUM_SCENARIOS
            mode_title = "Tüm 14 Senaryo Paketi"
        else:  # tekil
            filename = f"01_{selected_scenario_key}.csv"
            scenarios_to_gen = {selected_scenario_key: filename}
            mode_title = f"Tekil Senaryo ({selected_scenario_key})"

        report_lines = [
            f"# İHA TELEMETRİ ÜRETİM RAPORU - {folder_name}",
            f"Paket Türü: {mode_title}",
            f"Tarih/Saat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Klasör Numarası: #{seq_num}",
            "-" * 60,
            "Klasördeki CSV Dosyaları:"
        ]

        file_count = 0
        for key, filename in scenarios_to_gen.items():
            out_file = os.path.join(target_dir, filename)
            self.generate_and_save(key, out_file, **kwargs)
            desc = self.scenarios.get(key, key)
            report_lines.append(f"• {filename}  -->  {desc}")
            file_count += 1

        with open(os.path.join(target_dir, "senaryo_listesi.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        return target_dir, seq_num, file_count

    def generate_isolated_batch(self, base_output_dir: str = "samples", **kwargs) -> str:
        """Geriye dönük uyumluluk için eski metot çağrısı."""
        target_dir, _, _ = self.generate_numbered_folder(base_output_dir, mode="tum", **kwargs)
        return target_dir
