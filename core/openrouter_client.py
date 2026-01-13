"""
OpenRouter Client - OpenRouter API Client
Uses FLUX/Gemini-3 via OpenRouter
"""

import os
import base64
from typing import Optional, List
from openai import OpenAI

from core.config import ModelConfig, ResolutionConfig, GenerationConfig
from core.prompt_builder import ImagePromptBuilder


class OpenRouterClient:
    """OpenRouter API Client for PPT image generation (3rd fallback)"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter Client

        Args:
            api_key: OpenRouter API key, read from env var if not provided
        """
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
        model: str = None,
        size: str = None
    ) -> Optional[str]:
        """
        Generate image using OpenRouter

        Args:
            prompt: Image generation prompt
            model: Model ID (defaults to gemini-3-pro-image-preview)
            size: Image size

        Returns:
            Base64 image data, or None if failed
        """
        if not self.client:
            return None

        if model is None:
            model = self.model

        if size is None:
            size = ResolutionConfig.DEFAULT_SIZE

        full_prompt = ImagePromptBuilder.build_simple_prompt(prompt)

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

    def generate_images(
        self,
        prompts: List[str],
        resolution: str = GenerationConfig.DEFAULT_RESOLUTION,
        style: str = GenerationConfig.DEFAULT_STYLE,
        aspect_ratio: str = GenerationConfig.DEFAULT_ASPECT_RATIO
    ) -> List[Optional[str]]:
        """
        Batch generate images using OpenRouter

        Args:
            prompts: Image prompt list
            resolution: Resolution
            style: Style
            aspect_ratio: Aspect ratio

        Returns:
            Base64 image data list
        """
        images = []
        size = ResolutionConfig.get_size(aspect_ratio, resolution)

        for i, prompt in enumerate(prompts):
            print(f"[OPENROUTER] Generating slide {i+1}/{len(prompts)}...")
            try:
                # OpenRouter uses chat completions for image gen
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": ImagePromptBuilder.build_simple_prompt(prompt, style)}
                            ]
                        }
                    ],
                    max_tokens=2048
                )

                # Try to extract image from response
                image_data = self._extract_image_from_response(response)
                images.append(image_data)

                if image_data:
                    print(f"[OPENROUTER] OK Slide {i+1} generated")
                else:
                    print(f"[OPENROUTER] FAIL Slide {i+1} - no image in response")

            except Exception as e:
                print(f"[OPENROUTER] ERROR Slide {i+1}: {str(e)}")
                images.append(None)

        return images


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
