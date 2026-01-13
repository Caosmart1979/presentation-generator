"""
Base Image Client - Abstract base class for image generation clients
Provides common interface and functionality for all image generation clients
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from core.config import GenerationConfig


class BaseImageClient(ABC):
    """
    Abstract base class for image generation clients

    All image generation clients (Gemini, GLM, OpenRouter) should inherit from this class
    and implement the generate_image method.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize base client

        Args:
            api_key: API key for the service
        """
        self.api_key = api_key
        self.client = None  # Will be set by subclass

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = GenerationConfig.DEFAULT_ASPECT_RATIO,
        resolution: str = GenerationConfig.DEFAULT_RESOLUTION,
        style: str = GenerationConfig.DEFAULT_STYLE,
        **kwargs
    ) -> Optional[str]:
        """
        Generate a single image

        Args:
            prompt: Image generation prompt
            aspect_ratio: Aspect ratio (e.g., "16:9")
            resolution: Resolution (e.g., "2K", "4K")
            style: Style description
            **kwargs: Additional provider-specific arguments

        Returns:
            Base64 encoded image data, or None if generation failed
        """
        pass

    def generate_images(
        self,
        prompts: List[str],
        resolution: str = GenerationConfig.DEFAULT_RESOLUTION,
        style: str = GenerationConfig.DEFAULT_STYLE,
        aspect_ratio: str = GenerationConfig.DEFAULT_ASPECT_RATIO,
        **kwargs
    ) -> List[Optional[str]]:
        """
        Batch generate multiple images (default implementation)

        Args:
            prompts: List of image generation prompts
            resolution: Resolution
            style: Style description
            aspect_ratio: Aspect ratio
            **kwargs: Additional provider-specific arguments

        Returns:
            List of base64 encoded image data (None for failed generations)
        """
        images = []
        client_name = self.__class__.__name__

        for i, prompt in enumerate(prompts):
            print(f"[{client_name}] Generating slide {i+1}/{len(prompts)}...")
            try:
                image_result = self.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    style=style,
                    **kwargs
                )
                images.append(image_result)

                if image_result:
                    print(f"[{client_name}] OK Slide {i+1} generated")
                else:
                    print(f"[{client_name}] FAIL Slide {i+1} failed")

            except Exception as e:
                print(f"[{client_name}] ERROR Slide {i+1}: {str(e)}")
                images.append(None)

        return images

    def is_available(self) -> bool:
        """
        Check if the client is available (has valid configuration)

        Returns:
            True if client is available and ready to use
        """
        return self.client is not None

    def get_success_count(self, results: List[Optional[str]]) -> int:
        """
        Count successful generations in results

        Args:
            results: List of generation results

        Returns:
            Number of successful (non-None) results
        """
        return sum(1 for r in results if r is not None)

    def get_client_name(self) -> str:
        """
        Get the client name for logging

        Returns:
            Client class name
        """
        return self.__class__.__name__.replace('Client', '').upper()

    def __repr__(self) -> str:
        """String representation of the client"""
        return f"<{self.__class__.__name__} available={self.is_available()}>"
