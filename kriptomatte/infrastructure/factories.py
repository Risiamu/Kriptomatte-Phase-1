import json
import struct
import os
import logging
from typing import Dict, Any, Tuple
from kriptomatte.domain.model.value_objects import Manifest
from kriptomatte.infrastructure.io.file_system import FileSystem

logger = logging.getLogger(__name__)

class ManifestFactory:
    @staticmethod
    def create_from_metadata(metadata: Dict[str, Any], exr_file_path: str) -> Manifest:
        """
        Creates a Manifest domain object from the EXR metadata dictionary.
        Handles both embedded manifests and sidecar files.
        """
        raw_manifest = {}
        
        # Check for sidecar file
        manifest_file = metadata.get("manif_file")
        if manifest_file:
            if isinstance(manifest_file, bytes):
                manifest_file = manifest_file.decode('utf-8')
            
            logger.info(f"Side car manifest detected: {manifest_file}")
            full_path = FileSystem.resolve_path(exr_file_path, manifest_file)
            
            if full_path and os.path.exists(full_path):
                 with open(full_path, 'r') as json_data:
                    raw_manifest = json.load(json_data)
            else:
                logger.error(f"Cryptomatte: Unable to find manifest file: {full_path}")
                # Fallback to embedded if available? Original code didn't seem to fallback if file specified but missing
        
        # If no sidecar or failed, try embedded
        if not raw_manifest:
            manifest_bytes = metadata.get('manifest')
            if manifest_bytes:
                manifest_string = manifest_bytes.decode('utf-8')
                raw_manifest = json.loads(manifest_string)
            else:
                logger.warning("No manifest found in metadata.")
                return {}

        return ManifestFactory._parse_raw_manifest(raw_manifest)

    @staticmethod
    def _parse_raw_manifest(raw_manifest: Dict[str, str]) -> Manifest:
        """
        Converts the raw JSON manifest (Name -> HexString) to Domain Manifest (Name -> Float).
        """
        domain_manifest: Manifest = {}
        unpacker = struct.Struct('=f')
        packer = struct.Struct("=I")
        
        for name, hex_value in raw_manifest.items():
            # Original logic to convert hex string to float
            packed = packer.pack(int(hex_value, 16))
            # Ensure 4 bytes
            packed = b'\0' * (4 - len(packed)) + packed
            id_float = unpacker.unpack(packed)[0]
            
            # Ensure name is string
            name_str = name
            # original code did name.encode('utf-8') if str? wait.
            # "name_str = name if type(name) is str else name.encode("utf-8")"
            # It seems it wants bytes as keys in some parts, but Domain should use str.
            
            domain_manifest[name_str] = id_float
            
        return domain_manifest
