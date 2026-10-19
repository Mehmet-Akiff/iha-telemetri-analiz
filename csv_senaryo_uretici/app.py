"""
app.py
İHA Telemetri CSV Senaryo Üretici Masaüstü Uygulaması (v1.6.0).
Bağımsız masaüstü arayüzü, otomatik sıralı/tarihli periyot klasörleme,
akıllı en büyük sayı takibi (Üretilen Klasör N), anında canlı önizleme,
şeffaf hata ve temiz veri bildirimleri, garantili 1.8 sn animasyonlu İHA açılış ekranı (Splash Screen),
pencere fade-in ve sekme/sayfa geçiş animasyonları.
"""

import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import pandas as pd

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

from scenario_engine import TelemetryScenarioGenerator, SCENARIO_DESCRIPTIONS

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


def get_resource_path(relative_path: str) -> str:
    """PyInstaller veya taşınabilir çalışmada kaynak dosya yolunu döndürür."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class CSVGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("İHA Telemetri CSV Senaryo Üretici v1.6.0")
        self.geometry("1240x870")
        self.minsize(1020, 740)

        # İHA İkonunu Ayarla
        icon_path = get_resource_path(os.path.join("assets", "generator_icon.ico"))
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.generator = TelemetryScenarioGenerator()
        self.current_df = None
        self.current_raw = None

        # Varsayılan Hedef Kayıt Dizini (Masaüstündeki Test_CSV_Verileri veya samples)
        desktop_test_dir = r"C:\Users\PC\Desktop\IHA_Masaustu_Uygulamalari\Test_CSV_Verileri"
        if os.path.exists(desktop_test_dir):
            self.target_base_dir = os.path.abspath(desktop_test_dir)
        elif os.path.exists("samples"):
            self.target_base_dir = os.path.abspath("samples")
        else:
            self.target_base_dir = os.path.abspath(os.getcwd())

        self._build_ui()

        if pyi_splash is not None:
            try:
                pyi_splash.close()
            except Exception:
                pass

        # Çok hızlı açılsa bile en az 1.8 saniye garantili animasyonlu Açılış Paneli (Splash) göster
        self._show_startup_splash()

    def _show_startup_splash(self):
        """İlk tıklamada ekranda 1.8 saniye boyunca animasyonlu İHA Senaryo Üretici yükleme paneli gösterir."""
        self.attributes("-alpha", 0.0)

        splash = tk.Toplevel(self)
        splash.overrideredirect(True)
        splash.attributes("-topmost", True)
        splash.configure(bg="#0c2018")

        w, h = 540, 310
        sw = splash.winfo_screenwidth()
        sh = splash.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        splash.geometry(f"{w}x{h}+{x}+{y}")

        border = tk.Frame(splash, bg="#2bda72", bd=0)
        border.place(x=0, y=0, width=w, height=h)
        inner = tk.Frame(border, bg="#0c2018")
        inner.place(x=2, y=2, width=w - 4, height=h - 4)

        top_bar = tk.Frame(inner, bg="#2bda72", height=5)
        top_bar.pack(fill="x", side="top")

        png_path = get_resource_path(os.path.join("assets", "generator_icon.png"))
        if os.path.exists(png_path):
            try:
                pil_img = Image.open(png_path).resize((84, 84), Image.Resampling.LANCZOS)
                self._splash_logo = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(84, 84))
                logo_lbl = ctk.CTkLabel(inner, image=self._splash_logo, text="", fg_color="#0c2018")
                logo_lbl.pack(pady=(22, 8))
            except Exception:
                pass

        title_lbl = ctk.CTkLabel(
            inner,
            text="İHA TELEMETRİ CSV SENARYO ÜRETİCİ",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff",
            fg_color="#0c2018",
        )
        title_lbl.pack(pady=(2, 2))

        sub_lbl = ctk.CTkLabel(
            inner,
            text="14 Farklı Uçuş, Sensör Hatası ve Sınır Değer Simülatörü • v1.6.0",
            font=ctk.CTkFont(size=11),
            text_color="#69db7c",
            fg_color="#0c2018",
        )
        sub_lbl.pack(pady=(0, 18))

        status_lbl = ctk.CTkLabel(
            inner,
            text="İHA simülasyon profilleri yükleniyor... %0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e9ecef",
            fg_color="#0c2018",
        )
        status_lbl.pack(pady=(0, 8))

        pbar = ctk.CTkProgressBar(inner, width=430, height=12, corner_radius=6, progress_color="#2bda72", fg_color="#16382b")
        pbar.set(0.0)
        pbar.pack(pady=(0, 14))

        footer_lbl = ctk.CTkLabel(
            inner,
            text="🛡️ DigiCert İmzalı Güvenli Çalışma Zamanı • Akıllı Sıralı Klasörleme Sistemi",
            font=ctk.CTkFont(size=10),
            text_color="#868e96",
            fg_color="#0c2018",
        )
        footer_lbl.pack(side="bottom", pady=10)

        total_steps = 36  # ~1.8 saniye garantili açılış ekranı

        def animate_splash(step_idx=0):
            if step_idx <= total_steps:
                prog = step_idx / total_steps
                pbar.set(prog)
                pct = int(prog * 100)
                if prog < 0.30:
                    msg = f"14 farklı İHA uçuş ve hata senaryosu yükleniyor... %{pct}"
                elif prog < 0.65:
                    msg = f"Sentetik telemetri üretim motoru hazırlanıyor... %{pct}"
                elif prog < 0.90:
                    msg = f"Canlı tablo ve ham CSV önizleme katmanı başlatılıyor... %{pct}"
                else:
                    msg = f"Simülatör hazır! Arayüz açılıyor... %{pct}"
                status_lbl.configure(text=msg)
                self.after(48, animate_splash, step_idx + 1)
            else:
                try:
                    splash.destroy()
                except Exception:
                    pass
                self._fade_in_main_window()

        animate_splash(0)

    def _fade_in_main_window(self, alpha=0.0):
        """Ana pencereyi yumuşak (fade-in) animasyonla görünür yapar."""
        alpha = min(1.0, alpha + 0.12)
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(20, self._fade_in_main_window, alpha)
        else:
            self.focus_force()

    def _shorten_path(self, path: str, max_chars: int = 40) -> str:
        """Uzun dosya yollarını arayüzde taşmayacak şekilde kısaltır."""
        if len(path) <= max_chars:
            return path
        return "..." + path[-(max_chars - 3):]

    def _get_current_seq(self) -> int:
        return self.generator.get_next_sequence_number(self.target_base_dir)

    def _build_ui(self):
        top_frame = ctk.CTkFrame(self, corner_radius=10)
        top_frame.pack(fill="x", padx=15, pady=(15, 10))

        png_path = get_resource_path(os.path.join("assets", "generator_icon.png"))
        if os.path.exists(png_path):
            try:
                pil_hdr = Image.open(png_path).resize((34, 34), Image.Resampling.LANCZOS)
                self._hdr_icon = ctk.CTkImage(light_image=pil_hdr, dark_image=pil_hdr, size=(34, 34))
                hdr_img_lbl = ctk.CTkLabel(top_frame, image=self._hdr_icon, text="")
                hdr_img_lbl.pack(side="left", padx=(15, 4), pady=10)
            except Exception:
                pass

        title_lbl = ctk.CTkLabel(
            top_frame,
            text="İHA Telemetri CSV Senaryo Üretici",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_lbl.pack(side="left", padx=(6, 15), pady=12)

        subtitle_lbl = ctk.CTkLabel(
            top_frame,
            text="14 Farklı Uçuş ve Hata Senaryosu • Otomatik Sıralı Klasörleme • v1.6.0",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_lbl.pack(side="left", padx=10, pady=12)

        main_content = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # SOL PANEL (Kontroller & Üretim)
        self.left_panel = ctk.CTkFrame(main_content, width=440, corner_radius=10, border_width=1, border_color="#2b3035")
        self.left_panel.pack(side="left", fill="y", padx=(0, 10), pady=0)
        self.left_panel.pack_propagate(False)

        # 1. Senaryo Seçimi
        ctk.CTkLabel(self.left_panel, text="📌 Senaryo Seçimi (Otomatik Önizlenir):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 4))

        self.scenario_keys = list(SCENARIO_DESCRIPTIONS.keys())
        self.scenario_values = list(SCENARIO_DESCRIPTIONS.values())

        self.combo_scenarios = ctk.CTkComboBox(
            self.left_panel,
            values=self.scenario_values,
            width=400,
            command=self._on_scenario_changed
        )
        self.combo_scenarios.set(self.scenario_values[0])
        self.combo_scenarios.pack(padx=15, pady=4)

        self.lbl_scenario_desc = ctk.CTkLabel(
            self.left_panel,
            text="Seçili senaryo açıklaması burada görünecek.",
            font=ctk.CTkFont(size=11),
            text_color="#ced4da",
            wraplength=400,
            justify="left"
        )
        self.lbl_scenario_desc.pack(anchor="w", padx=15, pady=(2, 8))

        # 2. Parametre Ayarları
        ctk.CTkLabel(self.left_panel, text="⚙️ Parametre Ayarları:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(4, 4))

        p_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        p_frame.pack(fill="x", padx=15, pady=2)

        def make_param_row(parent, label_text, default_val):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label_text, font=ctk.CTkFont(size=11)).pack(side="left")
            entry = ctk.CTkEntry(row, width=75, height=26)
            entry.insert(0, default_val)
            entry.pack(side="right")
            return entry

        self.entry_count = make_param_row(p_frame, "Kayıt Sayısı (Satır):", "60")
        self.entry_gap = make_param_row(p_frame, "Kesinti Süresi (sn):", "12.0")
        self.entry_alt = make_param_row(p_frame, "Başlangıç İrtifası (m):", "100.0")
        self.entry_spd = make_param_row(p_frame, "Başlangıç Hızı (m/s):", "15.0")
        self.entry_bat = make_param_row(p_frame, "Başlangıç Batarya (%):", "100.0")

        # Canlı Önizlemeyi Yenile Butonu
        self.btn_preview = ctk.CTkButton(
            self.left_panel,
            text="👁️ Parametre Değişikliğini Önizle",
            command=self.preview_data_action,
            fg_color="#1971c2",
            hover_color="#1864ab",
            height=30,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.btn_preview.pack(fill="x", padx=15, pady=(6, 10))

        # 3. Akıllı Hedef Dizin & Sıralı Klasörleme Kartı
        target_card = ctk.CTkFrame(self.left_panel, corner_radius=8, border_width=1, border_color="#373a40")
        target_card.pack(fill="x", padx=15, pady=(4, 6))

        ctk.CTkLabel(target_card, text="📁 Hedef Kayıt Dizini:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(6, 2))

        self.lbl_target_dir = ctk.CTkLabel(
            target_card,
            text=self._shorten_path(self.target_base_dir),
            font=ctk.CTkFont(size=11),
            text_color="#74c0fc",
            wraplength=380,
            justify="left"
        )
        self.lbl_target_dir.pack(anchor="w", padx=10, pady=(0, 2))

        f_row = ctk.CTkFrame(target_card, fg_color="transparent")
        f_row.pack(fill="x", padx=10, pady=(2, 6))

        self.btn_change_dir = ctk.CTkButton(
            f_row,
            text="📂 Klasör Değiştir",
            command=self.change_target_directory,
            width=130,
            height=26,
            fg_color="#343a40",
            hover_color="#495057",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.btn_change_dir.pack(side="left")

        self.lbl_next_seq = ctk.CTkLabel(
            f_row,
            text=f"📌 Sıradaki: Üretilen Klasör {self._get_current_seq()}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#51cf66"
        )
        self.lbl_next_seq.pack(side="right", padx=4)

        # 4. Üretim Kapsamı Seçimi (Radio Buttons)
        scope_card = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        scope_card.pack(fill="x", padx=15, pady=(4, 4))
        ctk.CTkLabel(scope_card, text="📦 Üretim Kapsamı:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 2))

        self.var_mode = tk.StringVar(value="temel")

        self.radio_temel = ctk.CTkRadioButton(
            scope_card,
            text="Temel Test Seti (5 Temel CSV: Geçerli, Kesintili, Karışık...)",
            variable=self.var_mode,
            value="temel",
            font=ctk.CTkFont(size=11)
        )
        self.radio_temel.pack(anchor="w", pady=2)

        self.radio_tum = ctk.CTkRadioButton(
            scope_card,
            text="Tüm Senaryolar (14 Farklı Test CSV'si)",
            variable=self.var_mode,
            value="tum",
            font=ctk.CTkFont(size=11)
        )
        self.radio_tum.pack(anchor="w", pady=2)

        self.radio_tekil = ctk.CTkRadioButton(
            scope_card,
            text="Yalnızca Seçili Senaryo (1 CSV)",
            variable=self.var_mode,
            value="tekil",
            font=ctk.CTkFont(size=11)
        )
        self.radio_tekil.pack(anchor="w", pady=2)

        # 5. Ana Üretim Butonu (Büyük Yeşil Buton)
        self.btn_produce = ctk.CTkButton(
            self.left_panel,
            text="🚀 YENİ KLASÖRDE ÜRET",
            command=self.produce_batch_action,
            fg_color="#2b8a3e",
            hover_color="#237032",
            height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_produce.pack(fill="x", padx=15, pady=(8, 4))

        # 6. Alt Yardımcı Butonlar
        sub_row = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        sub_row.pack(fill="x", padx=15, pady=(2, 10))

        self.btn_open_target = ctk.CTkButton(
            sub_row,
            text="📁 Hedef Dizini Aç",
            command=self.open_target_folder,
            fg_color="#495057",
            hover_color="#343a40",
            width=190,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.btn_open_target.pack(side="left")

        self.btn_save_single = ctk.CTkButton(
            sub_row,
            text="💾 Farklı Kaydet...",
            command=self.save_csv_action,
            fg_color="#495057",
            hover_color="#343a40",
            width=190,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.btn_save_single.pack(side="right")

        # SAĞ PANEL (Canlı Tablo ve Ham CSV Görünümü)
        right_panel = ctk.CTkFrame(main_content, corner_radius=10, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        preview_header = ctk.CTkFrame(right_panel, corner_radius=10)
        preview_header.pack(fill="x", padx=0, pady=(0, 8))

        ctk.CTkLabel(
            preview_header,
            text="📊 Canlı Telemetri Veri Önizlemesi",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left", padx=15, pady=10)

        self.lbl_stats = ctk.CTkLabel(
            preview_header,
            text="Önizleme hazır",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#51cf66"
        )
        self.lbl_stats.pack(side="right", padx=15, pady=10)

        self.tabview = ctk.CTkTabview(
            right_panel,
            corner_radius=10,
            border_width=2,
            border_color="#2b3035",
            command=self._on_tab_switched
        )
        self.tabview.pack(fill="both", expand=True)

        self.tab_table = self.tabview.add("📋 Tablo Görünümü")
        self.tab_raw = self.tabview.add("📄 Ham CSV İçeriği (Raw)")
        self.tab_info = self.tabview.add("ℹ️ Senaryo Rehberi")

        # Sekme 1: Tablo
        table_frame = ctk.CTkFrame(self.tab_table, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

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

        # Sekme 2: Ham CSV Metni (Orijinal / Filtresiz Görünüm)
        raw_box_frame = ctk.CTkFrame(self.tab_raw, fg_color="transparent")
        raw_box_frame.pack(fill="both", expand=True, padx=10, pady=10)

        raw_info_bar = ctk.CTkFrame(raw_box_frame, fg_color="#1c2d48", corner_radius=6)
        raw_info_bar.pack(fill="x", pady=(0, 6))

        self.lbl_raw_tab_info = ctk.CTkLabel(
            raw_info_bar,
            text="📄 Doğrudan Üretilen Orijinal Ham CSV Metni (Filtresiz / El Değmemiş)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#74c0fc"
        )
        self.lbl_raw_tab_info.pack(side="left", padx=10, pady=5)

        self.btn_copy_generator_raw = ctk.CTkButton(
            raw_info_bar,
            text="📋 Metni Kopyala",
            width=110,
            height=24,
            fg_color="#343a40",
            hover_color="#495057",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._copy_raw_to_clipboard
        )
        self.btn_copy_generator_raw.pack(side="right", padx=8, pady=4)

        self.txt_raw = ctk.CTkTextbox(raw_box_frame, font=ctk.CTkFont(family="Consolas", size=11), wrap="none")
        self.txt_raw.pack(fill="both", expand=True, padx=0, pady=0)

        # Sekme 3: Senaryo Rehberi
        info_txt = ctk.CTkTextbox(self.tab_info, font=ctk.CTkFont(size=13))
        info_txt.pack(fill="both", expand=True, padx=10, pady=10)
        guide_lines = ["🧪 14 FARKLI İHA TELEMETRİ SENARYOSU REHBERİ\n" + "=" * 55 + "\n"]
        for idx, (k, v) in enumerate(SCENARIO_DESCRIPTIONS.items(), 1):
            guide_lines.append(f"{idx:02d}. [{k}]\n    • {v}\n")
        info_txt.insert("1.0", "\n".join(guide_lines))
        info_txt.configure(state="disabled")

        # İlk Başlangıç Yüklemesi
        self._on_scenario_changed(self.combo_scenarios.get())

    def _copy_raw_to_clipboard(self):
        try:
            content = self.txt_raw.get("1.0", "end-1c")
            if content.strip():
                self.clipboard_clear()
                self.clipboard_append(content)
                messagebox.showinfo("Kopyalandı", "Ham CSV içeriği panoya başarıyla kopyalandı!")
            else:
                messagebox.showwarning("Boş", "Kopyalanacak içerik bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Panoya kopyalama başarısız: {str(e)}")

    def _on_tab_switched(self):
        """Sayfa geçişlerinde yeşil çerçeve parlaması (glow pulse) animasyonu."""
        glow_colors = ["#2bda72", "#40c057", "#2b8a3e", "#2b3035"]

        def animate_border(idx=0):
            if idx < len(glow_colors):
                self.tabview.configure(border_color=glow_colors[idx])
                self.after(65, animate_border, idx + 1)

        animate_border(0)

    def _get_selected_scenario_key(self) -> str:
        idx = self.combo_scenarios.cget("values").index(self.combo_scenarios.get())
        return self.scenario_keys[idx]

    def _on_scenario_changed(self, choice):
        """Senaryo açılır kutudan her değiştirildiğinde açıklamayı ve tablo önizlemesini ANINDA günceller."""
        key = self._get_selected_scenario_key()
        desc = SCENARIO_DESCRIPTIONS.get(key, "")
        self.lbl_scenario_desc.configure(text=f"Açıklama: {desc}")
        self.radio_tekil.configure(text=f"Yalnızca Seçili Senaryo (1 CSV: {key})")

        # Otomatik Canlı Önizleme!
        self.preview_data_action()

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
        """Seçili senaryoya ve parametrelere göre veriyi anında yeniden üretir ve arayüzde gösterir."""
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

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.txt_raw.configure(state="normal")
        self.txt_raw.delete("1.0", "end")

        if df is not None and not df.empty:
            for _, row in df.iterrows():
                vals = [row.get(col, "") for col in self.columns]
                self.tree.insert("", "end", values=vals)
            csv_text = df.to_csv(index=False)
            self.txt_raw.insert("1.0", csv_text)

            scenario_status_map = {
                "valid": ("✓ %100 Geçerli Uçuş (Temiz Veri • Hata veya anomali içermez)", "#51cf66"),
                "with_gaps": ("⏱️ Zaman Kesintisi / Gap (Metin hatası içermez, telemetri atlaması var)", "#fcc419"),
                "mixed": ("⚠️ Karışık Kısmi Hata (İrtifada 'METIN_HATASI', negatif hız, aşırı batarya vs.)", "#ff922b"),
                "text_in_numeric": ("⚠️ Sayısal Alanda Metin (İrtifada 'COK_YUKSEK' metin hatası içerir)", "#ff922b"),
                "negative_speed": ("⚠️ Negatif Hız Hatası (Hız sütununda speed < 0 değerleri enjekte edilir)", "#ff922b"),
                "battery_bounds": ("⚠️ Batarya Sınır İhlali (%0 altı ve %100 üstü değerler enjekte edilir)", "#ff922b"),
                "coord_bounds": ("⚠️ Koordinat Sınır İhlali (Enlem/Boylam sınır dışı değerler içerir)", "#ff922b"),
                "empty_fields": ("⚠️ Boş Alanlar Hatası (Zorunlu telemetri alanları boş bırakılır)", "#ff922b"),
                "bad_timestamps": ("⚠️ Bozuk Zaman Damgası ('HATALI_ZAMAN_2026' enjekte edilir)", "#ff922b"),
                "bad_angles": ("⚠️ Açısal Sınır İhlalleri (Pitch > 180, Roll > 180 aşırı açılar)", "#ff922b"),
                "missing_columns": ("⚠️ Eksik Sütunlu CSV (9 zorunlu sütun eksik üretilir)", "#ff922b"),
                "all_invalid": ("⚠️ Sıfır Geçerli Kayıt (Tüm satırlar kasıtlı olarak hatalıdır)", "#ff6b6b"),
                "corrupt_file": ("⚠️ Bozuk CSV Sözdizimi (Açık tırnak ve geçersiz baytlar içerir)", "#ff6b6b"),
                "empty_file": ("⚠️ 0 Bayt Boş Dosya (Başlık veya veri içermez)", "#ff8787"),
            }

            status_text, status_color = scenario_status_map.get(
                key, (f"📊 {len(df)} kayıt • Önizleme Hazır", "#51cf66")
            )
            self.lbl_raw_tab_info.configure(
                text=f"📄 [{key}] Senaryosu İçin Üretilen Orijinal Ham CSV Metni ({len(df)} Satır)",
                text_color="#51cf66" if "Geçerli" in status_text else "#fcc419"
            )
        elif raw is not None:
            self.txt_raw.insert("1.0", raw if raw else "<0 Bayt Boş Dosya>")
            status_text = "⚠️ Özel Ham/Bozuk Metin (Ham CSV Sekmesine Bakın)"
            status_color = "#ff6b6b"
            self.lbl_raw_tab_info.configure(text=f"📄 [{key}] Ham Bozuk Metin", text_color="#ff6b6b")
        else:
            status_text = "⚠️ 0 Bayt Boş Dosya Senaryosu"
            status_color = "#ff8787"
            self.lbl_raw_tab_info.configure(text="📄 0 Bayt Boş Dosya", text_color="#ff8787")

        self.lbl_stats.configure(text=status_text, text_color=status_color)
        self.txt_raw.configure(state="disabled")

        # Tablo sekmesine yumuşak geçiş efekti
        self._on_tab_switched()

    def change_target_directory(self):
        """Kullanıcının yeni bir hedef ana klasör seçmesini sağlar ve numaralandırmayı otomatik sıfırlar/günceller."""
        new_dir = filedialog.askdirectory(
            title="CSV Periyot Klasörlerinin Oluşturulacağı Hedef Ana Dizini Seçin",
            initialdir=self.target_base_dir
        )
        if new_dir:
            self.target_base_dir = os.path.abspath(new_dir)
            self.lbl_target_dir.configure(text=self._shorten_path(self.target_base_dir))
            next_seq = self._get_current_seq()
            self.lbl_next_seq.configure(text=f"📌 Sıradaki: Üretilen Klasör {next_seq}")
            messagebox.showinfo(
                "Hedef Dizin Güncellendi",
                f"Yeni hedef dizin ayarlandı:\n\n{self.target_base_dir}\n\n"
                f"Bu klasördeki en büyük sayı taranarak sıradaki klasör numarası belirlendi:\n"
                f"Sıradaki: Üretilen Klasör {next_seq}"
            )

    def produce_batch_action(self):
        """
        Hedef klasördeki en büyük sayıyı otomatik bulur, 1 fazlasını alarak
        'Üretilen Klasör N - Tarih' klasörünü açar ve seçilen moddaki CSV'leri üretir.
        Ardından klasörü Windows Gezgini'nde açar.
        """
        params = self._read_params()
        if not params:
            return
        count, gap, alt, spd, bat = params
        mode = self.var_mode.get()
        selected_key = self._get_selected_scenario_key()

        try:
            target_dir, seq_num, file_count = self.generator.generate_numbered_folder(
                base_output_dir=self.target_base_dir,
                mode=mode,
                selected_scenario_key=selected_key,
                count=count,
                gap_duration_sec=gap,
                initial_altitude=alt,
                initial_speed=spd,
                initial_battery=bat
            )

            # Sıradaki numara göstergesini güncelle (örn: 1 bitti, sıradaki 2)
            next_seq = self._get_current_seq()
            self.lbl_next_seq.configure(text=f"📌 Sıradaki: Üretilen Klasör {next_seq}")

            # Başarılı bildirim ve klasörü anında açma
            messagebox.showinfo(
                "Üretim Başarılı",
                f"Yeni periyot klasörü başarıyla oluşturuldu:\n\n"
                f"📁 {os.path.basename(target_dir)}\n"
                f"📍 Konum: {target_dir}\n"
                f"📄 Dosya Sayısı: {file_count} adet CSV dosyası\n\n"
                f"Klasör Windows Gezgini'nde açılıyor..."
            )
            try:
                os.startfile(target_dir)
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Üretim Hatası", f"Klasör veya CSV üretimi sırasında hata oluştu:\n{str(e)}")

    def open_target_folder(self):
        """Hedef ana dizini Windows Gezgini'nde açar."""
        if not os.path.exists(self.target_base_dir):
            os.makedirs(self.target_base_dir, exist_ok=True)
        os.startfile(self.target_base_dir)

    def save_csv_action(self):
        """Seçili senaryoyu tekil dosya olarak kullanıcının seçeceği konuma kaydeder."""
        params = self._read_params()
        if not params:
            return

        count, gap, alt, spd, bat = params
        key = self._get_selected_scenario_key()

        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{time_tag}_telemetry_{key}.csv"

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
                f"CSV dosyası başarıyla kaydedildi:\n\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")


if __name__ == "__main__":
    app = CSVGeneratorApp()
    app.mainloop()
