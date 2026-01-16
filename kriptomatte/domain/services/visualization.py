import numpy as np

class BitwiseColorService:
    @staticmethod
    def encode_ids_to_rgb(id_map: np.ndarray) -> np.ndarray:
        """
        Converts a 2D array of Object IDs into a 3D RGB image using bitwise packing.

        Logic:
        - Red   = Lowest 8 bits
        - Green = Middle 8 bits
        - Blue  = Highest 8 bits

        Args:
            id_map: 2D numpy array (uint32 or int) of object IDs.

        Returns:
            np.ndarray: [H, W, 3] uint8 array ready to save as PNG.
        """
        # Ensure input is an integer type suitable for bitwise ops
        id_map = id_map.astype(np.uint32)

        # Vectorized bitwise extraction
        # We mask with 0xFF (255) to grab just that byte
        r = (id_map & 0xFF)
        g = (id_map >> 8) & 0xFF
        b = (id_map >> 16) & 0xFF

        # Stack into [Height, Width, 3]
        # astype(uint8) is critical for image saving
        rgb_image = np.stack((r, g, b), axis=-1).astype(np.uint8)

        return rgb_image

    @staticmethod
    def decode_rgb_to_ids(rgb_image: np.ndarray) -> np.ndarray:
        """
        Reverses the process: Converts an RGB image back into Object IDs.
        Useful for verification or reading the mask later.
        """
        rgb_image = rgb_image.astype(np.uint32)

        r = rgb_image[:, :, 0]
        g = rgb_image[:, :, 1]
        b = rgb_image[:, :, 2]

        # ID = R + (G * 256) + (B * 65536)
        return r + (g << 8) + (b << 16)
