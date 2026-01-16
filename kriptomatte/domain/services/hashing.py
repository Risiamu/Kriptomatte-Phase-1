import struct
from kriptomatte import pymmh3 as mmh3

class MurmurHashService:
    @staticmethod
    def hash_name_to_float(input_name: str) -> float:
        """
        Hashes a string name to a 32-bit float ID following the Cryptomatte specification.
        """
        hash_32 = mmh3.hash(input_name)
        exp = hash_32 >> 23 & 255
        if (exp == 0) or (exp == 255):
            hash_32 ^= 1 << 23

        packed = struct.pack('<L', hash_32 & 0xffffffff)
        return struct.unpack('<f', packed)[0]
