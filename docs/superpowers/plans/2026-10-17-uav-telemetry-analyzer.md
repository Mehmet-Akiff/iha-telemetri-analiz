# İHA Telemetri Analiz ve Görselleştirme Uygulaması Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Python ve CustomTkinter/Matplotlib kullanarak CSV telemetri verilerini okuyan, doğrulayan, kısmi kurtarma yapan, analiz eden, zaman serisi grafikleri çizen ve kapsamlı testleri olan masaüstü uygulamasını inşa etmek.

**Architecture:** Modüler katmanlı mimari; `telemetry_validator.py` (doğrulama ve veri temizleme), `telemetry_analyzer.py` (istatistik ve zaman boşluğu analizi), `data_generator.py` (sentetik veri ve sınır durumu üretimi), `gui_app.py` (modern masaüstü arayüzü), `tests/test_telemetry.py` (15 adet kapsamlı birim ve entegrasyon testi).

**Tech Stack:** Python 3.12, CustomTkinter, Matplotlib, Pandas, NumPy, Pytest.

**Spec:** `docs/superpowers/specs/2026-10-17-uav-telemetry-analyzer-design.md`

## Global Constraints
- Sütun isimleri: `timestamp`, `altitude`, `speed`, `battery_pct`, `longitude`, `latitude`, `pitch`, `roll`, `yaw`.
- `speed >= 0` olmalıdır.
- `0 <= battery_pct <= 100` olmalıdır.
- `-90 <= latitude <= 90` ve `-180 <= longitude <= 180` olmalıdır.
- Hatalı satırlar geçerli satırların işlenmesini durdurmamalı (kısmi kurtarma), ancak hangi satırın ne sebeple reddedildiği raporlanmalıdır.
- Pytest ile tüm testler %100 başarıyla geçmelidir.

---

### Task 1: Telemetry Validator Engine (`telemetry_validator.py`)
**Files:**
- Create: `telemetry_validator.py`
- Test: `tests/test_validator.py`

**Interfaces:**
- Consumes: CSV file path or file-like object
- Produces: `ValidationResult` (dataclass with fields `valid_df: pd.DataFrame`, `errors: List[dict]`, `total_rows: int`, `valid_rows: int`, `invalid_rows: int`, `error_message: Optional[str]`)

- [ ] **Step 1: Write failing tests for validation logic**
  Tests covering:
  - Missing column detection
  - Empty field detection
  - Non-numeric conversion error
  - Negative speed
  - Battery out of bounds (<0, >100)
  - Latitude/longitude out of bounds
  - Timestamp parse error
  - Empty file / unparseable CSV
  - Partial recovery (retaining valid rows while rejecting bad rows)

- [ ] **Step 2: Run tests to verify failure**
  Run: `pytest tests/test_validator.py -v`

- [ ] **Step 3: Implement `telemetry_validator.py`**
  Implement `TelemetryValidator` and `ValidationResult`.

- [ ] **Step 4: Run tests to verify pass**
  Run: `pytest tests/test_validator.py -v`

- [ ] **Step 5: Git commit**
  Commit task 1.

---

### Task 2: Telemetry Analyzer Engine (`telemetry_analyzer.py`)
**Files:**
- Create: `telemetry_analyzer.py`
- Test: `tests/test_analyzer.py`

**Interfaces:**
- Consumes: Valid telemetry `pandas.DataFrame` from Task 1, optional `gap_threshold_sec: float` (default 3.0)
- Produces: `AnalysisResult` dataclass with `avg_altitude`, `min_altitude`, `max_altitude`, `avg_speed`, `min_battery`, `total_flight_time_sec`, `timestamp_gaps: List[dict]`

- [ ] **Step 1: Write failing tests for analyzer**
  Tests covering:
  - Altitude min, max, avg calculations
  - Speed average calculation
  - Battery minimum
  - Detection of abnormal timestamp gaps (> threshold)
  - Chronological sorting of timestamps before gap calculation
  - Handling of edge cases (single record, zero valid records)

- [ ] **Step 2: Run tests to verify failure**
  Run: `pytest tests/test_analyzer.py -v`

- [ ] **Step 3: Implement `telemetry_analyzer.py`**
  Implement `TelemetryAnalyzer` and `AnalysisResult`.

- [ ] **Step 4: Run tests to verify pass**
  Run: `pytest tests/test_analyzer.py -v`

- [ ] **Step 5: Git commit**
  Commit task 2.

---

### Task 3: Sample Data Generator (`data_generator.py`)
**Files:**
- Create: `data_generator.py`
- Test: `tests/test_data_generator.py`

**Interfaces:**
- Consumes: Output directory path
- Produces: Generates sample CSV files (`telemetry_valid.csv`, `telemetry_mixed.csv`, `telemetry_corrupted.csv`, `telemetry_missing_columns.csv`, `telemetry_empty.csv`)

- [ ] **Step 1: Write failing tests for data generator**
- [ ] **Step 2: Run tests to verify failure**
- [ ] **Step 3: Implement `data_generator.py`**
- [ ] **Step 4: Run tests to verify pass**
- [ ] **Step 5: Git commit**

---

### Task 4: Complete Consolidated Pytest Suite (`tests/test_telemetry.py`)
**Files:**
- Create: `tests/test_telemetry.py`

- [ ] **Step 1: Implement full test suite matching all 10 PDF scenarios + 5 extra scenarios**
- [ ] **Step 2: Run all tests with pytest and verify 100% pass rate**
- [ ] **Step 3: Git commit**

---

### Task 5: Desktop GUI Application (`gui_app.py`)
**Files:**
- Create: `gui_app.py`

**Features:**
- CustomTkinter modern UI with dark mode
- File picker dialog
- Analyze button and configurable gap threshold entry
- Summary KPI metric cards
- Embedded Matplotlib time-series plots (Altitude, Speed, Battery with gap highlight overlays)
- Valid data Treeview table
- Error and rejected rows Treeview table
- Information and error popup dialogs
- "Generate Sample CSV" action button

- [ ] **Step 1: Implement `gui_app.py`**
- [ ] **Step 2: Verify GUI startup in headless/test mode or via integration run**
- [ ] **Step 3: Git commit**

---

### Task 6: Technical Report and Documentation (`README.md` & `TEKNIK_RAPOR.md`)
**Files:**
- Create: `README.md`
- Create: `TEKNIK_RAPOR.md`

- [ ] **Step 1: Write `README.md` with usage, installation, and test commands**
- [ ] **Step 2: Write `TEKNIK_RAPOR.md` covering parameter definitions, library rationales, timestamp threshold justification**
- [ ] **Step 3: Git commit**
