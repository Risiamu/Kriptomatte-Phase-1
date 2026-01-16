import os
import logging
import numpy as np
from kriptomatte.domain.repositories import ImageRepository
from kriptomatte.domain.services.masking import MaskCompositionService
from kriptomatte.infrastructure.io.image_writer import ImageWriter

logger = logging.getLogger(__name__)

class CryptomatteExtractionService:
    def __init__(self, repo: ImageRepository):
        self.repo = repo

    def extract_all(self, file_path: str, output_dir: str | None = None):
        """
        Extracts all masks from the given EXR file.
        """
        if output_dir is None:
            output_dir = os.path.dirname(file_path)

        logger.info(f"Starting extraction for {file_path}")
        
        # 1. Reconstitute Aggregate
        try:
            exr_image = self.repo.load_header(file_path)
        except Exception as e:
            logger.error(f"Failed to load EXR header: {e}")
            raise

        base_name = os.path.splitext(os.path.basename(file_path))[0]

        for layer in exr_image.layers:
            logger.info(f"Processing layer: {layer.name}")
            
            # Create a folder for this layer
            layer_folder = os.path.join(output_dir, f"{base_name}_{layer.name}")
            os.makedirs(layer_folder, exist_ok=True)
            
            # 2. Load heavy data only when needed
            logger.info(f"Reading channels for {layer.name}")
            raw_data = self.repo.read_channels(file_path, layer.channel_names)
            
            # --- OPTIMIZATION START ---
            logger.info(f"Analyzing visible objects in {layer.name}...")
            
            # Cryptomatte channels are alternating: [ID, Coverage, ID, Coverage, ...]
            # We slice raw_data to get only the ID channels (indices 0, 2, 4, etc.)
            id_channels = raw_data[:, :, 0::2]
            
            # Get all unique IDs present in the actual pixels
            visible_ids = np.unique(id_channels)
            
            # Convert to a set for O(1) lookup speed
            visible_ids_set = set(visible_ids)
            logger.info(f"Found {len(visible_ids_set)} visible objects out of {len(layer.manifest)} in manifest.")
            # --- OPTIMIZATION END ---
            
            # 3. Domain logic to get masks
            # layer.manifest is Dict[str, float]
            # sort keys for deterministic order
            sorted_names = sorted(layer.manifest.keys())
            
            for obj_name in sorted_names:
                obj_id = layer.manifest[obj_name]
                
                # --- FAST CHECK ---
                # If the ID isn't in the pixel data, skip expensive computation entirely
                if obj_id not in visible_ids_set:
                    continue
                # ------------------
                
                # compute_mask returns [H, W] uint8
                mask = MaskCompositionService.compute_mask(obj_id, raw_data)
                
                # Optimization: check if empty (Double check, though visible_ids_set should handle 99% of cases)
                if mask.min() == mask.max():
                    logger.debug(f"Skipping empty mask for {obj_name}")
                    continue
                
                logger.info(f"Saving mask for {obj_name}")
                
                # 4. Save
                # Sanitize filename
                safe_name = "".join([c for c in obj_name if c.isalnum() or c in (' ', '.', '_')]).strip()
                save_path = os.path.join(layer_folder, f"{safe_name}_mask.png")
                
                ImageWriter.save_mask(save_path, mask)
                
        logger.info("Extraction complete.")
