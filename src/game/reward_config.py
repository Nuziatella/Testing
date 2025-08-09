import json
import time
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional class TemplateCfg(BaseModel):
enable: bool = False
threshold: float = 0.85 class RewardConfig(BaseModel):
step_penalty: float = -0.01
move_reward_scale: float = 0.05
battle_event_reward: float = 0.5
money_delta_scale: float = 0.001
faint_penalty: float = -1.0
done_on_blackout: bool = False
clip_reward: bool = True
top_screen_roi: Tuple[int, int, int, int] = (0, 0, 256, 192)
templates: TemplateCfg = Field(default_factory=TemplateCfg)
hot_reload: bool = True
reload_interval_steps: int = 300 class RewardConfigLoader:
def init(self, path: str | None):
self.path = path
self.cfg = RewardConfig()
self.last_load_time = 0.0
self.load()
def load(self):
    if self.path:
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.cfg = RewardConfig(**data)
    self.last_load_time = time.time()

def maybe_reload(self, step_count: int):
    if not self.cfg.hot_reload or self.path is None:
        return
    if step_count % max(1, self.cfg.reload_interval_steps) == 0:
        try:
            self.load()
        except Exception:
            # keep previous config on errors
            pass