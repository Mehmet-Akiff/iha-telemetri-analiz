import os
import pytest
from data_generator import generate_all_samples
from telemetry_validator import TelemetryValidator

def test_generate_all_samples(tmp_path):
    out_dir = tmp_path / "sample_data"
    files = generate_all_samples(str(out_dir))
    
    assert os.path.exists(files["valid"])
    assert os.path.exists(files["mixed"])
    assert os.path.exists(files["corrupted"])
    assert os.path.exists(files["missing_columns"])
    assert os.path.exists(files["empty"])
    
    validator = TelemetryValidator()
    
    # 1. Valid file validation
    v_res = validator.validate_file(files["valid"])
    assert v_res.is_valid
    assert v_res.valid_rows > 0
    assert v_res.invalid_rows == 0
    
    # 2. Mixed file validation
    m_res = validator.validate_file(files["mixed"])
    assert m_res.is_valid
    assert m_res.valid_rows > 0
    assert m_res.invalid_rows > 0  # contains intentional errors
    
    # 3. Missing columns validation
    mc_res = validator.validate_file(files["missing_columns"])
    assert not mc_res.is_valid
    assert "eksik" in mc_res.fatal_error.lower()
    
    # 4. Empty file validation
    e_res = validator.validate_file(files["empty"])
    assert not e_res.is_valid
    assert "boş" in e_res.fatal_error.lower()
