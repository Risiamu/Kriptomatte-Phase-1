from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
from .value_objects import Manifest

@dataclass
class ObjectMask:
    name: str
    mask_data: np.ndarray  # Shape [H, W], dtype=uint8

@dataclass
class CryptomatteLayer:
    name: str
    manifest: Manifest
    channel_names: List[str]
    naming_scheme: str = "R"  # "R", "r", "red"
    
    # Metadata extracted from header
    id_prefix: str = ""
