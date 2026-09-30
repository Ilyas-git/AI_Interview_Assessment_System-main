"""
Script Runner Otomatis - AI Interview Assessment System
Menjalankan Backend (FastAPI) dan Frontend (React Vite) secara bersamaan
hanya dengan satu terminal atau klik ganda.
"""
import os
import sys
import time
import socket
import shutil
import signal
import subprocess
import threading
import webbrowser
from pathlib import Path

# Pastikan output terminal mendukung UTF-8 (Emoji & simbol) di Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent

def find_dirs():
    """Mencari lokasi direktori src/backend dan src/ui secara fleksibel"""
    candidates = [
        CURRENT_DIR,
        CURRENT_DIR / "AI_Interview_Assessment_System-main",
        CURRENT_DIR.parent,
        CURRENT_DIR.parent / "AI_Interview_Assessment_System-main",
    ]
    for c in candidates:
        backend = c / "src" / "backend"
        ui = c / "src" / "ui"
        if backend.is_dir() and ui.is_dir():
            return backend.resolve(), ui.resolve()
    raise RuntimeError("Gagal menemukan direktori src/backend dan src/ui!")

backend_dir, ui_dir = find_dirs()

# Deteksi python di venv (jika ada)
venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
if not venv_python.exists():
    venv_python = backend_dir / "venv" / "bin" / "python"
python_bin = str(venv_python) if venv_python.exists() else sys.executable

# Deteksi npm executable
npm_bin = shutil.which("npm.cmd") or shutil.which("npm") or "npm"

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_port_owner(port):
    """Membantu menghentikan proses lama yang masih tertahan di port tertentu"""
    if sys.platform == "win32":
        try:
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"'
            out = subprocess.check_output(cmd, shell=True, text=True).strip()
            if out:
                for pid in out.splitlines():
                    pid = pid.strip()
                    if pid and pid != "0":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", pid],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

print("=" * 65)
print("🚀  AI INTERVIEW ASSESSMENT SYSTEM (One-Terminal Runner)")
print("=" * 65)
print(f" [+] Direktori Backend  : {backend_dir}")
print(f" [+] Direktori Frontend : {ui_dir}")
print(f" [+] Python Interpreter : {python_bin}")
print(" ---------------------------------------------------------------")
print(" [*] Backend URL        : http://localhost:8000")
print(" [*] Frontend URL       : http://localhost:5173")
print(" [*] API Documentation  : http://localhost:8000/docs")
print("=" * 65)
print(" Tekan [Ctrl + C] untuk mematikan semua server sekaligus.")
print("=" * 65 + "\n")

# Bersihkan port jika ada proses sebelumnya yang masih tertahan
for port in [8000, 5173]:
    if is_port_in_use(port):
        print(f"[*] Port {port} sedang digunakan oleh proses lama, membersihkan...")
        kill_port_owner(port)
        time.sleep(1)

processes = []
is_cleaning_up = False

def kill_process_tree(pid):
    """Menghentikan seluruh process tree termasuk child processes di Windows"""
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception:
            pass
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except Exception:
            pass

def log_stream(stream, prefix):
    """Membaca dan mencetak log dari subprocess secara realtime"""
    try:
        for line in iter(stream.readline, ""):
            if not line:
                break
            text = line.rstrip()
            if text:
                print(f"{prefix} {text}", flush=True)
    except Exception:
        pass
    finally:
        try:
            stream.close()
        except Exception:
            pass

def cleanup(sig=None, frame=None):
    global is_cleaning_up
    if is_cleaning_up:
        return
    is_cleaning_up = True
    print("\n\n🛑 Menghentikan server backend & frontend...", flush=True)
    for p in processes:
        try:
            kill_process_tree(p.pid)
            p.terminate()
        except Exception:
            pass
    for port in [8000, 5173]:
        kill_port_owner(port)
    print("✓ Semua server berhasil dihentikan. Sampai jumpa!", flush=True)
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Siapkan environment
env = os.environ.copy()
env["PYTHONUNBUFFERED"] = "1"

# 1. Jalankan Backend (FastAPI)
print("[*] Memulai Backend FastAPI...", flush=True)
backend_cmd = [python_bin, "-u", "main.py"]
backend_proc = subprocess.Popen(
    backend_cmd,
    cwd=str(backend_dir),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    encoding="utf-8",
    errors="replace",
    env=env
)
processes.append(backend_proc)
threading.Thread(target=log_stream, args=(backend_proc.stdout, "[BACKEND] "), daemon=True).start()

# 2. Jalankan Frontend (Vite)
print("[*] Memulai Frontend React (Vite)...", flush=True)
frontend_cmd = [npm_bin, "run", "dev"]
frontend_proc = subprocess.Popen(
    frontend_cmd,
    cwd=str(ui_dir),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    encoding="utf-8",
    errors="replace",
    shell=(sys.platform == "win32"),
    env=env
)
processes.append(frontend_proc)
threading.Thread(target=log_stream, args=(frontend_proc.stdout, "[FRONTEND]"), daemon=True).start()

# 3. Buka browser otomatis setelah 3 detik
def auto_open_browser():
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

threading.Thread(target=auto_open_browser, daemon=True).start()

try:
    while True:
        time.sleep(1)
        for p in processes:
            if p.poll() is not None:
                cleanup()
except KeyboardInterrupt:
    cleanup()
