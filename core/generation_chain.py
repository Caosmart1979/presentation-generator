"""
Image Generation Chain - Responsibility Chain Pattern for fallback logic
Simplifies multi-level fallback by trying clients in order until all images succeed
"""

from typing import List, Optional
from core.base_client import BaseImageClient


class ImageGenerationChain:
    """
    Manages image generation with automatic fallback between multiple clients

    Uses the Chain of Responsibility pattern to try clients in order,
    filling in failed images with subsequent clients until all succeed or all fail.
    """

    def __init__(self, clients: List[BaseImageClient]):
        """
        Initialize generation chain with ordered list of clients

        Args:
            clients: List of image clients in priority order
                    (e.g., [glm_client, gemini_client, openrouter_client])
        """
        self.clients = [c for c in clients if c.is_available()]

        if not self.clients:
            print("[CHAIN] Warning: No available clients in chain")

    def generate_images(
        self,
        prompts: List[str],
        resolution: str = "2K",
        style: str = "realistic",
        aspect_ratio: str = "16:9"
    ) -> List[Optional[str]]:
        """
        Generate images with automatic fallback

        Tries each client in order, filling in failed images with subsequent clients.
        Returns when all images succeed or all clients have been tried.

        Args:
            prompts: List of image generation prompts
            resolution: Resolution (e.g., "2K", "4K")
            style: Style description
            aspect_ratio: Aspect ratio (e.g., "16:9")

        Returns:
            List of base64 image data (None for failed generations)
        """
        if not self.clients:
            print("[CHAIN] No available clients, returning all None")
            return [None] * len(prompts)

        # Initialize results with None
        results = [None] * len(prompts)

        print(f"\n[CHAIN] Starting generation chain with {len(self.clients)} clients")
        print(f"[CHAIN] Clients: {[c.get_client_name() for c in self.clients]}")

        # Try each client in order
        for level, client in enumerate(self.clients, 1):
            client_name = client.get_client_name()

            # Find which images still need generation
            pending_indices = [i for i, r in enumerate(results) if r is None]

            if not pending_indices:
                print(f"[CHAIN] All images generated successfully at level {level}")
                break

            print(f"\n[CHAIN] Level {level}: Trying {client_name}")
            print(f"[CHAIN] Pending: {len(pending_indices)}/{len(prompts)} images")

            # Generate only pending images
            pending_prompts = [prompts[i] for i in pending_indices]

            try:
                pending_results = client.generate_images(
                    prompts=pending_prompts,
                    resolution=resolution,
                    style=style,
                    aspect_ratio=aspect_ratio
                )

                # Fill in successful results
                for i, result in zip(pending_indices, pending_results):
                    if result is not None:
                        results[i] = result

                # Report progress
                success_count = client.get_success_count(results)
                print(f"[CHAIN] Level {level} complete: {success_count}/{len(prompts)} total succeeded")

            except Exception as e:
                print(f"[CHAIN] Level {level} ({client_name}) failed: {str(e)}")
                continue

        # Final report
        final_success = sum(1 for r in results if r is not None)
        print(f"\n[CHAIN] Generation complete: {final_success}/{len(prompts)} images succeeded")

        if final_success < len(prompts):
            failed_indices = [i+1 for i, r in enumerate(results) if r is None]
            print(f"[CHAIN] Failed slides: {failed_indices}")

        return results

    def generate_single_image(
        self,
        prompt: str,
        resolution: str = "2K",
        style: str = "realistic",
        aspect_ratio: str = "16:9"
    ) -> Optional[str]:
        """
        Generate a single image with fallback

        Args:
            prompt: Image generation prompt
            resolution: Resolution
            style: Style description
            aspect_ratio: Aspect ratio

        Returns:
            Base64 image data, or None if all clients failed
        """
        for client in self.clients:
            client_name = client.get_client_name()
            print(f"[CHAIN] Trying {client_name} for single image...")

            try:
                result = client.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    style=style
                )

                if result is not None:
                    print(f"[CHAIN] Success with {client_name}")
                    return result
                else:
                    print(f"[CHAIN] {client_name} failed, trying next...")

            except Exception as e:
                print(f"[CHAIN] {client_name} error: {str(e)}")
                continue

        print("[CHAIN] All clients failed for single image")
        return None

    def get_available_clients(self) -> List[str]:
        """
        Get list of available client names

        Returns:
            List of client names
        """
        return [c.get_client_name() for c in self.clients]

    def has_available_clients(self) -> bool:
        """
        Check if any clients are available

        Returns:
            True if at least one client is available
        """
        return len(self.clients) > 0
