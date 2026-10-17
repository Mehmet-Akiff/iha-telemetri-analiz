import pytest
import pandas as pd
from datetime import datetime, timedelta
from telemetry_analyzer import TelemetryAnalyzer, AnalysisResult, TimestampGap

def test_analyzer_calculations():
    # 5 timestamps with 1 second intervals, except one gap of 10 seconds
    base_time = datetime(2026, 10, 20, 12, 0, 0)
    times = [
        base_time,
        base_time + timedelta(seconds=1),
        base_time + timedelta(seconds=2),
        base_time + timedelta(seconds=12),  # 10s gap
        base_time + timedelta(seconds=13),
    ]
    
    df = pd.DataFrame({
        "timestamp": times,
        "altitude": [100.0, 110.0, 120.0, 130.0, 140.0],
        "speed": [10.0, 15.0, 20.0, 25.0, 30.0],
        "battery_pct": [95.0, 94.0, 92.0, 90.0, 88.0],
        "longitude": [29.0] * 5,
        "latitude": [41.0] * 5,
        "pitch": [0.0] * 5,
        "roll": [0.0] * 5,
        "yaw": [0.0] * 5,
    })
    
    analyzer = TelemetryAnalyzer(gap_threshold_seconds=3.0)
    result = analyzer.analyze(df)
    
    # Check metrics
    assert result.avg_altitude == pytest.approx(120.0)
    assert result.min_altitude == pytest.approx(100.0)
    assert result.max_altitude == pytest.approx(140.0)
    assert result.avg_speed == pytest.approx(20.0)
    assert result.min_battery == pytest.approx(88.0)
    assert result.data_points_count == 5
    assert result.total_flight_time_seconds == pytest.approx(13.0)
    
    # Check gap detection
    assert result.has_gaps is True
    assert len(result.timestamp_gaps) == 1
    gap = result.timestamp_gaps[0]
    assert gap.gap_seconds == pytest.approx(10.0)
    assert gap.start_time == pd.Timestamp(times[2])
    assert gap.end_time == pd.Timestamp(times[3])

def test_analyzer_unsorted_timestamps():
    # Timestamps provided out of order
    base_time = datetime(2026, 10, 20, 12, 0, 0)
    times = [
        base_time + timedelta(seconds=10),
        base_time,
        base_time + timedelta(seconds=5),
    ]
    df = pd.DataFrame({
        "timestamp": times,
        "altitude": [150.0, 100.0, 125.0],
        "speed": [10.0, 10.0, 10.0],
        "battery_pct": [80.0, 90.0, 85.0],
        "longitude": [29.0] * 3,
        "latitude": [41.0] * 3,
        "pitch": [0.0] * 3,
        "roll": [0.0] * 3,
        "yaw": [0.0] * 3,
    })
    
    analyzer = TelemetryAnalyzer(gap_threshold_seconds=4.0)
    result = analyzer.analyze(df)
    
    assert result.min_altitude == 100.0
    assert result.max_altitude == 150.0
    # Between 0s and 5s -> gap 5s (>4s). Between 5s and 10s -> gap 5s (>4s).
    assert len(result.timestamp_gaps) == 2

def test_analyzer_empty_df():
    analyzer = TelemetryAnalyzer()
    with pytest.raises(ValueError, match="geçerli veri bulunamadı|empty"):
        analyzer.analyze(pd.DataFrame())
