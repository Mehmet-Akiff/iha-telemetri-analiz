"""
tests/test_telemetry.py
PDF Bölüm 6'da belirtilen 10 zorunlu senaryo ve 5 ek senaryoyu (toplam 15 senaryo)
kapsayan pytest test paketi.
"""

import os
import pytest
import pandas as pd
from datetime import datetime, timedelta
from telemetry_validator import TelemetryValidator, ValidationResult
from telemetry_analyzer import TelemetryAnalyzer, AnalysisResult

@pytest.fixture
def validator():
    return TelemetryValidator()

@pytest.fixture
def analyzer():
    return TelemetryAnalyzer(gap_threshold_seconds=3.0)

# ==============================================================================
# SENARYO 1: Geçerli bir CSV dosyasının doğru şekilde yüklenmesi
# ==============================================================================
def test_scenario_01_valid_csv_loading(tmp_path, validator):
    """Senaryo 1: Geçerli ve eksiksiz bir CSV dosyasının başarıyla yüklenmesi."""
    csv_file = tmp_path / "valid_flight.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,15.0,90.0,29.0,41.0,1.0,0.0,90.0\n"
        "2026-10-20 10:00:01,102.0,15.5,89.8,29.0001,41.0001,1.2,0.1,90.5\n"
    )
    result = validator.validate_file(str(csv_file))
    assert result.is_valid is True
    assert result.fatal_error is None
    assert result.valid_rows == 2
    assert result.invalid_rows == 0
    assert len(result.valid_df) == 2

# ==============================================================================
# SENARYO 2: Gerekli bir sütunun eksik olması
# ==============================================================================
def test_scenario_02_missing_required_column(tmp_path, validator):
    """Senaryo 2: Gerekli sütunlardan birinin (yaw) eksik olması durumunda hata üretilmesi."""
    csv_file = tmp_path / "missing_col.csv"
    # yaw sütunu eksik
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll\n"
        "2026-10-20 10:00:00,100.0,15.0,90.0,29.0,41.0,1.0,0.0\n"
    )
    result = validator.validate_file(str(csv_file))
    assert result.is_valid is False
    assert result.fatal_error is not None
    assert "yaw" in result.fatal_error.lower()

# ==============================================================================
# SENARYO 3: Zorunlu bir alanın boş olması
# ==============================================================================
def test_scenario_03_empty_mandatory_field(tmp_path, validator):
    """Senaryo 3: Bir satırda zorunlu alanın (speed) boş bırakılması."""
    csv_file = tmp_path / "empty_field.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,,90.0,29.0,41.0,1.0,0.0,90.0\n"
    )
    result = validator.validate_file(str(csv_file))
    assert result.valid_rows == 0
    assert result.invalid_rows == 1
    assert any(err.column == "speed" and "boş" in err.message.lower() for err in result.errors)

# ==============================================================================
# SENARYO 4: Sayısal bir alanda geçersiz metin bulunması
# ==============================================================================
def test_scenario_04_invalid_text_in_numeric_field(tmp_path, validator):
    """Senaryo 4: Sayısal olması gereken irtifa (altitude) alanında metin ('YUKSEK') bulunması."""
    csv_file = tmp_path / "text_in_numeric.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,YUKSEK,15.0,90.0,29.0,41.0,1.0,0.0,90.0\n"
    )
    result = validator.validate_file(str(csv_file))
    assert result.valid_rows == 0
    assert result.invalid_rows == 1
    assert any(err.column == "altitude" and "geçersiz metin" in err.message.lower() for err in result.errors)

# ==============================================================================
# SENARYO 5: Batarya değerinin alt ve üst sınırlarının kontrol edilmesi
# ==============================================================================
def test_scenario_05_battery_pct_boundary_limits(tmp_path, validator):
    """Senaryo 5: Bataryanın < %0 ve > %100 değerlerinde reddedilmesi."""
    csv_file = tmp_path / "battery_limits.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,15.0,-5.0,29.0,41.0,0,0,0\n"
        "2026-10-20 10:00:01,100.0,15.0,105.0,29.0,41.0,0,0,0\n"
        "2026-10-20 10:00:02,100.0,15.0,0.0,29.0,41.0,0,0,0\n"
        "2026-10-20 10:00:03,100.0,15.0,100.0,29.0,41.0,0,0,0\n"
    )
    result = validator.validate_file(str(csv_file))
    # 0.0 ve 100.0 geçerli, -5 ve 105 geçersiz olmalı
    assert result.valid_rows == 2
    assert result.invalid_rows == 2
    bat_errors = [e for e in result.errors if e.column == "battery_pct"]
    assert len(bat_errors) == 2

# ==============================================================================
# SENARYO 6: Enlem ve boylam sınırlarının kontrol edilmesi
# ==============================================================================
def test_scenario_06_lat_lon_boundary_limits(tmp_path, validator):
    """Senaryo 6: Enlem (-90..90) ve boylam (-180..180) sınır kontrolleri."""
    csv_file = tmp_path / "coord_limits.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,15.0,80.0,29.0,95.0,0,0,0\n"      # Geçersiz lat > 90
        "2026-10-20 10:00:01,100.0,15.0,80.0,29.0,-92.0,0,0,0\n"     # Geçersiz lat < -90
        "2026-10-20 10:00:02,100.0,15.0,80.0,185.0,41.0,0,0,0\n"     # Geçersiz lon > 180
        "2026-10-20 10:00:03,100.0,15.0,80.0,-190.0,41.0,0,0,0\n"    # Geçersiz lon < -180
    )
    result = validator.validate_file(str(csv_file))
    assert result.valid_rows == 0
    assert result.invalid_rows == 4

# ==============================================================================
# SENARYO 7: Boş veya bozuk CSV dosyasının işlenmesi
# ==============================================================================
def test_scenario_07_empty_or_corrupt_csv(tmp_path, validator):
    """Senaryo 7: Boş dosya veya bozuk CSV yapısında uygun hata mesajı üretilmesi."""
    # Boş dosya
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")
    res_empty = validator.validate_file(str(empty_file))
    assert res_empty.is_valid is False
    assert "boş" in res_empty.fatal_error.lower()

    # Bozuk CSV
    corrupt_file = tmp_path / "corrupt.csv"
    corrupt_file.write_bytes(b"\x00\x01\x02\xff\xfe")
    res_corrupt = validator.validate_file(str(corrupt_file))
    assert res_corrupt.is_valid is False
    assert res_corrupt.fatal_error is not None

# ==============================================================================
# SENARYO 8: Hiç geçerli kayıt bulunmayan bir dosyanın işlenmesi
# ==============================================================================
def test_scenario_08_no_valid_records(tmp_path, validator):
    """Senaryo 8: Dosyadaki tüm satırların hatalı olduğu durum."""
    csv_file = tmp_path / "all_invalid.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,-15.0,80.0,29.0,41.0,0,0,0\n"
        "2026-10-20 10:00:01,100.0,15.0,150.0,29.0,41.0,0,0,0\n"
    )
    result = validator.validate_file(str(csv_file))
    assert result.is_valid is False
    assert result.valid_rows == 0
    assert result.invalid_rows == 2
    assert "geçerli kayıt içermemektedir" in result.fatal_error.lower()

# ==============================================================================
# SENARYO 9: Analiz sonuçlarının beklenen değerlerle karşılaştırılması
# ==============================================================================
def test_scenario_09_analysis_metric_accuracy(analyzer):
    """Senaryo 9: Ortalama/min/maks irtifa, ort. hız ve min bataryanın matematiksel doğruluğu."""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-10-20 12:00:00", periods=4, freq="1s"),
        "altitude": [100.0, 200.0, 300.0, 400.0],  # Ort: 250, Min: 100, Maks: 400
        "speed": [10.0, 20.0, 30.0, 40.0],          # Ort: 25
        "battery_pct": [90.0, 85.0, 75.0, 60.0],    # Min: 60
        "longitude": [29.0] * 4,
        "latitude": [41.0] * 4,
        "pitch": [0.0] * 4,
        "roll": [0.0] * 4,
        "yaw": [0.0] * 4,
    })
    result = analyzer.analyze(df)
    assert result.avg_altitude == 250.0
    assert result.min_altitude == 100.0
    assert result.max_altitude == 400.0
    assert result.avg_speed == 25.0
    assert result.min_battery == 60.0
    assert result.total_flight_time_seconds == 3.0

# ==============================================================================
# SENARYO 10: Zaman damgaları arasındaki olağan dışı boşlukların doğru tespit edilmesi
# ==============================================================================
def test_scenario_10_timestamp_gap_detection(analyzer):
    """Senaryo 10: Belirlenen eşiği (3 saniye) aşan zaman boşluklarının tespiti."""
    times = [
        pd.Timestamp("2026-10-20 12:00:00"),
        pd.Timestamp("2026-10-20 12:00:01"),  # 1 sn delta
        pd.Timestamp("2026-10-20 12:00:08"),  # 7 sn delta -> ANOMALİ (boşluk)
        pd.Timestamp("2026-10-20 12:00:09"),  # 1 sn delta
    ]
    df = pd.DataFrame({
        "timestamp": times,
        "altitude": [100.0] * 4,
        "speed": [15.0] * 4,
        "battery_pct": [80.0] * 4,
        "longitude": [29.0] * 4,
        "latitude": [41.0] * 4,
        "pitch": [0.0] * 4,
        "roll": [0.0] * 4,
        "yaw": [0.0] * 4,
    })
    result = analyzer.analyze(df, gap_threshold_seconds=3.0)
    assert result.has_gaps is True
    assert len(result.timestamp_gaps) == 1
    assert result.timestamp_gaps[0].gap_seconds == 7.0
    assert result.timestamp_gaps[0].start_time == pd.Timestamp("2026-10-20 12:00:01")
    assert result.timestamp_gaps[0].end_time == pd.Timestamp("2026-10-20 12:00:08")

# ==============================================================================
# EK SENARYO 11: Kısmi kurtarma (Geçerli kayıtların işlenmeye devam etmesi)
# ==============================================================================
def test_scenario_11_mixed_partial_recovery(tmp_path, validator):
    """Ek Senaryo 1: Hatalı satırlar varken geçerli satırların başarıyla işlenmesi."""
    csv_file = tmp_path / "mixed.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,15.0,90.0,29.0,41.0,0,0,0\n"   # Geçerli
        "2026-10-20 10:00:01,100.0,-1.0,90.0,29.0,41.0,0,0,0\n"   # Hatalı (negatif hız)
        "2026-10-20 10:00:02,105.0,16.0,89.0,29.0,41.0,0,0,0\n"   # Geçerli
    )
    result = validator.validate_file(str(csv_file))
    assert result.is_valid is True
    assert result.valid_rows == 2
    assert result.invalid_rows == 1
    assert len(result.valid_df) == 2
    assert len(result.errors) == 1

# ==============================================================================
# EK SENARYO 12: Negatif hız değerlerinin tespiti
# ==============================================================================
def test_scenario_12_negative_speed_detection(tmp_path, validator):
    """Ek Senaryo 2: Negatif hız değerinin yakalanması ve açıklayıcı hata verilmesi."""
    csv_file = tmp_path / "negative_speed.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,-12.4,90.0,29.0,41.0,0,0,0\n"
    )
    result = validator.validate_file(str(csv_file))
    assert result.valid_rows == 0
    assert any(err.column == "speed" and "negatif olamaz" in err.message.lower() for err in result.errors)

# ==============================================================================
# EK SENARYO 13: Çözümlenemeyen veya bozuk zaman damgaları
# ==============================================================================
def test_scenario_13_unparseable_timestamp(tmp_path, validator):
    """Ek Senaryo 3: Bozuk veya tarih formatına uymayan zaman damgasının reddedilmesi."""
    csv_file = tmp_path / "bad_time.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "BOZUK_ZAMAN_2026,100.0,15.0,90.0,29.0,41.0,0,0,0\n"
    )
    result = validator.validate_file(str(csv_file))
    assert result.valid_rows == 0
    assert any(err.column == "timestamp" and "çözümlenemeyen" in err.message.lower() for err in result.errors)

# ==============================================================================
# EK SENARYO 14: Açısal (Pitch, Roll, Yaw) sınır ihlallerinin kontrolü
# ==============================================================================
def test_scenario_14_angular_limits(tmp_path, validator):
    """Ek Senaryo 4: Pitch/Roll/Yaw fiziksel/açısal sınırlarının aşılması."""
    csv_file = tmp_path / "bad_angles.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 10:00:00,100.0,15.0,90.0,29.0,41.0,195.0,0,0\n"   # Pitch > 180
        "2026-10-20 10:00:01,100.0,15.0,90.0,29.0,41.0,0,-200.0,0\n"  # Roll < -180
        "2026-10-20 10:00:02,100.0,15.0,90.0,29.0,41.0,0,0,450.0\n"   # Yaw > 360
    )
    result = validator.validate_file(str(csv_file))
    assert result.valid_rows == 0
    assert result.invalid_rows == 3

# ==============================================================================
# EK SENARYO 15: Sırasız gelen telemetrinin analizde sıralanması
# ==============================================================================
def test_scenario_15_unsorted_timestamps_handling(analyzer):
    """Ek Senaryo 5: Kronolojik sırasız kaydedilmiş telemetrinin doğru sıralanıp süre hesaplanması."""
    t1 = pd.Timestamp("2026-10-20 10:00:10")
    t2 = pd.Timestamp("2026-10-20 10:00:00")
    t3 = pd.Timestamp("2026-10-20 10:00:05")

    df = pd.DataFrame({
        "timestamp": [t1, t2, t3],
        "altitude": [150.0, 100.0, 125.0],
        "speed": [15.0, 15.0, 15.0],
        "battery_pct": [80.0, 90.0, 85.0],
        "longitude": [29.0] * 3,
        "latitude": [41.0] * 3,
        "pitch": [0.0] * 3,
        "roll": [0.0] * 3,
        "yaw": [0.0] * 3,
    })
    result = analyzer.analyze(df)
    assert result.total_flight_time_seconds == 10.0
    assert result.min_altitude == 100.0
    assert result.max_altitude == 150.0
