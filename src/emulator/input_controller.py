import time
import json
from typing import Dict, List import win32gui
import win32con
import win32api VK = {
"up": 0x26,
"down": 0x28,
"left": 0x25,
"right": 0x27,
"z": 0x5A,
"x": 0x58,
"a": 0x41,
"s": 0x53,
"q": 0x51,
"w": 0x57,
"return": 0x0D,
"rshift": 0xA1
} def load_keymap(path: str) -> Dict[str, str]:
with open(path, "r", encoding="utf-8") as f:
return json.load(f) def focus(hwnd: int):
try:
win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
win32gui.SetForegroundWindow(hwnd)
except Exception:
pass def key_down(vk: int):
win32api.keybd_event(vk, 0, 0, 0) def key_up(vk: int):
win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0) class InputController:
def init(self, hwnd: int, keymap: Dict[str, str], focus_before_send: bool = True, down_time: float = 0.04):
self.hwnd = hwnd
self.keymap = keymap
self.focus_before_send = focus_before_send
self.down_time = down_time
def press_keys(self, logical_keys: List[str]):
    if self.focus_before_send:
        focus(self.hwnd)
        time.sleep(0.01)
    vks = []
    for k in logical_keys:
        phys = self.keymap.get(k)
        if phys is None:
            continue
        vk = VK.get(phys)
        if vk is None:
            continue
        vks.append(vk)
    # Key down
    for vk in vks:
        key_down(vk)
    time.sleep(self.down_time)
    # Key up
    for vk in reversed(vks):
        key_up(vk)

def press_action(self, action_idx: int):
    # Map discrete action index to logical DS buttons
    # 0: noop, 1:UP,2:DOWN,3:LEFT,4:RIGHT,5:A,6:B,7:X,8:Y,9:L,10:R,11:START,12:SELECT
    mapping = {
        0: [],
        1: ["UP"], 2: ["DOWN"], 3: ["LEFT"], 4: ["RIGHT"],
        5: ["A"], 6: ["B"], 7: ["X"], 8: ["Y"],
        9: ["L"], 10: ["R"], 11: ["START"], 12: ["SELECT"]
    }
    self.press_keys(mapping.get(action_idx, []))