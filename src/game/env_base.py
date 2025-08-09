from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
import numpy as np

class EnvBase(ABC):
    """Abstract base class for RL environments."""
    action_space_n: int

    @abstractmethod
    def reset(self) -> np.ndarray:
        """Reset the environment and return the initial observation."""
        pass

    @abstractmethod
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Take an action and return (observation, reward, done, info)."""
        pass