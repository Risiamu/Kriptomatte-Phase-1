import OpenEXR
import Imath
import numpy as np
import re
import enum
import logging
from typing import List, Dict, Any, Tuple
from kriptomatte.domain.repositories import ImageRepository
from kriptomatte.domain.model.aggregates import ExrImage
from kriptomatte.domain.model.entities import CryptomatteLayer
from kriptomatte.domain.model.value_objects import PixelWindow
from kriptomatte.infrastructure.factories import ManifestFactory

logger = logging.getLogger(__name__)

class ExrDtype(enum.Enum):
    FLOAT32 = 0
    FLOAT16 = 1

pixel_dtype = {
    ExrDtype.FLOAT32: Imath.PixelType(Imath.PixelType.FLOAT),
    ExrDtype.FLOAT16: Imath.PixelType(Imath.PixelType.HALF),
}
numpy_dtype = {
    ExrDtype.FLOAT32: np.float32,
    ExrDtype.FLOAT16: np.float16,
}

CRYPTO_METADATA_LEGAL_PREFIX = ["exr/cryptomatte/", "cryptomatte/"]

class OpenExrRepository(ImageRepository):
    def load_header(self, path: str) -> ExrImage:
        logger.info(f"Opening EXR file: {path}")
        exr_file = OpenEXR.InputFile(path)
        header = exr_file.header()
        
        # Parse Window
        dw = header['dataWindow']
        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1
        window = PixelWindow(height=height, width=width)
        
        # Parse Layers
        layers = self._parse_layers(header, path)
        
        # We don't keep the OpenEXR file open in the aggregate, 
        # but we might need to re-open it for reading channels.
        # For now, we just return the aggregate.
        
        return ExrImage(
            file_path=path,
            header=dict(header), # Convert to dict to avoid pickling issues if any
            window=window,
            layers=layers
        )

    def read_channels(self, path: str, channels: List[str]) -> np.ndarray:
        exr_file = OpenEXR.InputFile(path)
        header = exr_file.header()
        
        # Get window shape for reshaping
        dw = header['dataWindow']
        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1
        shape = (height, width)
        
        read_channels_list = []
        for channel_name in channels:
            # Determine type
            chan_type = header['channels'][channel_name].type
            
            # Match to our internal enum
            exr_d = None
            for ed, pd in pixel_dtype.items():
                if pd == chan_type:
                    exr_d = ed
                    break
            
            if exr_d == ExrDtype.FLOAT16:
                np_type = np.float16
            else:
                np_type = np.float32
                
            channel_arr = np.frombuffer(exr_file.channel(channel_name), dtype=np_type)
            channel_arr = channel_arr.reshape(shape)
            
            # Cast to float32 if half float, as domain expects standard floats
            if np_type == np.float16:
                 channel_arr = channel_arr.astype(np.float32)
                 
            read_channels_list.append(channel_arr)
            
        return np.stack(read_channels_list, axis=-1)

    def _parse_layers(self, header: Any, path: str) -> List[CryptomatteLayer]:
        layers = []
        cryptomattes_meta = self._get_cryptomattes_from_header(header)
        
        for meta_id, meta_data in cryptomattes_meta.items():
            name = meta_data.get("name", meta_id)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            # Identify channels
            channels, naming_scheme = self._identify_channels(header, name)
            
            # Parse Manifest
            manifest = ManifestFactory.create_from_metadata(meta_data, path)
            
            layer = CryptomatteLayer(
                name=name,
                manifest=manifest,
                channel_names=channels,
                naming_scheme=naming_scheme,
                id_prefix=meta_id
            )
            layers.append(layer)
            
        return layers

    def _get_cryptomattes_from_header(self, exr_header):
        temp_cryptomattes = {}
        for key, value in exr_header.items():
            for prefix in CRYPTO_METADATA_LEGAL_PREFIX:
                if not key.startswith(prefix):
                    continue
                numbered_key = key[len(prefix):]
                
                # logic from original code
                parts = numbered_key.split("/")
                metadata_id = parts[0]
                partial_key = parts[1] if len(parts) > 1 else "" # Handle edge case if split fails?
                
                if metadata_id not in temp_cryptomattes:
                    temp_cryptomattes[metadata_id] = {}
                
                temp_cryptomattes[metadata_id][partial_key] = value
                temp_cryptomattes[metadata_id]['md_prefix'] = prefix
                break
        return temp_cryptomattes

    def _identify_channels(self, input_header, input_name):
        channel_list = list(input_header['channels'].keys())
        
        # regex for "cryptoObject" + digits + ending with .red or .r
        # Original: re.compile(r'({name}\d+)\.(red|r|R)$'.format(name=input_name))
        escaped_name = re.escape(input_name)
        channel_regex = re.compile(r'({name}\d+)\.(red|r|R)$'.format(name=escaped_name))
        
        pure_channels_prefixes = set() # Use set to avoid dupes then sort
        naming_scheme = "R"
        
        for channel in channel_list:
            match = channel_regex.match(channel)
            if match:
                pure_channels_prefixes.add(match.group(1))
                naming_scheme = match.group(2)
        
        sorted_prefixes = sorted(list(pure_channels_prefixes))
        
        # Now expand prefixes to full RGBA list
        full_channel_list = []
        
        # map scheme to suffixes
        suffixes = ["R", "G", "B", "A"]
        if naming_scheme == "r":
             suffixes = ["r", "g", "b", "a"]
        elif naming_scheme == "red":
             suffixes = ["red", "green", "blue", "alpha"]
             
        for prefix in sorted_prefixes:
            for suffix in suffixes:
                full_channel_list.append(f"{prefix}.{suffix}")
                
        return full_channel_list, naming_scheme
