"""
gui_app.py
İHA Telemetri Analiz ve Görselleştirme Masaüstü Uygulaması (v1.2.0).
CustomTkinter ve Matplotlib tabanlı modern kullanıcı arayüzü.
Açılış ekranı (splash screen), ikon, animasyonlu sayaçlar ve sayfa geçişleri.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# PyInstaller Açılış Ekranı (Splash Screen) Kapatıcı
try:
    import pyi_splash
    pyi_splash.update_text("Telemetri arayüzü başlatılıyor...")
except ImportError:
    pyi_splash = None

from telemetry_validator import TelemetryValidator, ValidationResult
from telemetry_analyzer import TelemetryAnalyzer, AnalysisResult

# Uygulama Tema Ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def get_resource_path(relative_path: str) -> str:
    """PyInstaller veya normal çalışmada kaynak dosya yolunu döndürür."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class TelemetryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("İHA Telemetri Analiz İstasyonu v1.2.0")
        self.geometry("1280x860")
        self.minsize(1050, 720)

        # İkon Ayarla
        icon_path = get_resource_path(os.path.join("assets", "telemetry_icon.ico"))
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.validator = TelemetryValidator()
        self.analyzer = TelemetryAnalyzer(gap_threshold_seconds=3.0)

        self.current_file_path = None
        self.current_validation: ValidationResult = None
        self.current_analysis: AnalysisResult = None

        self._build_ui()

        # Splash ekranını kapat
        if pyi_splash is not None:
            try:
                pyi_splash.close()
            except Exception:
                pass

    def _build_ui(self):
        # 1. Üst Başlık ve Kontrol Çubuğu (CSV Üret Butonu Kaldırıldı)
        top_frame = ctk.CTkFrame(self, corner_radius=10)
        top_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_label = ctk.CTkLabel(
            top_frame,
            text="🛸 İHA Telemetri Analiz İstasyonu",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=15, pady=12)

        self.btn_select_file = ctk.CTkButton(
            top_frame,
            text="📂 CSV Dosyası Seç",
            command=self.select_file,
            width=140,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_select_file.pack(side="left", padx=10, pady=12)

        self.lbl_file_path = ctk.CTkLabel(
            top_frame,
            text="Analiz edilecek CSV dosyasını seçiniz...",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )
        self.lbl_file_path.pack(side="left", padx=10, fill="x", expand=True)

        lbl_threshold = ctk.CTkLabel(top_frame, text="Zaman Boşluğu Eşiği (sn):", font=ctk.CTkFont(size=12))
        lbl_threshold.pack(side="left", padx=(10, 5))

        self.entry_threshold = ctk.CTkEntry(top_frame, width=60)
        self.entry_threshold.insert(0, "3.0")
        self.entry_threshold.pack(side="left", padx=5)

        self.btn_analyze = ctk.CTkButton(
            top_frame,
            text="⚙️ Analiz Et",
            command=self.run_analysis,
            fg_color="#2b8a3e",
            hover_color="#237032",
            width=120,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_analyze.pack(side="left", padx=(10, 15), pady=12)

        # 2. Özet KPI Kartları
        self.kpi_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.cards = {}
        card_configs = [
            ("total_records", "Toplam / Geçerli Kayıt", "- / -"),
            ("error_count", "Hatalı Kayıt Sayısı", "-"),
            ("avg_altitude", "Ortalama İrtifa", "- m"),
            ("min_max_altitude", "Min / Maks İrtifa", "- / - m"),
            ("avg_speed", "Ortalama Hız", "- m/s"),
            ("min_battery", "Min Batarya", "- %"),
            ("gaps_detected", "Tespit Edilen Boşluk", "- adet"),
        ]

        for i, (key, title, default_val) in enumerate(card_configs):
            card = ctk.CTkFrame(self.kpi_frame, corner_radius=8)
            card.pack(side="left", fill="both", expand=True, padx=4)

            t_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#adb5bd")
            t_lbl.pack(padx=8, pady=(8, 2))

            v_lbl = ctk.CTkLabel(card, text=default_val, font=ctk.CTkFont(size=14, weight="bold"))
            v_lbl.pack(padx=8, pady=(0, 8))

            self.cards[key] = v_lbl

        # 3. Sekmeli Ana Bölüm (Sayfa Geçiş Animasyonu Desteği)
        self.tabview = ctk.CTkTabview(self, corner_radius=10, command=self._on_tab_switched)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_charts = self.tabview.add("📈 Telemetri Grafikleri")
        self.tab_table = self.tabview.add("📋 Geçerli Veri Tablosu")
        self.tab_errors = self.tabview.add("⚠️ Hatalı Kayıtlar Raporu")

        self._setup_charts_tab()
        self._setup_table_tab()
        self._setup_errors_tab()

    def _setup_charts_tab(self):
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.fig.patch.set_facecolor("#212529")

        self.ax_alt = self.fig.add_subplot(3, 1, 1)
        self.ax_spd = self.fig.add_subplot(3, 1, 2, sharex=self.ax_alt)
        self.ax_bat = self.fig.add_subplot(3, 1, 3, sharex=self.ax_alt)

        self._style_axis(self.ax_alt, "İrtifa (Altitude) [m]", "#4dabf7")
        self._style_axis(self.ax_spd, "Hız (Speed) [m/s]", "#69db7c")
        self._style_axis(self.ax_bat, "Batarya Seviyesi [%]", "#ffa94d")

        self.fig.tight_layout(pad=2.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_charts)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _style_axis(self, ax, title, color):
        ax.set_facecolor("#1a1a1a")
        ax.set_title(title, color="white", fontsize=11, fontweight="bold", pad=5)
        ax.tick_params(colors="lightgray", labelsize=8)
        ax.grid(True, color="#343a40", linestyle="--", linewidth=0.7)
        for spine in ax.spines.values():
            spine.set_color("#495057")

    def _setup_table_tab(self):
        frame = ctk.CTkFrame(self.tab_table, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("timestamp", "altitude", "speed", "battery_pct", "longitude", "latitude", "pitch", "roll", "yaw")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#212529", foreground="white", fieldbackground="#212529", rowheight=24)
        style.configure("Treeview.Heading", background="#343a40", foreground="white", font=('Helvetica', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#1971c2')])

        self.tree_valid = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree_valid.heading(col, text=col)
            self.tree_valid.column(col, width=110, anchor="center")

        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=self.tree_valid.yview)
        scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=self.tree_valid.xview)
        self.tree_valid.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree_valid.pack(side="left", fill="both", expand=True)

    def _setup_errors_tab(self):
        frame = ctk.CTkFrame(self.tab_errors, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("row", "column", "message", "raw_value")
        self.tree_errors = ttk.Treeview(frame, columns=columns, show="headings")
        
        self.tree_errors.heading("row", text="Satır No")
        self.tree_errors.heading("column", text="Hatalı Sütun")
        self.tree_errors.heading("message", text="Red Nedeni / Açıklama")
        self.tree_errors.heading("raw_value", text="Girilen Geçersiz Değer")

        self.tree_errors.column("row", width=80, anchor="center")
        self.tree_errors.column("column", width=120, anchor="center")
        self.tree_errors.column("message", width=450, anchor="w")
        self.tree_errors.column("raw_value", width=160, anchor="center")

        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=self.tree_errors.yview)
        scroll_x = ttk.Scrollbar(frame, orient="horizontal", command=self.tree_errors.xview)
        self.tree_errors.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree_errors.pack(side="left", fill="both", expand=True)

    def _on_tab_switched(self):
        """Sayfa geçişlerinde hafif yumuşak geçiş (smooth transition) efekti."""
        current_tab = self.tabview.get()
        if "Grafik" in current_tab and hasattr(self, "canvas"):
            self.canvas.draw_idle()

    def _animate_number(self, card_key: str, start: float, end: float, unit: str = "", steps: int = 10, is_int: bool = False):
        """Metrik kartındaki sayıyı profesyonel sayaç animasyonuyla artırır."""
        def step(current_step):
            if current_step >= steps:
                if is_int:
                    self.cards[card_key].configure(text=f"{int(end)} {unit}".strip())
                else:
                    self.cards[card_key].configure(text=f"{end:.1f} {unit}".strip())
                return
            progress = current_step / steps
            current_val = start + (end - start) * progress
            if is_int:
                self.cards[card_key].configure(text=f"{int(current_val)} {unit}".strip())
            else:
                self.cards[card_key].configure(text=f"{current_val:.1f} {unit}".strip())
            self.after(18, step, current_step + 1)
        step(1)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Telemetri CSV Dosyası Seçin",
            filetypes=[("CSV Dosyaları", "*.csv"), ("Tüm Dosyalar", "*.*")]
        )
        if file_path:
            self.current_file_path = file_path
            self.lbl_file_path.configure(text=os.path.basename(file_path), text_color="white")

    def run_analysis(self):
        if not self.current_file_path:
            messagebox.showwarning(
                "Dosya Seçilmedi",
                "Lütfen analiz başlatmadan önce geçerli bir telemetri CSV dosyası seçiniz."
            )
            return

        try:
            threshold = float(self.entry_threshold.get().strip())
            if threshold <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Geçersiz Eşik",
                "Zaman boşluğu eşiği pozitif bir sayı olmalıdır (Örn: 3.0)."
            )
            return

        result = self.validator.validate_file(self.current_file_path)
        self.current_validation = result

        for item in self.tree_errors.get_children():
            self.tree_errors.delete(item)

        for err in result.errors:
            self.tree_errors.insert("", "end", values=(err.row, err.column, err.message, err.raw_value))

        if not result.is_valid:
            self._reset_kpi_and_views()
            messagebox.showerror(
                "Doğrulama / Yükleme Hatası",
                f"Dosya işlenemedi!\n\nNeden: {result.fatal_error}"
            )
            return

        try:
            analysis = self.analyzer.analyze(result.valid_df, gap_threshold_seconds=threshold)
            self.current_analysis = analysis
        except Exception as e:
            messagebox.showerror(
                "Analiz Hatası",
                f"Telemetri analizi sırasında beklenmeyen hata oluştu:\n{str(e)}"
            )
            return

        # KPI Kartlarını Sayaç Animasyonu ile Güncelle
        self.cards["total_records"].configure(text=f"{result.total_rows} / {result.valid_rows}")
        self.cards["error_count"].configure(
            text=f"{result.invalid_rows}",
            text_color="#ff6b6b" if result.invalid_rows > 0 else "#51cf66"
        )
        self._animate_number("avg_altitude", 0.0, analysis.avg_altitude, unit="m")
        self.cards["min_max_altitude"].configure(text=f"{analysis.min_altitude} / {analysis.max_altitude} m")
        self._animate_number("avg_speed", 0.0, analysis.avg_speed, unit="m/s")
        self.cards["min_battery"].configure(
            text=f"{analysis.min_battery} %",
            text_color="#ff6b6b" if analysis.min_battery < 20 else "white"
        )
        self.cards["gaps_detected"].configure(
            text=f"{len(analysis.timestamp_gaps)} adet",
            text_color="#fcc419" if analysis.has_gaps else "white"
        )

        # Tabloyu Doldur
        for item in self.tree_valid.get_children():
            self.tree_valid.delete(item)

        for _, row in result.valid_df.iterrows():
            ts_str = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(row["timestamp"], "strftime") else str(row["timestamp"])
            self.tree_valid.insert("", "end", values=(
                ts_str,
                row["altitude"],
                row["speed"],
                row["battery_pct"],
                row["longitude"],
                row["latitude"],
                row["pitch"],
                row["roll"],
                row["yaw"]
            ))

        # Grafikleri Çiz
        self._plot_telemetry(result.valid_df, analysis)

        # YALNIZCA HATA VARSA UYARI POPUP'I AÇILIR (Hatasız durumda popup açılmaz)
        if result.invalid_rows > 0:
            messagebox.showwarning(
                "Doğrulama Uyarısı: Hatalı Kayıtlar Bulundu",
                f"Telemetri dosyasında {result.invalid_rows} adet hatalı satır tespit edildi ve elendi.\n\n"
                f"• İşlenen Geçerli Kayıt: {result.valid_rows}\n"
                f"• Reddedilen Hatalı Kayıt: {result.invalid_rows}\n\n"
                f"Reddedilen satırların nedenleri 'Hatalı Kayıtlar Raporu' sekmesine aktarılmıştır."
            )

    def _plot_telemetry(self, df: pd.DataFrame, analysis: AnalysisResult):
        df_sorted = df.sort_values(by="timestamp").reset_index(drop=True)
        times = df_sorted["timestamp"]

        self.ax_alt.clear()
        self.ax_spd.clear()
        self.ax_bat.clear()

        self.ax_alt.plot(times, df_sorted["altitude"], color="#4dabf7", linewidth=2.0, label="İrtifa (m)")
        self._style_axis(self.ax_alt, "İrtifa (Altitude) [m]", "#4dabf7")
        self.ax_alt.legend(loc="upper left", facecolor="#212529", edgecolor="#495057", labelcolor="white")

        self.ax_spd.plot(times, df_sorted["speed"], color="#69db7c", linewidth=2.0, label="Hız (m/s)")
        self._style_axis(self.ax_spd, "Hız (Speed) [m/s]", "#69db7c")
        self.ax_spd.legend(loc="upper left", facecolor="#212529", edgecolor="#495057", labelcolor="white")

        self.ax_bat.plot(times, df_sorted["battery_pct"], color="#ffa94d", linewidth=2.0, label="Batarya (%)")
        self._style_axis(self.ax_bat, "Batarya Seviyesi [%]", "#ffa94d")
        self.ax_bat.legend(loc="upper left", facecolor="#212529", edgecolor="#495057", labelcolor="white")

        for gap in analysis.timestamp_gaps:
            for ax in (self.ax_alt, self.ax_spd, self.ax_bat):
                ax.axvspan(gap.start_time, gap.end_time, color="#ff6b6b", alpha=0.35, linestyle="--")
                ax.axvline(gap.end_time, color="#ff6b6b", linestyle=":", linewidth=1.5)

        self.ax_bat.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        self.fig.autofmt_xdate()
        self.fig.tight_layout(pad=1.8)
        self.canvas.draw()

    def _reset_kpi_and_views(self):
        for key in self.cards:
            self.cards[key].configure(text="-", text_color="white")
        for item in self.tree_valid.get_children():
            self.tree_valid.delete(item)
        self.ax_alt.clear()
        self.ax_spd.clear()
        self.ax_bat.clear()
        self._style_axis(self.ax_alt, "İrtifa (Altitude) [m]", "#4dabf7")
        self._style_axis(self.ax_spd, "Hız (Speed) [m/s]", "#69db7c")
        self._style_axis(self.ax_bat, "Batarya Seviyesi [%]", "#ffa94d")
        self.canvas.draw()

if __name__ == "__main__":
    app = TelemetryApp()
    app.mainloop()
