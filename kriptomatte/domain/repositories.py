from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np
from .model.aggregates import ExrImage

class ImageRepository(ABC):
    @abstractmethod
    def load_header(self, path: str) -> ExrImage:
        """
        Loads the header information and constructs the ExrImage aggregate root.
        This includes identifying all Cryptomatte layers and their manifests.
        """
        pass
    
    @abstractmethod
    def read_channels(self, path: str, channels: List[str]) -> np.ndarray:
        """
        Reads specific channels from the file.
        Returns a numpy array of shape [H, W, len(channels)].
        """
        pass
