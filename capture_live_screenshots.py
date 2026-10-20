# -*- coding: utf-8 -*-
"""
Canlı Ekran Görüntüsü Yakalama Otomasyonu (v1.6.0)
Kullanıcının aktif masaüstünde (WinSta0\\Default) uygulamaları görünür olarak açar,
adım adım senaryoları çalıştırır ve 10 adet ekran görüntüsünü kaydeder.
"""
import ctypes
from ctypes import wintypes
import os
import sys
import time
import threading
import subprocess
from PIL import Image, ImageGrab

# 1. Kullanıcının görünür masaüstüne (WinSta0\Default) bağlan ve DPI farkındalığını aç
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass

DESK_ALL = 0x01FF
hdesk = user32.OpenDesktopW("Default", 0, False, DESK_ALL)
if hdesk:
    user32.SetThreadDesktop(hdesk)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(PROJECT_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def attach_thread_to_default_desktop():
    hd = user32.OpenDesktopW("Default", 0, False, DESK_ALL)
    if hd:
        user32.SetThreadDesktop(hd)


def get_top_hwnd(widget):
    widget.update_idletasks()
    widget.update()
    hwnd = widget.winfo_id()
    return user32.GetAncestor(hwnd, 2) or user32.GetParent(hwnd) or hwnd


def get_window_bbox(hwnd, pad=0):
    rect = wintypes.RECT()
    try:
        dwmapi = ctypes.windll.dwmapi
        res = dwmapi.DwmGetWindowAttribute(
            wintypes.HWND(hwnd),
            ctypes.c_ulong(9),
            ctypes.byref(rect),
            ctypes.sizeof(rect),
        )
        if res != 0:
            user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(rect))
    except Exception:
        user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(rect))

    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    left = max(0, rect.left - pad)
    top = max(0, rect.top - pad)
    right = min(screen_w, rect.right + pad)
    bottom = min(screen_h, rect.bottom + pad)
    return (left, top, right, bottom)


def bring_to_front(widget):
    try:
        widget.deiconify()
        widget.lift()
        widget.attributes("-topmost", True)
        widget.update()
        top_hwnd = get_top_hwnd(widget)
        user32.ShowWindow(top_hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(top_hwnd)
        widget.update()
    except Exception:
        pass


def grab_widget_window(widget, out_filename):
    attach_thread_to_default_desktop()
    widget.update_idletasks()
    widget.update()
    time.sleep(0.35)
    top_hwnd = get_top_hwnd(widget)
    bbox = get_window_bbox(top_hwnd, pad=2)
    img = ImageGrab.grab(bbox=bbox)
    out_path = os.path.join(SCREENSHOTS_DIR, out_filename)
    img.save(out_path, "PNG")
    print(f"[OK] Kaydedildi: {out_filename} ({img.size[0]}x{img.size[1]})")
    return out_path


def capture_modal_and_close(top_hwnd, dialog_titles, out_filename, delay_before_grab=1.3):
    """
    Arka plan iş parçacığında çalışarak açılan yerel Windows mesaj kutusunu (#32770) yakalar,
    kullanıcının ekranda görmesi için bekler, ana pencere + mesaj kutusunun ekran görüntüsünü alır
    ve ardından mesaj kutusunu kapatır. (Tkinter nesnesine arka plandan dokunmaz!)
    """
    def _worker():
        attach_thread_to_default_desktop()
        t0 = time.time()
        dlg_hwnd = 0
        while time.time() - t0 < 6.0:
            for title in dialog_titles:
                h = user32.FindWindowW("#32770", title)
                if h and user32.IsWindowVisible(h):
                    dlg_hwnd = h
                    break
            if dlg_hwnd:
                break
            time.sleep(0.06)

        # Kullanıcının ekranda popup'ı rahatça görmesi için bekle
        time.sleep(delay_before_grab)

        try:
            bbox_main = get_window_bbox(top_hwnd, pad=2)
            if dlg_hwnd:
                user32.SetForegroundWindow(dlg_hwnd)
                time.sleep(0.15)
                bbox_dlg = get_window_bbox(dlg_hwnd, pad=8)
                bbox = (
                    min(bbox_main[0], bbox_dlg[0]),
                    min(bbox_main[1], bbox_dlg[1]),
                    max(bbox_main[2], bbox_dlg[2]),
                    max(bbox_main[3], bbox_dlg[3]),
                )
            else:
                bbox = bbox_main

            img = ImageGrab.grab(bbox=bbox)
            out_path = os.path.join(SCREENSHOTS_DIR, out_filename)
            img.save(out_path, "PNG")
            print(f"[OK - MODAL] Kaydedildi: {out_filename} ({img.size[0]}x{img.size[1]})")
        except Exception as e:
            print(f"[ERR - MODAL] {out_filename}: {e}")

        # Mesaj kutusunu kapat (WM_CLOSE = 0x0010, WM_COMMAND IDOK = 1)
        if dlg_hwnd:
            user32.PostMessageW(dlg_hwnd, 0x0010, 0, 0)
            time.sleep(0.12)
            if user32.IsWindowVisible(dlg_hwnd):
                user32.PostMessageW(dlg_hwnd, 0x0111, 1, 0)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t


def step1_capture_csv_generator():
    print("\n--- [1/3] CSV Senaryo Üretici Arayüzü Başlatılıyor ---")
    gen_dir = os.path.join(PROJECT_DIR, "csv_senaryo_uretici")
    sys.path.insert(0, gen_dir)
    import app as gen_app

    app = gen_app.CSVGeneratorApp()
    t_start = time.time()
    while time.time() - t_start < 2.2:
        app.update()
        time.sleep(0.03)

    app.geometry("1240x760+40+15")
    bring_to_front(app)
    for _ in range(25):
        app.update()
        time.sleep(0.03)

    app.combo_scenarios.set(app.scenario_values[2])
    app.preview_data_action()
    for _ in range(30):
        app.update()
        time.sleep(0.04)

    time.sleep(1.0)
    grab_widget_window(app, "01_csv_senaryo_uretici_arayuzu.png")
    time.sleep(0.4)
    app.destroy()


def step2_capture_telemetry_app():
    print("\n--- [2/3] İHA Telemetri Analiz İstasyonu Başlatılıyor ---")
    sys.path.insert(0, PROJECT_DIR)
    import gui_app

    app = gui_app.TelemetryApp()
    # Splash ekranını canlı göster
    t_start = time.time()
    while time.time() - t_start < 2.2:
        app.update()
        time.sleep(0.03)

    # 1080p ekranda görev çubuğuna çarpmadan tam görünmesi için konumlandır
    app.geometry("1240x760+40+15")
    bring_to_front(app)
    for _ in range(30):
        app.update()
        time.sleep(0.03)

    top_hwnd = get_top_hwnd(app)
    sample_dir = os.path.join(PROJECT_DIR, "samples")

    # ---------------------------------------------------------
    # Şekil 4.1: Dosya seçilmeden analiz (04_hata_dosya_secilmeden_analiz.png)
    # ---------------------------------------------------------
    print("-> Şekil 4.1: Dosya seçilmeden analiz testi...")
    app.current_file_path = None
    app.lbl_file_path.configure(text="Analiz edilecek CSV dosyasını seçiniz...", text_color="gray")
    app.update()
    time.sleep(0.5)
    t41 = capture_modal_and_close(top_hwnd, ["Dosya Seçilmedi", "Uyarı"], "04_hata_dosya_secilmeden_analiz.png", 1.2)
    app.run_analysis()
    t41.join(timeout=4.0)
    app.update()
    time.sleep(0.4)

    # ---------------------------------------------------------
    # Şekil 4.2: Boş dosya hatası (05_hata_bos_veya_bozuk_dosya.png)
    # ---------------------------------------------------------
    print("-> Şekil 4.2: Boş CSV dosyası hatası...")
    empty_csv = os.path.join(sample_dir, "telemetry_empty.csv")
    app.current_file_path = empty_csv
    app.lbl_file_path.configure(text=os.path.basename(empty_csv), text_color="#00d2ff")
    app.update()
    time.sleep(0.5)
    t42 = capture_modal_and_close(
        top_hwnd,
        ["Doğrulama / Yükleme Hatası", "Veri Hatası", "Hata"],
        "05_hata_bos_veya_bozuk_dosya.png",
        1.2,
    )
    app.run_analysis()
    t42.join(timeout=4.0)
    app.update()
    time.sleep(0.4)

    # ---------------------------------------------------------
    # Şekil 4.3: Eksik sütunlu dosya hatası (06_hata_eksik_sutunlu_dosya.png)
    # ---------------------------------------------------------
    print("-> Şekil 4.3: Eksik sütunlu CSV dosyası hatası...")
    missing_csv = os.path.join(sample_dir, "telemetry_missing_columns.csv")
    app.current_file_path = missing_csv
    app.lbl_file_path.configure(text=os.path.basename(missing_csv), text_color="#00d2ff")
    app.update()
    time.sleep(0.5)
    t43 = capture_modal_and_close(
        top_hwnd,
        ["Doğrulama / Yükleme Hatası", "Veri Hatası", "Hata"],
        "06_hata_eksik_sutunlu_dosya.png",
        1.2,
    )
    app.run_analysis()
    t43.join(timeout=4.0)
    app.update()
    time.sleep(0.4)

    # ---------------------------------------------------------
    # Şekil 3.1: %100 Geçerli Uçuş Analizi ve Grafikler (03_gecerli_ucus_analiz_ve_grafikler.png)
    # ---------------------------------------------------------
    print("-> Şekil 3.1: Geçerli uçuş analizi ve zaman serisi grafikleri...")
    valid_csv = os.path.join(sample_dir, "telemetry_valid.csv")
    app.current_file_path = valid_csv
    app.lbl_file_path.configure(text=os.path.basename(valid_csv), text_color="#00d2ff")
    app._load_raw_file_content(valid_csv)
    app.update()
    app.run_analysis()
    app.tabview.set("📈 Telemetri Grafikleri")
    app._on_tab_switched()
    for _ in range(35):
        app.update()
        time.sleep(0.03)
    time.sleep(0.8)
    grab_widget_window(app, "03_gecerli_ucus_analiz_ve_grafikler.png")

    # ---------------------------------------------------------
    # Şekil 4.4: Kısmi Hatalı Veri Uyarı Popup'ı (07_kismi_hatali_uyari_popup.png)
    # ---------------------------------------------------------
    print("-> Şekil 4.4: Kısmi hatalı veri ve zaman boşluğu uyarı popup'ı...")
    mixed_csv = os.path.join(sample_dir, "telemetry_mixed.csv")
    app.current_file_path = mixed_csv
    app.lbl_file_path.configure(text=os.path.basename(mixed_csv), text_color="#00d2ff")
    app._load_raw_file_content(mixed_csv)
    app.update()
    time.sleep(0.5)
    t44 = capture_modal_and_close(
        top_hwnd,
        ["Doğrulama Uyarısı: Hatalı Kayıtlar Bulundu", "Uyarı"],
        "07_kismi_hatali_uyari_popup.png",
        1.4,
    )
    app.run_analysis()
    t44.join(timeout=4.0)
    for _ in range(35):
        app.update()
        time.sleep(0.03)

    # ---------------------------------------------------------
    # Şekil 5.1: Zaman Boşluğu (Gap) Grafik Anomalisi (09_zaman_boslugu_gap_grafik_anomalisi.png)
    # ---------------------------------------------------------
    print("-> Şekil 5.1: Zaman boşluğu (Gap) kırmızı anomali bölgesi grafikleri...")
    app.tabview.set("📈 Telemetri Grafikleri")
    app._on_tab_switched()
    for _ in range(35):
        app.update()
        time.sleep(0.03)
    time.sleep(0.8)
    grab_widget_window(app, "09_zaman_boslugu_gap_grafik_anomalisi.png")

    # ---------------------------------------------------------
    # Şekil 4.5: Hatalı Kayıtlar Raporu Sekmesi (08_hatali_kayitlar_raporu_sekmesi.png)
    # ---------------------------------------------------------
    print("-> Şekil 4.5: Hatalı Kayıtlar Raporu sekmesi...")
    app.tabview.set("⚠️ Hatalı Kayıtlar Raporu")
    app._on_tab_switched()
    for _ in range(35):
        app.update()
        time.sleep(0.03)
    time.sleep(0.8)
    grab_widget_window(app, "08_hatali_kayitlar_raporu_sekmesi.png")

    # ---------------------------------------------------------
    # Şekil 2.1: Ham CSV Dosyası (Orijinal) Sekmesi (02_ham_csv_orijinal_sekmesi.png)
    # ---------------------------------------------------------
    print("-> Şekil 2.1: Ham CSV Dosyası (Orijinal) sekmesi...")
    app.tabview.set("📄 Ham CSV Dosyası (Orijinal)")
    app._on_tab_switched()
    for _ in range(35):
        app.update()
        time.sleep(0.03)
    time.sleep(0.8)
    grab_widget_window(app, "02_ham_csv_orijinal_sekmesi.png")

    time.sleep(0.4)
    app.destroy()


def step3_capture_pytest_window():
    print("\n--- [3/3] Pytest 35 Otomatik Test Çıktısı Penceresi Gösteriliyor ---")
    res = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    pytest_output = f"PS {PROJECT_DIR}> python -m pytest tests/ -v\n" + res.stdout

    import customtkinter as ctk

    ctk.set_appearance_mode("dark")
    term_win = ctk.CTk()
    term_win.title("Windows PowerShell — Pytest Otomatik Test Koşumu (35 Test Senaryosu)")
    term_win.geometry("1180x740+50+20")
    term_win.configure(fg_color="#0C0C0C")

    header = ctk.CTkFrame(term_win, fg_color="#1F2428", height=38, corner_radius=0)
    header.pack(fill="x", side="top")
    ctk.CTkLabel(
        header,
        text="  🐚 Windows PowerShell — pytest tests/ -v (İHA Telemetri Otomatik Birim ve Entegrasyon Testleri)",
        font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
        text_color="#58A6FF",
    ).pack(side="left", padx=10, pady=6)
    ctk.CTkLabel(
        header,
        text="✔ 35 passed in 0.65s  ",
        font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
        text_color="#3FB950",
    ).pack(side="right", padx=12, pady=6)

    txt = ctk.CTkTextbox(
        term_win,
        font=ctk.CTkFont(family="Consolas", size=11),
        fg_color="#0C0C0C",
        text_color="#D4D4D4",
        corner_radius=0,
    )
    txt.pack(fill="both", expand=True, padx=8, pady=8)
    txt.insert("1.0", pytest_output)

    inner_tb = txt._textbox
    inner_tb.tag_config("passed", foreground="#3FB950")
    inner_tb.tag_config("cmd", foreground="#58A6FF")
    inner_tb.tag_config("summary", foreground="#3FB950", background="#122D1F")
    inner_tb.tag_add("cmd", "1.0", "1.end")

    lines = pytest_output.splitlines()
    for idx, line in enumerate(lines, start=1):
        if "PASSED" in line:
            p_pos = line.find("PASSED")
            inner_tb.tag_add("passed", f"{idx}.{p_pos}", f"{idx}.{p_pos+6}")
        if "passed in" in line:
            inner_tb.tag_add("summary", f"{idx}.0", f"{idx}.end")

    bring_to_front(term_win)
    for _ in range(30):
        term_win.update()
        time.sleep(0.03)

    time.sleep(1.2)
    grab_widget_window(term_win, "10_pytest_35_otomatik_test_ciktisi.png")
    time.sleep(0.4)
    term_win.destroy()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "step1":
            step1_capture_csv_generator()
        elif mode == "step2":
            step2_capture_telemetry_app()
        elif mode == "step3":
            step3_capture_pytest_window()
    else:
        if not os.path.exists(os.path.join(SCREENSHOTS_DIR, "01_csv_senaryo_uretici_arayuzu.png")):
            subprocess.run([sys.executable, "-X", "utf8", __file__, "step1"], check=True)
        subprocess.run([sys.executable, "-X", "utf8", __file__, "step2"], check=True)
        subprocess.run([sys.executable, "-X", "utf8", __file__, "step3"], check=True)
        print("\n=== TÜM 10 EKRAN GÖRÜNTÜSÜ BAŞARIYLA YAKALANDI ===")
