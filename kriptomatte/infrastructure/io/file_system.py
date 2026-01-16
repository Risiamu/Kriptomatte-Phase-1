import os
from pathlib import Path

class FileSystem:
    @staticmethod
    def create_folder(path: str) -> str:
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def resolve_path(base_path: str, relative_path: str) -> str:
        """Resolves a relative path against a base file path."""
        if "\\" in relative_path:
             # to enforce the specification from original code
             # "Cryptomatte: Invalid sidecar path (Back-slashes not allowed)"
             return "" 
        
        joined = os.path.join(os.path.dirname(base_path), relative_path)
        return os.path.normpath(joined)
