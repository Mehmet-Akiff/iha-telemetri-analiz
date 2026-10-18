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
