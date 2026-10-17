import io
import os
import pytest
import pandas as pd
from telemetry_validator import TelemetryValidator, ValidationResult, REQUIRED_COLUMNS

def test_missing_required_column(tmp_path):
    csv_file = tmp_path / "missing_col.csv"
    csv_file.write_text("timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll\n"
                        "2026-10-20 12:00:00,100,15,80,29.0,41.0,0,0\n")
    validator = TelemetryValidator()
    result = validator.validate_file(str(csv_file))
    assert not result.is_valid
    assert result.fatal_error is not None
    assert "yaw" in result.fatal_error.lower()

def test_empty_csv(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    validator = TelemetryValidator()
    result = validator.validate_file(str(csv_file))
    assert not result.is_valid
    assert result.fatal_error is not None
    assert "boş" in result.fatal_error.lower() or "empty" in result.fatal_error.lower()

def test_valid_csv(tmp_path):
    csv_file = tmp_path / "valid.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 12:00:00,100.5,15.2,85.0,29.1,41.2,2.1,-1.0,90.5\n"
        "2026-10-20 12:00:01,102.0,15.8,84.8,29.1001,41.2001,2.0,-0.8,91.0\n"
    )
    validator = TelemetryValidator()
    result = validator.validate_file(str(csv_file))
    assert result.is_valid
    assert result.total_rows == 2
    assert result.valid_rows == 2
    assert result.invalid_rows == 0
    assert len(result.errors) == 0
    assert len(result.valid_df) == 2

def test_row_validations_and_partial_recovery(tmp_path):
    # Contains:
    # Row 1: valid
    # Row 2: negative speed (-5)
    # Row 3: battery > 100 (105)
    # Row 4: battery < 0 (-10)
    # Row 5: latitude > 90 (95)
    # Row 6: longitude < -180 (-190)
    # Row 7: non-numeric altitude ('high')
    # Row 8: empty speed ('')
    # Row 9: unparseable timestamp ('not-a-date')
    # Row 10: valid
    csv_file = tmp_path / "mixed.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 12:00:00,100,15,80,29.0,41.0,0,0,0\n"
        "2026-10-20 12:00:01,100,-5,80,29.0,41.0,0,0,0\n"
        "2026-10-20 12:00:02,100,15,105,29.0,41.0,0,0,0\n"
        "2026-10-20 12:00:03,100,15,-10,29.0,41.0,0,0,0\n"
        "2026-10-20 12:00:04,100,15,80,29.0,95.0,0,0,0\n"
        "2026-10-20 12:00:05,100,15,80,-195.0,41.0,0,0,0\n"
        "2026-10-20 12:00:06,high,15,80,29.0,41.0,0,0,0\n"
        "2026-10-20 12:00:07,100,,80,29.0,41.0,0,0,0\n"
        "2026-10-20 12:00:08,100,15,80,29.0,41.0,0,0,0\n"
        "corrupted-timestamp,100,15,80,29.0,41.0,0,0,0\n"
    )
    validator = TelemetryValidator()
    result = validator.validate_file(str(csv_file))
    
    # Partial recovery: valid rows (Row 1, 9) must be kept
    assert result.is_valid
    assert result.valid_rows == 2
    assert result.invalid_rows == 8
    assert len(result.errors) == 8
    assert len(result.valid_df) == 2

def test_zero_valid_records(tmp_path):
    csv_file = tmp_path / "all_bad.csv"
    csv_file.write_text(
        "timestamp,altitude,speed,battery_pct,longitude,latitude,pitch,roll,yaw\n"
        "2026-10-20 12:00:01,100,-5,80,29.0,41.0,0,0,0\n"
        "2026-10-20 12:00:02,100,15,120,29.0,41.0,0,0,0\n"
    )
    validator = TelemetryValidator()
    result = validator.validate_file(str(csv_file))
    assert not result.is_valid
    assert result.valid_rows == 0
    assert result.invalid_rows == 2
    assert "geçerli kayıt içermemektedir" in result.fatal_error.lower() or "no valid" in result.fatal_error.lower()
