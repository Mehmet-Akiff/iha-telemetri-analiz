"""
telemetry_analyzer.py
Doğrulanmış İHA telemetri verileri üzerinden istatistiksel analizler
ve olağan dışı zaman damgası boşluklarını (time gap anomaly) tespit eden modül.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np

@dataclass
class TimestampGap:
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    gap_seconds: float
    start_index: int
    end_index: int

@dataclass
class AnalysisResult:
    avg_altitude: float
    min_altitude: float
    max_altitude: float
    avg_speed: float
    min_battery: float
    total_flight_time_seconds: float
    data_points_count: int
    gap_threshold_seconds: float
    timestamp_gaps: List[TimestampGap] = field(default_factory=list)

    @property
    def has_gaps(self) -> bool:
        return len(self.timestamp_gaps) > 0

class TelemetryAnalyzer:
    """İHA telemetri verilerini analiz eden motor sınıfı."""

    def __init__(self, gap_threshold_seconds: float = 3.0):
        """
        gap_threshold_seconds: Ardışık kayıtlar arasında veri kaybı/kesinti
        sayılacak zaman farkı eşiği (varsayılan: 3.0 saniye).
        """
        self.gap_threshold_seconds = gap_threshold_seconds

    def analyze(self, df: pd.DataFrame, gap_threshold_seconds: Optional[float] = None) -> AnalysisResult:
        """
        Doğrulanmış telemetri DataFrame'i üzerinde analiz yapar.
        """
        if df is None or df.empty:
            raise ValueError("Analiz için geçerli veri bulunamadı (DataFrame boş).")

        threshold = gap_threshold_seconds if gap_threshold_seconds is not None else self.gap_threshold_seconds

        # Ensure timestamp is datetime and sort chronologically
        working_df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(working_df["timestamp"]):
            working_df["timestamp"] = pd.to_datetime(working_df["timestamp"])

        working_df = working_df.sort_values(by="timestamp").reset_index(drop=True)

        avg_alt = float(working_df["altitude"].mean())
        min_alt = float(working_df["altitude"].min())
        max_alt = float(working_df["altitude"].max())
        avg_spd = float(working_df["speed"].mean())
        min_bat = float(working_df["battery_pct"].min())

        data_count = len(working_df)
        if data_count > 1:
            total_flight_time = float(
                (working_df["timestamp"].iloc[-1] - working_df["timestamp"].iloc[0]).total_seconds()
            )
        else:
            total_flight_time = 0.0

        # Zaman boşluklarını (Time Gaps) tespit et
        gaps: List[TimestampGap] = []
        if data_count > 1:
            diffs = working_df["timestamp"].diff().dt.total_seconds()
            for i in range(1, data_count):
                delta = diffs.iloc[i]
                if delta > threshold:
                    gaps.append(TimestampGap(
                        start_time=working_df["timestamp"].iloc[i - 1],
                        end_time=working_df["timestamp"].iloc[i],
                        gap_seconds=float(delta),
                        start_index=i - 1,
                        end_index=i
                    ))

        return AnalysisResult(
            avg_altitude=round(avg_alt, 2),
            min_altitude=round(min_alt, 2),
            max_altitude=round(max_alt, 2),
            avg_speed=round(avg_spd, 2),
            min_battery=round(min_bat, 2),
            total_flight_time_seconds=round(total_flight_time, 2),
            data_points_count=data_count,
            gap_threshold_seconds=threshold,
            timestamp_gaps=gaps
        )
