"""
generator_gui.py
Geriye dönük uyumluluk başlatıcısı — doğrudan csv_senaryo_uretici/app.py (v1.6.0)
içerisindeki güncel CSVGeneratorApp masaüstü uygulamasını başlatır.
"""

import os
import sys

_SUB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv_senaryo_uretici")
if _SUB_DIR not in sys.path:
    sys.path.insert(0, _SUB_DIR)

from app import CSVGeneratorApp

if __name__ == "__main__":
    app = CSVGeneratorApp()
    app.mainloop()
