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
            return None
        total = np.zeros_like(masks[0])
        for m in masks:
            total = np.maximum(total, m)
        return total
