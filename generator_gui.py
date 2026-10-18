"""
generator_gui.py
İHA Telemetri CSV Senaryo Üretici Masaüstü Uygulaması.
Tüm test ve sınır senaryolarını seçip özelleştirilmiş CSV üreten arayüz.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import pandas as pd

from data_generator import TelemetryScenarioGenerator, SCENARIO_DESCRIPTIONS

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class CSVGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("İHA Telemetri CSV Senaryo Üretici İstasyonu")
        self.geometry("1180x820")
        self.minsize(980, 700)

        self.generator = TelemetryScenarioGenerator()
        self.current_df = None
        self.current_raw = None

        self._build_ui()

    def _build_ui(self):
        # 1. Üst Başlık
        top_frame = ctk.CTkFrame(self, corner_radius=10)
        top_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_lbl = ctk.CTkLabel(
            top_frame,
            text="🧪 İHA Telemetri CSV Senaryo Üretici",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_lbl.pack(side="left", padx=15, pady=12)

        subtitle_lbl = ctk.CTkLabel(
            top_frame,
            text="Test ve analiz için 14 farklı uçuş ve hata senaryosu oluşturun",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_lbl.pack(side="left", padx=10, pady=12)

        # 2. Ana Gövde (Sol: Ayarlar, Sağ: Veri Önizleme)
        main_content = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Sol Panel (Kontroller ve Parametreler)
        left_panel = ctk.CTkFrame(main_content, width=420, corner_radius=10)
        left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        left_panel.pack_propagate(False)

        # Senaryo Seçimi
        ctk.CTkLabel(left_panel, text="📌 Senaryo Seçimi:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))

        self.scenario_keys = list(SCENARIO_DESCRIPTIONS.keys())
        self.scenario_values = list(SCENARIO_DESCRIPTIONS.values())

        self.combo_scenarios = ctk.CTkComboBox(
            left_panel,
            values=self.scenario_values,
            width=380,
            command=self._on_scenario_changed
        )
        self.combo_scenarios.set(self.scenario_values[0])
        self.combo_scenarios.pack(padx=15, pady=5)

        self.lbl_scenario_desc = ctk.CTkLabel(
            left_panel,
            text="Seçili senaryo açıklaması burada görünecek.",
            font=ctk.CTkFont(size=11),
            text_color="#ced4da",
            wraplength=380,
            justify="left"
        )
        self.lbl_scenario_desc.pack(anchor="w", padx=15, pady=(2, 15))

        # Parametreler Bölümü
        ctk.CTkLabel(left_panel, text="⚙️ Parametre Ayarları:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(5, 5))

        # Kayıt Sayısı
        p_row1 = ctk.CTkFrame(left_panel, fg_color="transparent")
        p_row1.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(p_row1, text="Kayıt Sayısı (Satır):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.entry_count = ctk.CTkEntry(p_row1, width=80)
        self.entry_count.insert(0, "60")
        self.entry_count.pack(side="right")

        # Zaman Boşluğu Süresi (sn)
        p_row2 = ctk.CTkFrame(left_panel, fg_color="transparent")
        p_row2.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(p_row2, text="Kesinti Süresi (sn):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.entry_gap = ctk.CTkEntry(p_row2, width=80)
        self.entry_gap.insert(0, "8.0")
        self.entry_gap.pack(side="right")

        # Başlangıç İrtifası
        p_row3 = ctk.CTkFrame(left_panel, fg_color="transparent")
        p_row3.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(p_row3, text="Başlangıç İrtifası (m):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.entry_alt = ctk.CTkEntry(p_row3, width=80)
        self.entry_alt.insert(0, "50.0")
        self.entry_alt.pack(side="right")

        # Başlangıç Hızı
        p_row4 = ctk.CTkFrame(left_panel, fg_color="transparent")
        p_row4.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(p_row4, text="Başlangıç Hızı (m/s):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.entry_spd = ctk.CTkEntry(p_row4, width=80)
        self.entry_spd.insert(0, "15.0")
        self.entry_spd.pack(side="right")

        # Başlangıç Bataryası
        p_row5 = ctk.CTkFrame(left_panel, fg_color="transparent")
        p_row5.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(p_row5, text="Başlangıç Bataryası (%):", font=ctk.CTkFont(size=12)).pack(side="left")
        self.entry_bat = ctk.CTkEntry(p_row5, width=80)
        self.entry_bat.insert(0, "100.0")
        self.entry_bat.pack(side="right")

        # Aksiyon Butonları
        ctk.CTkLabel(left_panel, text="🚀 İşlemler:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(20, 5))

        self.btn_preview = ctk.CTkButton(
            left_panel,
            text="👁️ Veriyi Canlı Önizle",
            command=self.preview_data_action,
            fg_color="#1971c2",
            hover_color="#1864ab",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_preview.pack(fill="x", padx=15, pady=6)

        self.btn_save_csv = ctk.CTkButton(
            left_panel,
            text="💾 CSV Olarak Farklı Kaydet",
            command=self.save_csv_action,
            fg_color="#2b8a3e",
            hover_color="#237032",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_save_csv.pack(fill="x", padx=15, pady=6)

        self.btn_open_samples = ctk.CTkButton(
            left_panel,
            text="📁 Örnekler Klasörünü Aç",
            command=self.open_samples_folder,
            fg_color="#495057",
            hover_color="#343a40"
        )
        self.btn_open_samples.pack(fill="x", padx=15, pady=6)

        self.btn_launch_analyzer = ctk.CTkButton(
            left_panel,
            text="🛸 Telemetri Analiz İstasyonunu Aç",
            command=self.launch_analyzer_app,
            fg_color="#f08c00",
            hover_color="#e67700",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_launch_analyzer.pack(fill="x", padx=15, pady=(15, 10))

        # Sağ Panel (Tablo Önizleme)
        right_panel = ctk.CTkFrame(main_content, corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        preview_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        preview_header.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(
            preview_header,
            text="📊 Oluşturulan Veri Önizlemesi",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left")

        self.lbl_stats = ctk.CTkLabel(
            preview_header,
            text="Önizleme hazır değil",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.lbl_stats.pack(side="right")

        # Treeview Tablosu
        table_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.columns = ("timestamp", "altitude", "speed", "battery_pct", "longitude", "latitude", "pitch", "roll", "yaw")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#212529", foreground="white", fieldbackground="#212529", rowheight=24)
        style.configure("Treeview.Heading", background="#343a40", foreground="white", font=('Helvetica', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#2b8a3e')])

        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # İlk senaryo bilgisini yükle ve otomatik önizle
        self._on_scenario_changed(self.combo_scenarios.get())
        self.preview_data_action()

    def _get_selected_scenario_key(self) -> str:
        idx = self.combo_scenarios.cget("values").index(self.combo_scenarios.get())
        return self.scenario_keys[idx]

    def _on_scenario_changed(self, choice):
        key = self._get_selected_scenario_key()
        desc = SCENARIO_DESCRIPTIONS.get(key, "")
        self.lbl_scenario_desc.configure(text=f"Açıklama: {desc}")

    def _read_params(self):
        try:
            count = int(self.entry_count.get().strip())
            gap = float(self.entry_gap.get().strip())
            alt = float(self.entry_alt.get().strip())
            spd = float(self.entry_spd.get().strip())
            bat = float(self.entry_bat.get().strip())
            if count <= 0:
                raise ValueError
            return count, gap, alt, spd, bat
        except Exception:
            messagebox.showerror("Hatalı Giriş", "Lütfen tüm parametre alanlarına geçerli sayısal değerler giriniz!")
            return None

    def preview_data_action(self):
        """Seçili senaryoya göre veriyi üretir ve tabloda önizler."""
        params = self._read_params()
        if not params:
            return

        count, gap, alt, spd, bat = params
        key = self._get_selected_scenario_key()

        df, raw = self.generator.generate_data(
            scenario_key=key,
            count=count,
            gap_duration_sec=gap,
            initial_altitude=alt,
            initial_speed=spd,
            initial_battery=bat
        )
        self.current_df = df
        self.current_raw = raw

        # Tabloyu temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        if df is not None and not df.empty:
            for _, row in df.iterrows():
                vals = [row.get(col, "") for col in self.columns]
                self.tree.insert("", "end", values=vals)
            self.lbl_stats.configure(
                text=f"{len(df)} kayıt üretildi • Durum: Önizleme Hazır",
                text_color="#51cf66"
            )
        elif raw is not None:
            self.lbl_stats.configure(
                text="Özel Ham/Bozuk Metin Formatı (Boş veya Bozuk Dosya)",
                text_color="#ff6b6b"
            )
        else:
            self.lbl_stats.configure(
                text="0 Bayt Boş Dosya Senaryosu",
                text_color="#fcc419"
            )

    def save_csv_action(self):
        """Kullanıcının belirleyeceği konuma CSV dosyasını kaydeder."""
        params = self._read_params()
        if not params:
            return

        count, gap, alt, spd, bat = params
        key = self._get_selected_scenario_key()

        default_filename = f"telemetry_{key}.csv"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV Dosyaları", "*.csv"), ("Tüm Dosyalar", "*.*")]
        )
        if not file_path:
            return

        try:
            self.generator.generate_and_save(
                scenario_key=key,
                output_file_path=file_path,
                count=count,
                gap_duration_sec=gap,
                initial_altitude=alt,
                initial_speed=spd,
                initial_battery=bat
            )
            messagebox.showinfo(
                "Kayıt Başarılı",
                f"CSV dosyası başarıyla kaydedildi:\n\n{file_path}\n\nArtık bu dosyayı 'İHA Telemetri Analiz İstasyonu' üzerinden test edebilirsiniz."
            )
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")

    def open_samples_folder(self):
        """Örneklerin bulunduğu klasörü Windows Gezgini'nde açar."""
        sample_dir = os.path.abspath("samples")
        if not os.path.exists(sample_dir):
            os.makedirs(sample_dir, exist_ok=True)
        os.startfile(sample_dir)

    def launch_analyzer_app(self):
        """Ana Telemetri Analiz uygulamasını başlatır."""
        script_path = os.path.abspath("gui_app.py")
        subprocess.Popen([sys.executable, script_path])

if __name__ == "__main__":
    app = CSVGeneratorApp()
    app.mainloop()
