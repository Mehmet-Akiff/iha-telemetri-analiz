"""
build_signed_dist.py
PyInstaller'ın imzasız runw.exe önyükleyicisi yerine %100 DigiCert imzalı (Python Software Foundation)
resmi pythonw.exe çalışma motorunu kullanan, Avast/Defender tarafından kesinlikle engellenmeyen
bağımsız masaüstü paketleyici (v1.3.0).
"""

import os
import shutil
import zipfile

PYTHON_HOME = r"C:\Users\PC\AppData\Local\Programs\Python\Python312"
EMBED_ZIP = r"c:\Users\PC\Desktop\Projects\İME Proje\python-3.12.1-embed-amd64.zip"


def create_signed_runtime(target_runtime_dir: str):
    os.makedirs(target_runtime_dir, exist_ok=True)
    # 1. Resmi imzalı embeddable zip'i çıkart
    with zipfile.ZipFile(EMBED_ZIP, "r") as zf:
        zf.extractall(target_runtime_dir)

    # 2. python312._pth dosyasını güncelle (tkinter, lib, site-packages ve uygulama dizinini ekle)
    pth_file = os.path.join(target_runtime_dir, "python312._pth")
    with open(pth_file, "w", encoding="utf-8") as f:
        f.write("python312.zip\n")
        f.write(".\n")
        f.write("..\n")
        f.write("Lib\n")
        f.write("DLLs\n")
        f.write("site-packages\n")
        f.write("import site\n")

    # 3. Tkinter (_tkinter.pyd, tcl86t.dll, tk86t.dll) ve tcl/tk klasörlerini kopyala
    dlls_src = os.path.join(PYTHON_HOME, "DLLs")
    for dll_name in ["_tkinter.pyd", "tcl86t.dll", "tk86t.dll", "zlib1.dll"]:
        src_path = os.path.join(dlls_src, dll_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(target_runtime_dir, dll_name))

    tcl_src = os.path.join(PYTHON_HOME, "tcl")
    tcl_dst = os.path.join(target_runtime_dir, "tcl")
    if os.path.exists(tcl_src) and not os.path.exists(tcl_dst):
        shutil.copytree(tcl_src, tcl_dst)

    # 4. Standart kütüphaneden tkinter modülünü kopyala
    tk_lib_src = os.path.join(PYTHON_HOME, "Lib", "tkinter")
    tk_lib_dst = os.path.join(target_runtime_dir, "Lib", "tkinter")
    if os.path.exists(tk_lib_src) and not os.path.exists(tk_lib_dst):
        shutil.copytree(tk_lib_src, tk_lib_dst)

    # 5. Gerekli site-packages kütüphanelerini kopyala
    sp_src = os.path.join(PYTHON_HOME, "Lib", "site-packages")
    sp_dst = os.path.join(target_runtime_dir, "site-packages")
    os.makedirs(sp_dst, exist_ok=True)

    required_pkgs = [
        "customtkinter",
        "darkdetect",
        "packaging",
        "numpy",
        "numpy.libs",
        "pandas",
        "pandas.libs",
        "dateutil",
        "pytz",
        "tzdata",
        "six.py",
        "matplotlib",
        "mpl_toolkits",
        "pylab.py",
        "PIL",
        "contourpy",
        "cycler",
        "fonttools",
        "kiwisolver",
        "pyparsing",
    ]

    for pkg in required_pkgs:
        s = os.path.join(sp_src, pkg)
        d = os.path.join(sp_dst, pkg)
        if os.path.exists(s):
            if os.path.isdir(s):
                if not os.path.exists(d):
                    shutil.copytree(
                        s,
                        d,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests", "test", "*nmakehlp.exe"),
                    )
            else:
                shutil.copy2(s, d)


def build_package(
    app_title: str,
    folder_name: str,
    project_dir: str,
    entry_script: str,
    extra_files: list,
    extra_dirs: list,
):
    dist_root = os.path.join(project_dir, "dist_signed", folder_name)
    if os.path.exists(dist_root):
        shutil.rmtree(dist_root)
    os.makedirs(dist_root, exist_ok=True)

    # Uygulama dosyalarını kopyala
    shutil.copy2(os.path.join(project_dir, entry_script), os.path.join(dist_root, entry_script))
    for ef in extra_files:
        shutil.copy2(os.path.join(project_dir, ef), os.path.join(dist_root, ef))
    for ed in extra_dirs:
        s_dir = os.path.join(project_dir, ed)
        if os.path.exists(s_dir):
            shutil.copytree(s_dir, os.path.join(dist_root, ed))

    # İmzalı runtime'ı oluştur
    runtime_dir = os.path.join(dist_root, "runtime")
    create_signed_runtime(runtime_dir)

    # Tcl/Tk ortam değişkenlerini otomatik ayarlayan başlatıcı sarmalayıcı (boot.pyw)
    boot_pyw = os.path.join(dist_root, "boot.pyw")
    with open(boot_pyw, "w", encoding="utf-8") as f:
        f.write(
            f"""import os, sys
base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
os.environ['TCL_LIBRARY'] = os.path.join(base_dir, 'runtime', 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(base_dir, 'runtime', 'tcl', 'tk8.6')
import {os.path.splitext(entry_script)[0]}
if __name__ == '__main__':
    if hasattr({os.path.splitext(entry_script)[0]}, 'TelemetryApp'):
        app = {os.path.splitext(entry_script)[0]}.TelemetryApp()
        app.mainloop()
    elif hasattr({os.path.splitext(entry_script)[0]}, 'CSVGeneratorApp'):
        app = {os.path.splitext(entry_script)[0]}.CSVGeneratorApp()
        app.mainloop()
"""
        )

    # Kullanıcının çift tıklayacağı sıfır-konsol başlatıcı (.vbs ve .bat)
    vbs_launcher = os.path.join(dist_root, f"{app_title} Baslat.vbs")
    with open(vbs_launcher, "w", encoding="utf-8") as f:
        f.write(
            'Set fso = CreateObject("Scripting.FileSystemObject")\n'
            'baseDir = fso.GetParentFolderName(WScript.ScriptFullName)\n'
            'Set shell = CreateObject("WScript.Shell")\n'
            'shell.CurrentDirectory = baseDir\n'
            'shell.Run Chr(34) & baseDir & "\\runtime\\pythonw.exe" & Chr(34) & " " & Chr(34) & baseDir & "\\boot.pyw" & Chr(34), 0, False\n'
        )

    bat_launcher = os.path.join(dist_root, f"{app_title} Baslat.bat")
    with open(bat_launcher, "w", encoding="utf-8") as f:
        f.write(
            '@echo off\n'
            'cd /d "%~dp0"\n'
            'start "" "%~dp0runtime\\pythonw.exe" "%~dp0boot.pyw"\n'
        )

    print(f"[OK] Built signed package: {dist_root}")
    return dist_root


if __name__ == "__main__":
    p1 = build_package(
        app_title="IHA_Telemetri_Analiz",
        folder_name="IHA_Telemetri_Analiz_v1.4.0",
        project_dir=r"c:\Users\PC\Desktop\Projects\İME Proje",
        entry_script="gui_app.py",
        extra_files=["telemetry_validator.py", "telemetry_analyzer.py", "data_generator.py", "README.md", "TEKNIK_RAPOR.md"],
        extra_dirs=["assets", "samples"],
    )

    p2 = build_package(
        app_title="CSV_Senaryo_Uretici",
        folder_name="CSV_Senaryo_Uretici_v1.4.0",
        project_dir=r"c:\Users\PC\Desktop\Projects\iha-csv-senaryo-uretici",
        entry_script="app.py",
        extra_files=["scenario_engine.py", "README.md"],
        extra_dirs=["assets"],
    )
