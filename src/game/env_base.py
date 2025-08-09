from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple import numpy as np class EnvBase(ABC):
action_space_n: int
@abstractmethod
def reset(self) -> np.ndarray:
    ...

@abstractmethod
def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
    ...