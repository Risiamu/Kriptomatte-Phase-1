import numpy as np
import colorsys

class VisualizationService:
    @staticmethod
    def generate_random_colors(num_colors: int) -> np.ndarray:
        """
        Generates N distinct colors using Golden Ratio sampling for Hue.
        Returns uint8 array of shape (num_colors, 3).
        """
        # 1. Generate distinct Hues using Golden Ratio
        # 0.61803398875 is the Golden Ratio Conjugate
        golden_ratio = 0.61803398875
        hues = (np.arange(num_colors) * golden_ratio) % 1.0

        # 2. Vary Saturation and Lightness to distinguish neighbors even more
        # We cycle S and L with different periods to avoid patterns
        saturations = 0.5 + (np.arange(num_colors) % 2) * 0.25  # 0.5 or 0.75
        lightness = 0.4 + (np.arange(num_colors) % 3) * 0.15    # 0.4, 0.55, or 0.7

        # 3. Vectorized HSV to RGB conversion
        # Since standard colorsys is scalar, we can use a fast vectorized approximation or loop
        # For N < 100k, a list comprehension with colorsys is plenty fast enough
        rgb_tuples = [
            colorsys.hls_to_rgb(h, l, s)
            for h, l, s in zip(hues, lightness, saturations)
        ]

        rgb_array = np.array(rgb_tuples, dtype=np.float32)
        return (rgb_array * 255).astype(np.uint8)

    @staticmethod
    def apply_random_colormap(mask_combined: np.ndarray) -> np.ndarray:
        """
        Applies random colors to the labeled mask.
        mask_combined: 2D array [H, W] with integer IDs (0..N).
        """
        # Ensure mask is integer
        mask_combined = mask_combined.astype(int)

        # 1. Identify amount of colors needed
        # (Assuming indices are contiguous 0..N. If sparse, use unique)
        max_id = mask_combined.max()
        if max_id == 0:
            # Handle all black/background case
            return np.zeros((*mask_combined.shape, 3), dtype=np.uint8)

        # 2. Generate Palette
        # We need max_id + 1 colors (index 0 is usually background)
        palette = VisualizationService.generate_random_colors(max_id + 1)

        # Set background (index 0) to Black explicitly
        palette[0] = [0, 0, 0]

        # 3. Map pixels to colors
        # numpy.take is extremely fast for this integer indexing
        colored_image = palette[mask_combined]

        return colored_image
