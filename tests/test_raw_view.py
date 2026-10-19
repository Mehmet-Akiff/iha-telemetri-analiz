import os
import tempfile
import pytest

def read_raw_csv_file(file_path: str, max_chars: int = 500_000) -> dict:
    """
    Telemetri analiz istasyonunda gösterilmek üzere ham CSV dosyasını okur ve dosya metaverilerini üretir.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

    file_size_bytes = os.path.getsize(file_path)

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(max_chars)
        # Eğer okunan karakter sayısı sınıra ulaştıysa ve dosya devam ediyorsa kesilmiştir
        extra_char = f.read(1)
        is_truncated = bool(extra_char)

    line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)

    return {
        "file_name": os.path.basename(file_path),
        "file_size_bytes": file_size_bytes,
        "line_count": line_count,
        "content": content,
        "truncated": is_truncated
    }


def test_read_raw_csv_normal():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f.write("timestamp,altitude,speed\n2026-10-20 14:30:00,100.0,15.0\n2026-10-20 14:30:01,METIN_HATASI,16.0\n")
        f_path = f.name

    try:
        meta = read_raw_csv_file(f_path)
        assert meta["file_name"] == os.path.basename(f_path)
        assert meta["line_count"] == 3
        assert "METIN_HATASI" in meta["content"]
        assert meta["truncated"] is False
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


def test_read_raw_csv_empty():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", encoding="utf-8") as f:
        f_path = f.name

    try:
        meta = read_raw_csv_file(f_path)
        assert meta["line_count"] == 0
        assert meta["file_size_bytes"] == 0
        assert meta["content"] == ""
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


def test_read_raw_csv_nonexistent():
    with pytest.raises(FileNotFoundError):
        read_raw_csv_file("nonexistent_flight_data_99999.csv")
