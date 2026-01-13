"""
GLM Client - GLM-4V API Client
用于图片生成、转场描述和内容优化
优先使用 GLM-4V 生成图片
"""

import os
import json
import re
from typing import Optional, Dict, Any, List
from zhipuai import ZhipuAI

from core.base_client import BaseImageClient
from core.config import ModelConfig, ResolutionConfig, GenerationConfig
from core.prompt_builder import ImagePromptBuilder


class GLMClient(BaseImageClient):
    """GLM-4V API Client for image generation and auxiliary functions"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GLM Client

        Args:
            api_key: GLM API key, read from env var if not provided
        """
        super().__init__(api_key)
        self.api_key = api_key or os.getenv('GLM_API_KEY')
        if not self.api_key:
            print("[GLM] GLM_API_KEY not set, GLM features will be disabled")
            self.client = None
        else:
            self.client = ZhipuAI(api_key=self.api_key)

    # ========================================
    # Image Generation (GLM-4V)
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
        Generate image using GLM-4V / CogView

        Args:
            prompt: Image generation prompt
            aspect_ratio: Aspect ratio (16:9, 4:3, 1:1)
            resolution: Resolution (2K/4K/1080p)
            style: Style

        Returns:
            Base64 image data, or None if failed
        """
        if not self.client:
            return None

        full_prompt = ImagePromptBuilder.build_prompt(
            prompt, aspect_ratio, resolution, style
        )

        try:
            # Try CogView-3 for image generation
            response = self.client.images.generations(
                model=ModelConfig.GLM_IMAGE_MODEL,
                prompt=full_prompt,
                size=ResolutionConfig.get_size(aspect_ratio, resolution)
            )

            if response.data and len(response.data) > 0:
                # Return base64 of the image
                return response.data[0].b64_json
            else:
                return None

        except Exception as e:
            print(f"[GLM] Image generation failed: {str(e)}")
            return None



    # ========================================
    # Content Planning (GLM-4.7)
    # ========================================

    def generate_slide_plan(
        self,
        topic: str,
        page_count: int = 5
    ) -> Dict[str, Any]:
        """
        Generate PPT content plan from topic

        Args:
            topic: Presentation topic
            page_count: Number of pages

        Returns:
            Content plan dict with title and slides
        """
        if not self.client:
            return self._default_plan(topic, page_count)

        prompt = f"""Generate a {page_count}-page PPT content plan for:

Topic: {topic}

Generate structured content plan with:
1. Page type (cover/content/data/summary)
2. Page content (concise)

Return as JSON:
{{
  "title": "Presentation Title",
  "slides": [
    {{"page_type": "cover", "content": "Cover content"}},
    {{"page_type": "content", "content": "Content 1..."}}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=ModelConfig.GLM_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional presentation planner."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            content = response.choices[0].message.content
            return self._parse_plan_response(content)

        except Exception as e:
            print(f"[GLM] Plan generation failed, using default: {str(e)}")
            return self._default_plan(topic, page_count)

    def _parse_plan_response(self, content: str) -> Dict[str, Any]:
        """Parse plan response"""
        # Try to extract JSON
        json_match = re.search(r'\{[^{}]*"slides"[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e:
                print(f"[GLM] JSON parse failed: {e}")
            except Exception as e:
                print(f"[GLM] Unexpected error parsing JSON: {e}")

        # Fallback: create plan from content
        lines = [l.strip() for l in content.split('\n') if l.strip()]

        slides = []
        for i, line in enumerate(lines[:5]):  # Max 5 slides
            if i == 0:
                slides.append({"page_type": "cover", "content": line[:100]})
            else:
                slides.append({"page_type": "content", "content": line[:100]})

        return {
            "title": lines[0][:50] if lines else "Presentation",
            "slides": slides
        }

    # ========================================
    # Transition Description
    # ========================================

    def generate_transition(
        self,
        from_image: str,
        to_image: str,
        style: str = "professional"
    ) -> Dict[str, Any]:
        """Generate transition description between slides"""
        if not self.client:
            return self._fallback_transition(from_image, to_image)

        prompt = f"""Analyze these two PPT slides and generate transition description:

From: {from_image}
To: {to_image}
Style: {style}

Generate:
1. Transition type (fade, slide, zoom, particles, etc.)
2. Detailed transition description
3. Duration suggestion (1-3 seconds)
4. Key visual elements

Return as JSON."""

        try:
            response = self.client.chat.completions.create(
                model=ModelConfig.GLM_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional presentation transition designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            content = response.choices[0].message.content
            return self._parse_transition_response(content)

        except Exception as e:
            print(f"[GLM] Transition generation failed: {str(e)}")
            return self._fallback_transition(from_image, to_image)

    def _parse_transition_response(self, content: str) -> Dict[str, Any]:
        """Parse transition response"""
        return {
            "transition_type": "fade",
            "duration": "2.0",
            "description": content,
            "key_elements": [],
            "color_consistency": "auto"
        }

    def _fallback_transition(self, from_image: str, to_image: str) -> Dict[str, Any]:
        """Default transition"""
        return {
            "transition_type": "fade",
            "duration": "1.5",
            "description": "Fade transition effect",
            "key_elements": ["fade out", "fade in"],
            "color_consistency": "auto"
        }

    # ========================================
    # Content Optimization
    # ========================================

    def optimize_content(
        self,
        content: str,
        max_length: int = 50
    ) -> str:
        """Optimize PPT content for presentation"""
        if not self.client:
            return content

        prompt = f"""Optimize this PPT content for presentation:

Original: {content}

Requirements:
1. Concise, max {max_length} chars per point
2. Clear hierarchy
3. Keep core information
4. Suitable for verbal presentation

Return optimized content."""

        try:
            response = self.client.chat.completions.create(
                model=ModelConfig.GLM_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional presentation content editor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[GLM] Content optimization failed: {str(e)}")
            return content

    # ========================================
    # Default Plan
    # ========================================

    def _default_plan(self, topic: str, page_count: int) -> Dict[str, Any]:
        """Default content plan"""
        slides = []
        slides.append({"page_type": "cover", "content": topic})
        for i in range(page_count - 2):
            slides.append({"page_type": "content", "content": f"Point {i+1} about {topic}"})
        slides.append({"page_type": "summary", "content": f"{topic} Summary"})

        return {
            "title": topic[:50],
            "total_slides": page_count,
            "slides": slides
        }
