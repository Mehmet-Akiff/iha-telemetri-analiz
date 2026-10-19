"""
tests/test_scenario_generator.py
Tüm CSV üretim senaryolarını test eden test modülü.
"""

import os
import pytest
import pandas as pd
from data_generator import TelemetryScenarioGenerator, SCENARIO_DESCRIPTIONS
from telemetry_validator import TelemetryValidator

@pytest.fixture
def gen():
    return TelemetryScenarioGenerator()

@pytest.fixture
def validator():
    return TelemetryValidator()

def test_available_scenarios_list(gen):
    scenarios = gen.get_available_scenarios()
    assert len(scenarios) >= 10
    assert "valid" in scenarios
    assert "with_gaps" in scenarios
    assert "mixed" in scenarios
    assert "negative_speed" in scenarios
    assert "battery_bounds" in scenarios

def test_generate_valid_scenario(gen, validator, tmp_path):
    out_file = tmp_path / "test_valid.csv"
    gen.generate_and_save("valid", str(out_file), count=30)
    
    assert os.path.exists(out_file)
    res = validator.validate_file(str(out_file))
    assert res.is_valid is True
    assert res.valid_rows == 30
    assert res.invalid_rows == 0

def test_generate_with_gaps_scenario(gen, validator, tmp_path):
    out_file = tmp_path / "test_gaps.csv"
    gen.generate_and_save("with_gaps", str(out_file), count=25, gap_duration_sec=7.0)
    
    assert os.path.exists(out_file)
    res = validator.validate_file(str(out_file))
    assert res.is_valid is True
    assert res.valid_rows == 25

def test_generate_negative_speed_scenario(gen, validator, tmp_path):
    out_file = tmp_path / "test_neg_spd.csv"
    gen.generate_and_save("negative_speed", str(out_file), count=20)
    
    res = validator.validate_file(str(out_file))
    assert any(err.column == "speed" and "negatif" in err.message.lower() for err in res.errors)

def test_generate_battery_bounds_scenario(gen, validator, tmp_path):
    out_file = tmp_path / "test_bat.csv"
    gen.generate_and_save("battery_bounds", str(out_file), count=20)
    
    res = validator.validate_file(str(out_file))
    assert any(err.column == "battery_pct" for err in res.errors)

def test_generate_missing_columns_scenario(gen, validator, tmp_path):
    out_file = tmp_path / "test_missing_cols.csv"
    gen.generate_and_save("missing_columns", str(out_file))
    
    res = validator.validate_file(str(out_file))
    assert res.is_valid is False
    assert "eksik" in res.fatal_error.lower()

def test_sequence_numbering_and_folder_creation(gen, tmp_path):
    # 1. Boş klasörde ilk numara 1 olmalı
    assert gen.get_next_sequence_number(str(tmp_path)) == 1
    
    # 2. Üretim yapıldığında "Üretilen Klasör 1 - ..." klasörü açılmalı
    folder1, seq1, count1 = gen.generate_numbered_folder(str(tmp_path), mode="temel")
    assert seq1 == 1
    assert count1 == 5  # Temel sette 5 CSV olmalı
    assert os.path.exists(folder1)
    assert "Üretilen Klasör 1" in os.path.basename(folder1)
    
    # 3. İkinci üretimde numara 2 olmalı
    folder2, seq2, count2 = gen.generate_numbered_folder(str(tmp_path), mode="temel")
    assert seq2 == 2
    assert "Üretilen Klasör 2" in os.path.basename(folder2)
    
    # 4. Eğer klasör 1 silinirse, klasördeki en büyük sayı (2) baz alınarak sıradaki 3 olmalı!
    import shutil
    shutil.rmtree(folder1)
    assert not os.path.exists(folder1)
    assert os.path.exists(folder2)
    assert gen.get_next_sequence_number(str(tmp_path)) == 3
    
    folder3, seq3, count3 = gen.generate_numbered_folder(str(tmp_path), mode="tum")
    assert seq3 == 3
    assert count3 == 14
    assert "Üretilen Klasör 3" in os.path.basename(folder3)
    
    # 5. Yeni bir klasöre geçildiğinde sıfırdan 1 ile başlamalı
    new_empty_dir = tmp_path / "yeni_hedef"
    assert gen.get_next_sequence_number(str(new_empty_dir)) == 1


def test_text_error_presence_in_raw_csv(gen):
    # 'mixed' senaryosunda METIN_HATASI yer almalı
    df_mixed, _ = gen.generate_data("mixed", count=20)
    assert any("METIN_HATASI" in str(v) for v in df_mixed["altitude"].tolist())

    # 'text_in_numeric' senaryosunda COK_YUKSEK yer almalı
    df_text, _ = gen.generate_data("text_in_numeric", count=20)
    assert any("COK_YUKSEK" in str(v) for v in df_text["altitude"].tolist())

    # 'valid' senaryosunda ise hiçbir metin hatası olmamalı, tüm irtifalar sayısal olmalı
    df_valid, _ = gen.generate_data("valid", count=20)
    assert all(isinstance(v, (int, float)) for v in df_valid["altitude"].tolist())


