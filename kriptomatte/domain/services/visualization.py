import colorsys
import numpy as np
from typing import List, Tuple

class RandomColor:
    def __init__(self, init_sat, init_hue, init_luma=0.07):
        self.init_hue = init_hue
        self.init_sat = init_sat
        self.init_luma = init_luma
        self.update_counter = 0

    def update_hls(self):
        if self.update_counter % 3 == 2:
            self.init_hue = (self.init_hue + 0.04) % 1
        if self.update_counter % 3 == 1:
            self.init_sat = (self.init_sat + 0.14) % 1
        if self.update_counter % 3 == 0:
            self.init_luma = (self.init_luma + 0.07) % 0.5 + 0.07
        self.update_counter = self.update_counter + 1

    def random_color(self) -> List[int]:
        r, g, b = colorsys.hls_to_rgb(self.init_hue, self.init_luma, self.init_sat)
        rgb_256_int8 = []
        for color in [r, g, b]:
            color_in_numpy = np.array(color, dtype=np.float32)
            color_in_numpy = (np.clip(color_in_numpy * 255, 0, 255)).astype(np.uint8)
            col_list = int(color_in_numpy) # Convert to standard int
            rgb_256_int8.append(col_list)
        self.update_hls()
        return rgb_256_int8

class VisualizationService:
    @staticmethod
    def apply_random_colormap(mask_combined: np.ndarray) -> np.ndarray:
        """
        Applies random colors to the labeled mask.
        mask_combined: 2D array where each value corresponds to an object ID (0 is background).
        """
        # Original params: RandomColor(0, 0, 0.07)
        random_color_gen = RandomColor(0, 0, 0.07)
        
        num_objects = mask_combined.max() + 1
        # Background (0) is black
        colors = [[0, 0, 0]] + [random_color_gen.random_color() for _ in range(num_objects - 1)]
        
        # Use numpy take to map indices to colors
        # colors array shape: [NumObjects, 3]
        # mask_combined shape: [H, W]
        # result shape: [H, W, 3]
        mask_combined_rgb = np.take(colors, mask_combined, axis=0)
        
        return mask_combined_rgb.astype(np.uint8)
