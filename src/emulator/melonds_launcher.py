import subprocess
import time
import os
import win32gui
import win32con def launch_melonds(melonds_exe: str, rom_path: str | None = None) -> subprocess.Popen:
if not os.path.exists(melonds_exe):
raise FileNotFoundError(f"melonDS executable not found: {melonds_exe}")
args = [melonds_exe]
if rom_path:
args.append(rom_path)
proc = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
# Give melonDS time to open window
time.sleep(2.0)
return proc def find_melonds_window(title_hint: str = "melonDS") -> int | None:
hwnd_found = None
def enum_handler(hwnd, _):
nonlocal hwnd_found
if win32gui.IsWindowVisible(hwnd):
title = win32gui.GetWindowText(hwnd)
if title_hint.lower() in title.lower():
hwnd_found = hwnd
win32gui.EnumWindows(enum_handler, None)
return hwnd_found def focus_window(hwnd: int) -> None:
try:
win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
win32gui.SetForegroundWindow(hwnd)
except Exception:
# Best-effort; caller can retry
pass