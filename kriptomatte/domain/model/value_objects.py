from dataclasses import dataclass
from typing import Dict, List, Tuple
import ctypes
import struct

@dataclass(frozen=True)
class PixelWindow:
    height: int
    width: int

@dataclass(frozen=True)
class CryptoID:
    value: float

    def to_rgb(self) -> List[float]:
        """Converts the hashed id to a preview color."""
        bits = ctypes.cast(ctypes.pointer(ctypes.c_float(self.value)), ctypes.POINTER(ctypes.c_uint32)).contents.value
        mask = 2 ** 32 - 1
        return [0.0, float((bits << 8) & mask) / float(mask), float((bits << 16) & mask) / float(mask)]

    def to_hex(self) -> str:
        packed = struct.pack('=f', self.value)
        # Unpack as unsigned int to get hex representation
        unpacked = struct.unpack("=I", packed)[0]
        return f"{unpacked:08x}"

# Manifest is essentially a mapping of Object Name -> ID (float)
Manifest = Dict[str, float]
