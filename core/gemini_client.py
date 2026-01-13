"""
Gemini Client - Gemini Image Generation Client
Uses Imagen 4 via google.genai
"""

import os
import requests
import base64
from typing import Optional
from google import genai
from google.genai import types


class GeminiClient:
    """Gemini API Client for PPT image generation"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Client

        Args:
            api_key: Gemini API key, read from env var if not provided
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set, please check .env file")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "imagen-4.0-generate-001"  # Working model

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        style: str = "realistic"
    ) -> str:
        """
        Generate image using Gemini Imagen API

        Args:
            prompt: Image generation prompt
            aspect_ratio: Aspect ratio, default 16:9
            resolution: Resolution (2K/4K)
            style: Style

        Returns:
            Image base64 data
        """
        full_prompt = self._build_prompt(prompt, aspect_ratio, resolution, style)

        try:
            response = self.client.models.generate_images(
                model=self.model,
                prompt=full_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                )
            )

            # Parse response - Imagen 4 returns image bytes
            if response.generated_images and len(response.generated_images) > 0:
                img = response.generated_images[0].image
                # Check if it has bytes or preview image
                if hasattr(img, 'image_bytes') and img.image_bytes:
                    return base64.b64encode(img.image_bytes).decode('utf-8')
                elif hasattr(img, 'preview_image'):
                    return base64.b64encode(img.preview_image).decode('utf-8')
                else:
                    # Try to get raw bytes
                    return str(img)  # Fallback
            else:
                raise RuntimeError("No image in response")

        except Exception as e:
            raise RuntimeError(f"Gemini image generation failed: {str(e)}")

    def _build_prompt(
        self,
        base_prompt: str,
        aspect_ratio: str,
        resolution: str,
        style: str
    ) -> str:
        """Build full generation prompt"""
        return f"""Professional presentation slide: {base_prompt}

Style: {style}
Aspect Ratio: {aspect_ratio}
Resolution: {resolution}

Quality: High resolution, professional design, clean layout, suitable for business presentation.
Clean, modern, minimalist design with good typography and visual hierarchy."""

    def generate_slides(
        self,
        prompts: list[str],
        resolution: str = "2K",
        style: str = "realistic"
    ) -> list[str]:
        """
        Batch generate multiple slide images

        Args:
            prompts: Image prompt list
            resolution: Resolution
            style: Style

        Returns:
            Image base64 data list
        """
        images = []
        for i, prompt in enumerate(prompts):
            print(f"Generating slide {i+1}/{len(prompts)}...")
            try:
                image_result = self.generate_image(prompt, resolution=resolution, style=style)
                images.append(image_result)
            except Exception as e:
                print(f"Slide {i+1} failed: {str(e)}")
                images.append(None)

        return images

    def save_image(self, image_base64: str, filepath: str) -> None:
        """
        Save image to file

        Args:
            image_base64: Base64 image data
            filepath: Save path
        """
        try:
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',', 1)[1]

            image_data = base64.b64decode(image_base64)
            with open(filepath, "wb") as f:
                f.write(image_data)

            print(f"[SAVE] Image saved: {filepath}")

        except Exception as e:
            print(f"[ERROR] Failed to save image: {str(e)}")
