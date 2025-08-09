import time
from typing import Dict, Tuple, Any, Optional
import numpy as np
import cv2
from emulator.melonds_launcher import launch_melonds, find_melonds_window, focus_window
from emulator.window_capture import WindowCapturer
from emulator.input_controller import InputController, load_keymap
from game.env_base import EnvBase
from game.reward_config import RewardConfigLoader

class PokemonPlatinumEnv(EnvBase):
    """RL environment for Pokémon Platinum using melonDS emulator."""
    def __init__(
        self,
        melonds_exe: str,
        rom_path: str,
        keymap_path: str,
        rewards_config_path: Optional[str] = None,
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
        self.keymap = load_keymap(keymap_path)
        self.input_controller = None
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
        if self.input_controller is None:
            self.input_controller = InputController(self.hwnd, self.keymap, focus_before_send=self.focus_each_step)

    def reset(self) -> np.ndarray:
        """Reset the environment and return the initial stacked observation."""
        self._ensure_emulator()
        focus_window(self.hwnd)
        time.sleep(0.1)
        self.frames = []
        obs = self.capturer.capture()
        for _ in range(self.stack_frames):
            self.frames.append(obs.copy())
        self.prev_obs = obs.copy()
        self.step_count = 0
        return np.stack(self.frames, axis=0)

    def _movement_reward(self, obs: np.ndarray) -> float:
        """Calculate movement-based reward using frame difference."""
        if self.prev_obs is None:
            self.prev_obs = obs.copy()
            return 0.0
        diff = cv2.absdiff((self.prev_obs * 255).astype(np.uint8), (obs * 255).astype(np.uint8))
        mag = float(np.mean(diff) / 255.0)
        self.prev_obs = obs.copy()
        return mag * self.rcfg.cfg.move_reward_scale

    def _compute_reward(self, obs: np.ndarray) -> Tuple[float, bool, Dict[str, Any]]:
        """Compute reward, done flag, and info dict."""
        self.rcfg.maybe_reload(self.step_count)
        reward = self.rcfg.cfg.step_penalty
        done = False
        info: Dict[str, Any] = {}
        # Movement proxy
        reward += self._movement_reward(obs)
        # Additional reward logic can be added here
        return reward, done, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Take an action and return (observation, reward, done, info)."""
        self._ensure_emulator()
        for _ in range(self.frame_skip):
            self.input_controller.press_action(action)
            time.sleep(0.04)
        obs = self.capturer.capture()
        self.frames.pop(0)
        self.frames.append(obs.copy())
        stacked_obs = np.stack(self.frames, axis=0)
        reward, done, info = self._compute_reward(obs)
        self.step_count += 1
        return stacked_obs, reward, done, info
