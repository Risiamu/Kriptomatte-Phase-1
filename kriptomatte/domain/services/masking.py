import numpy as np

class MaskCompositionService:
    @staticmethod
    def get_coverage_for_rank(float_id: float, combined_cryptomattes: np.ndarray, rank: int) -> np.ndarray:
        """
        Get the coverage mask for a given rank.
        combined_cryptomattes is [H, W, Channels] where Channels are R, G, B, A sequences.
        Rank 0 corresponds to channels 0 (ID) and 1 (Coverage).
        Rank 1 corresponds to channels 2 (ID) and 3 (Coverage).
        """
        # Ensure we don't go out of bounds
        if (rank * 2 + 1) >= combined_cryptomattes.shape[2]:
            return np.zeros((combined_cryptomattes.shape[0], combined_cryptomattes.shape[1]), dtype=np.float32)

        id_rank = combined_cryptomattes[:, :, rank * 2] == float_id
        coverage_rank = combined_cryptomattes[:, :, rank * 2 + 1] * id_rank

        return coverage_rank

    @staticmethod
    def compute_mask(obj_float_id: float, channels_arr: np.ndarray) -> np.ndarray:
        """
        Computes the mask for a specific object ID from the raw channel data.
        channels_arr: numpy array of shape [H, W, N_Channels]
        """
        # Calculate number of ranks (pairs of ID/Coverage)
        # Each rank is 2 channels.
        num_ranks = channels_arr.shape[2] // 2
        
        coverage_list = []
        for rank in range(num_ranks):
            coverage_rank = MaskCompositionService.get_coverage_for_rank(obj_float_id, channels_arr, rank)
            coverage_list.append(coverage_rank)
        
        if not coverage_list:
            return np.zeros((channels_arr.shape[0], channels_arr.shape[1]), dtype=np.uint8)

        coverage = sum(coverage_list)
        coverage = np.clip(coverage, 0.0, 1.0)
        mask = (coverage * 255).astype(np.uint8)
        return mask

    @staticmethod
    def combine_masks(masks: list[np.ndarray]) -> np.ndarray:
        """
        Simple combination for visualization or merging.
        (Note: The original get_combined_mask logic was more complex for ID mapping visualization)
        """
        if not masks:
            return np.array([]) # Return empty array if no masks
        total = np.zeros_like(masks[0])
        for m in masks:
            total = np.maximum(total, m)
        return total

    @staticmethod
    def combine_masks_with_ids(masks_with_ids: list[tuple[int, np.ndarray]]) -> np.ndarray:
        """
        Combines masks using the provided integer IDs.
        masks_with_ids: List of (id, mask). mask is uint8 coverage.
        Returns:
            mask_combined: uint32 array [H, W] with IDs.
        """
        if not masks_with_ids:
            return np.array([], dtype=np.uint32)

        first_mask = masks_with_ids[0][1]
        mask_combined = np.zeros_like(first_mask, dtype=np.uint32)
        best = np.zeros_like(first_mask) # Coverage tracker

        for id_val, obj_mask in masks_with_ids:
             # Update where current coverage is better
             mask_combined[obj_mask > best] = id_val
             best = np.maximum(best, obj_mask)
             
        return mask_combined

    @staticmethod
    def combine_masks_sequentially(obj_masks: list[tuple[str, np.ndarray]]) -> tuple[np.ndarray, dict]:
        """
        Combines masks into a single labeled image, preserving obstruction based on order and coverage.
        obj_masks: List of (object_name, mask_array). mask_array should be uint8 [H, W].
        Returns:
            mask_combined: uint16 array [H, W] with integer labels.
            name_to_id: Dict mapping object name to the integer label used in mask_combined.
        """
        if not obj_masks:
            return np.array([]), {}

        first_mask = obj_masks[0][1]
        mask_combined = np.zeros_like(first_mask, dtype=np.uint16)
        best = np.zeros_like(first_mask)
        name_to_mask_id_map = {}

        for idx, (obj_name, obj_mask) in enumerate(obj_masks):
            # ID starts at 1 (0 is background)
            label_id = idx + 1
            name_to_mask_id_map[obj_name] = label_id
            
            # Update label where this mask has higher coverage than previous best
            # Note: obj_mask is uint8 (0-255).
            mask_combined[obj_mask > best] = label_id
            
            # Update best coverage
            best = np.maximum(best, obj_mask)

        return mask_combined, name_to_mask_id_map
