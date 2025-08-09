import time
from typing import Dict, Tuple, Any import numpy as np
import cv2 from emulator.melonds_launcher import launch_melonds, find_melonds_window, focus_window
from emulator.window_capture import WindowCapturer
from emulator.input_controller import InputController, load_keymap
from game.env_base import EnvBase
from game.reward_config import RewardConfigLoader class PokemonPlatinumEnv(EnvBase):
def init(
self,
melonds_exe: str,
rom_path: str,
keymap_path: str,
rewards_config_path: str | None = None,
frame_skip: int = 4,
stack_frames: int = 4,
action_space_n: int = 13,
focus_each_step: bool = True
):
self.melonds_exe = melonds_exe
self.rom_path = rom_path
self.proc = None
self.hwnd = None
self.capturer = None
self.frame_skip = frame_skip
self.stack_frames = stack_frames
self.frames = []
self.action_space_n = action_space_n
self.focus_each_step = focus_each_step
self.rcfg = RewardConfigLoader(rewards_config_path)
# input
self.keymap = load_keymap(keymap_path)
# movement ROI in preprocessed frame space will be whole frame for now
self.prev_obs = None
self.step_count = 0
def _ensure_emulator(self):
    if self.proc is None:
        self.proc = launch_melonds(self.melonds_exe, self.rom_path)
        time.sleep(2.0)
    if self.hwnd is None:
        self.hwnd = find_melonds_window("melonDS")
        if self.hwnd is None:
            raise RuntimeError("Unable to find melonDS window")
    if self.capturer is None:
        self.capturer = WindowCapturer(self.hwnd, use_dxcam=True, target_size=(84, 84))

def reset(self) -> np.ndarray:
    self._ensure_emulator()
    focus_window(self.hwnd)
    time.sleep(0.1)
    # warmup frames
    self.frames = []
    obs = self.capturer.capture()
    for _ in range(self.stack_frames):
        self.frames.append(obs.copy())
    self.prev_obs = obs.copy()
    self.step_count = 0
    return np.stack(self.frames, axis=0)

def _movement_reward(self, obs: np.ndarray) -> float:
    if self.prev_obs is None:
        self.prev_obs = obs.copy()
        return 0.0
    diff = cv2.absdiff((self.prev_obs * 255).astype(np.uint8), (obs * 255).astype(np.uint8))
    # sum normalized difference as proxy for movement
    mag = float(np.mean(diff) / 255.0)
    self.prev_obs = obs.copy()
    return mag * self.rcfg.cfg.move_reward_scale

def _compute_reward(self, obs: np.ndarray) -> Tuple[float, bool, Dict[str, Any]]:
    self.rcfg.maybe_reload(self.step_count)
    reward = self.rcfg.cfg.step_penalty
    done = False
    info: Dict[str, Any] = {}

    # Movement proxy
    reward += self._