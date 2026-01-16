from dataclasses import dataclass, field
from typing import List, Dict, Any
from .entities import CryptomatteLayer
from .value_objects import PixelWindow

@dataclass
class ExrImage:
    """
    Aggregate Root for an EXR file containing Cryptomatte data.
    """
    file_path: str
    header: Dict[str, Any]
    window: PixelWindow
    layers: List[CryptomatteLayer] = field(default_factory=list)

    def get_layer(self, layer_name: str) -> CryptomatteLayer:
        for layer in self.layers:
            if layer.name == layer_name:
                return layer
        raise ValueError(f"Layer {layer_name} not found in {self.file_path}")
