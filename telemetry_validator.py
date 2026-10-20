"""
telemetry_validator.py
İHA telemetri verilerini yükleme, biçim kontrolü, sınır değer doğrulaması
ve kısmi kurtarma (partial recovery) işlemlerini gerçekleştiren modül.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import os
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "timestamp",
    "altitude",
    "speed",
    "battery_pct",
    "longitude",
    "latitude",
    "pitch",
    "roll",
    "yaw"
]

NUMERIC_COLUMNS = [
    "altitude",
    "speed",
    "battery_pct",
    "longitude",
    "latitude",
    "pitch",
    "roll",
    "yaw"
]

@dataclass
class RowError:
    row: int
    column: str
    message: str
    raw_value: Any

@dataclass
class ValidationResult:
    is_valid: bool
    valid_df: pd.DataFrame
    errors: List[RowError] = field(default_factory=list)
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    fatal_error: Optional[str] = None

class TelemetryValidator:
    """İHA telemetri verilerini doğrulayan ve filtreleyen sınıf."""

    def __init__(self, required_cols: Optional[List[str]] = None):
        self.required_columns = required_cols or REQUIRED_COLUMNS

    def validate_file(self, file_path: str) -> ValidationResult:
        """Belirtilen dosya yolundaki CSV dosyasını okur ve doğrular."""
        if not os.path.exists(file_path):
            return ValidationResult(
                is_valid=False,
                valid_df=pd.DataFrame(),
                fatal_error=f"Dosya bulunamadı: {file_path}"
            )

        if os.path.getsize(file_path) == 0:
            return ValidationResult(
                is_valid=False,
                valid_df=pd.DataFrame(),
                fatal_error="CSV dosyası boş (0 bayt)."
            )

        try:
            # Read CSV with string types initially to avoid silent type coercion
            raw_df = pd.read_csv(file_path, dtype=str, skipinitialspace=True)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                valid_df=pd.DataFrame(),
                fatal_error=f"CSV dosyası okunamadı veya biçimi bozuk: {str(e)}"
            )

        return self.validate_dataframe(raw_df)

    def validate_dataframe(self, df: pd.DataFrame) -> ValidationResult:
        """Verilen DataFrame'i doğrular ve geçerli/hatalı kayıtları ayrıştırır."""
        if df.empty:
            return ValidationResult(
                is_valid=False,
                valid_df=pd.DataFrame(),
                fatal_error="CSV dosyası veri satırı içermemektedir (boş tablo)."
            )

        # 1. Başlık ve zorunlu sütun kontrolü
        df_cols_clean = [str(c).strip().lower() for c in df.columns]
        col_map = {str(c).strip().lower(): c for c in df.columns}
        
        missing_cols = [c for c in self.required_columns if c.lower() not in df_cols_clean]
        if missing_cols:
            return ValidationResult(
                is_valid=False,
                valid_df=pd.DataFrame(),
                fatal_error=f"Gerekli sütunlar eksik: {', '.join(missing_cols)}"
            )

        # Standardize column names to lower case
        rename_dict = {col_map[c.lower()]: c.lower() for c in self.required_columns}
        working_df = df.rename(columns=rename_dict)[self.required_columns].copy()

        errors: List[RowError] = []
        valid_records: List[Dict[str, Any]] = []
        total_rows = len(working_df)

        for idx, row in working_df.iterrows():
            row_num = idx + 2  # 1-indexed Excel/CSV line number (header is row 1)
            row_errors: List[RowError] = []
            parsed_row: Dict[str, Any] = {}

            # 2. Boşluk ve Eksik Değer Kontrolü
            for col in self.required_columns:
                val = row[col]
                if pd.isna(val) or val is None or str(val).strip() == "" or str(val).strip().lower() == "nan":
                    row_errors.append(RowError(
                        row=row_num,
                        column=col,
                        message=f"Zorunlu alan boş bırakılamaz.",
                        raw_value=val
                    ))

            if row_errors:
                errors.extend(row_errors)
                continue

            # 3. Timestamp kontrolü
            raw_ts = str(row["timestamp"]).strip()
            try:
                # Support ISO8601 strings, unix timestamps or standard date formats
                parsed_ts = pd.to_datetime(raw_ts)
                parsed_row["timestamp"] = parsed_ts
            except Exception:
                row_errors.append(RowError(
                    row=row_num,
                    column="timestamp",
                    message="Geçersiz veya çözümlenemeyen zaman damgası.",
                    raw_value=raw_ts
                ))

            # 4. Sayısal alanlar ve sınır değer kontrolleri
            for col in NUMERIC_COLUMNS:
                raw_val = str(row[col]).strip()
                try:
                    num_val = float(raw_val)
                    if np.isnan(num_val) or np.isinf(num_val):
                        raise ValueError("NaN veya Sonsuz sayısal değer.")
                    parsed_row[col] = num_val
                except ValueError:
                    row_errors.append(RowError(
                        row=row_num,
                        column=col,
                        message=f"Sayısal olması gereken alanda geçersiz metin: '{raw_val}'",
                        raw_value=raw_val
                    ))
                    continue

                # Alan spesifik kural kontrolleri
                if col == "altitude" and not (-500.0 <= num_val <= 50000.0):
                    row_errors.append(RowError(
                        row=row_num,
                        column="altitude",
                        message=f"Geçersiz irtifa değeri (-500 m ile 50000 m arası olmalı): {num_val}",
                        raw_value=num_val
                    ))

                elif col == "speed" and num_val < 0:
                    row_errors.append(RowError(
                        row=row_num,
                        column="speed",
                        message=f"Hız negatif olamaz: {num_val}",
                        raw_value=num_val
                    ))

                elif col == "battery_pct" and not (0.0 <= num_val <= 100.0):
                    row_errors.append(RowError(
                        row=row_num,
                        column="battery_pct",
                        message=f"Batarya %0 - %100 aralığı dışında: {num_val}",
                        raw_value=num_val
                    ))

                elif col == "latitude" and not (-90.0 <= num_val <= 90.0):
                    row_errors.append(RowError(
                        row=row_num,
                        column="latitude",
                        message=f"Geçersiz enlem değeri (-90 ile +90 arası olmalı): {num_val}",
                        raw_value=num_val
                    ))

                elif col == "longitude" and not (-180.0 <= num_val <= 180.0):
                    row_errors.append(RowError(
                        row=row_num,
                        column="longitude",
                        message=f"Geçersiz boylam değeri (-180 ile +180 arası olmalı): {num_val}",
                        raw_value=num_val
                    ))

                elif col == "pitch" and not (-180.0 <= num_val <= 180.0):
                    row_errors.append(RowError(
                        row=row_num,
                        column="pitch",
                        message=f"Geçersiz pitch açısı (-180 ile +180 arası olmalı): {num_val}",
                        raw_value=num_val
                    ))

                elif col == "roll" and not (-180.0 <= num_val <= 180.0):
                    row_errors.append(RowError(
                        row=row_num,
                        column="roll",
                        message=f"Geçersiz roll açısı (-180 ile +180 arası olmalı): {num_val}",
                        raw_value=num_val
                    ))

                elif col == "yaw" and not (-360.0 <= num_val <= 360.0):
                    row_errors.append(RowError(
                        row=row_num,
                        column="yaw",
                        message=f"Geçersiz yaw açısı (-360 ile +360 arası olmalı): {num_val}",
                        raw_value=num_val
                    ))

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_records.append(parsed_row)

        valid_df = pd.DataFrame(valid_records)
        valid_count = len(valid_records)
        invalid_count = total_rows - valid_count

        if valid_count == 0:
            return ValidationResult(
                is_valid=False,
                valid_df=valid_df,
                errors=errors,
                total_rows=total_rows,
                valid_rows=0,
                invalid_rows=total_rows,
                fatal_error="Dosya geçerli kayıt içermemektedir (tüm satırlar hatalı)."
            )

        return ValidationResult(
            is_valid=True,
            valid_df=valid_df,
            errors=errors,
            total_rows=total_rows,
            valid_rows=valid_count,
            invalid_rows=invalid_count,
            fatal_error=None
        )
