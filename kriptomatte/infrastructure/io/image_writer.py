from PIL import Image
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class ImageWriter:
    @staticmethod
    def save_mask(path: str, mask: np.ndarray):
        """
        Saves a mask (uint8 numpy array) to disk.
        """
        logger.debug(f"Saving mask to {path}. Mask shape: {mask.shape}, dtype: {mask.dtype}")
        
        # Ensure directory exists
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            logger.debug(f"Creating directory: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
        
        # Original code did this:
        # object_crypto_mask = np.repeat(np.expand_dims(object_crypto_mask, axis=2), 4, axis=2)
        # crypto_mask_image = Image.fromarray(object_crypto_mask, mode='RGBA')
        
        # If it's a single channel mask [H, W], make it RGBA?
        # The user might want just the mask (L) or RGBA.
        # Following original logic:
        try:
            if mask.ndim == 2:
                img = Image.fromarray(mask, mode='L')
                img.save(path)
            elif mask.ndim == 3 and mask.shape[2] == 3:
                img = Image.fromarray(mask, mode='RGB')
                img.save(path)
            elif mask.ndim == 3 and mask.shape[2] == 4:
                img = Image.fromarray(mask, mode='RGBA')
                img.save(path)
            else:
                logger.warning(f"Unknown mask shape {mask.shape}, trying to save anyway")
                Image.fromarray(mask).save(path)
            
            logger.info(f"Saved mask to {path}")
        except Exception as e:
            logger.error(f"Failed to save image to {path}: {e}")
            raise
