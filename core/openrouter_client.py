"""
OpenRouter Client - OpenRouter API Client
Uses FLUX/Gemini-3 via OpenRouter
"""

import os
import base64
from typing import Optional, List
from openai import OpenAI

from core.base_client import BaseImageClient
from core.config import ModelConfig, ResolutionConfig, GenerationConfig
from core.prompt_builder import ImagePromptBuilder


class OpenRouterClient(BaseImageClient):
    """OpenRouter API Client for PPT image generation (3rd fallback)"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter Client

        Args:
            api_key: OpenRouter API key, read from env var if not provided
        """
        super().__init__(api_key)
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            print("[OPENROUTER] OPENROUTER_API_KEY not set, OpenRouter features will be disabled")
            self.client = None
        else:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key
            )
            self.model = ModelConfig.OPENROUTER_IMAGE_MODEL

    # ========================================
    # Image Generation
    # ========================================

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = GenerationConfig.DEFAULT_ASPECT_RATIO,
        resolution: str = GenerationConfig.DEFAULT_RESOLUTION,
        style: str = GenerationConfig.DEFAULT_STYLE,
        **kwargs
    ) -> Optional[str]:
        """
        Generate image using OpenRouter

        Args:
            prompt: Image generation prompt
            aspect_ratio: Aspect ratio
            resolution: Resolution
            style: Style description
            **kwargs: Additional arguments (model, size)

        Returns:
            Base64 image data, or None if failed
        """
        if not self.client:
            return None

        model = kwargs.get('model', self.model)
        size = kwargs.get('size', ResolutionConfig.get_size(aspect_ratio, resolution))

        full_prompt = ImagePromptBuilder.build_simple_prompt(prompt, style)

        try:
            response = self.client.responses.create(
                model=model,
                input=full_prompt
            )

            # Parse response for image data
            if hasattr(response, 'data') and len(response.data) > 0:
                item = response.data[0]
                # Check different response formats
                if hasattr(item, 'url'):
                    # If URL returned, download and encode
                    return self._download_and_encode_url(item.url)
                elif hasattr(item, 'b64_json'):
                    return item.b64_json

            return None

        except Exception as e:
            print(f"[OPENROUTER] Image generation failed: {str(e)}")
            return None



    def _extract_image_from_response(self, response) -> Optional[str]:
        """Extract image data from OpenRouter response"""
        try:
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content
                    # Check if content is a URL
                    if content and content.startswith('http'):
                        return self._download_and_encode_url(content)
                    # Check if content is base64 data URL
                    if content and content.startswith('data:image'):
                        return content.split(',', 1)[1]
            return None
        except Exception as e:
            print(f"[OPENROUTER] Failed to extract image: {str(e)}")
            return None

    def _download_and_encode_url(self, url: str) -> Optional[str]:
        """Download image from URL and encode as base64"""
        try:
            import requests
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode('utf-8')
            return None
        except Exception as e:
            print(f"[OPENROUTER] Failed to download image: {str(e)}")
            return None
