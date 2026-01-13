"""
GLM Client - GLM-4V API Client
用于图片生成、转场描述和内容优化
优先使用 GLM-4V 生成图片
"""

import os
import json
import re
import base64
from typing import Optional, Dict, Any, List
from zhipuai import ZhipuAI


class GLMClient:
    """GLM-4V API Client for image generation and auxiliary functions"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GLM Client

        Args:
            api_key: GLM API key, read from env var if not provided
        """
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
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        style: str = "realistic"
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

        full_prompt = self._build_image_prompt(prompt, aspect_ratio, resolution, style)

        try:
            # Try CogView-3 for image generation
            response = self.client.images.generations(
                model="cogview-3",  # GLM's image generation model
                prompt=full_prompt,
                size=self._get_image_size(aspect_ratio, resolution)
            )

            if response.data and len(response.data) > 0:
                # Return base64 of the image
                return response.data[0].b64_json
            else:
                return None

        except Exception as e:
            print(f"[GLM] Image generation failed: {str(e)}")
            return None

    def generate_images(
        self,
        prompts: List[str],
        resolution: str = "2K",
        style: str = "realistic",
        aspect_ratio: str = "16:9"
    ) -> List[Optional[str]]:
        """
        Batch generate images using GLM-4V

        Args:
            prompts: Image prompt list
            resolution: Resolution
            style: Style
            aspect_ratio: Aspect ratio

        Returns:
            Base64 image data list
        """
        images = []
        for i, prompt in enumerate(prompts):
            print(f"[GLM] Generating slide {i+1}/{len(prompts)}...")
            try:
                image_result = self.generate_image(
                    prompt=prompt,
                    resolution=resolution,
                    style=style,
                    aspect_ratio=aspect_ratio
                )
                images.append(image_result)
                if image_result:
                    print(f"[GLM] OK Slide {i+1} generated")
                else:
                    print(f"[GLM] FAIL Slide {i+1} failed")
            except Exception as e:
                print(f"[GLM] ERROR Slide {i+1}: {str(e)}")
                images.append(None)

        return images

    def _build_image_prompt(
        self,
        base_prompt: str,
        aspect_ratio: str,
        resolution: str,
        style: str
    ) -> str:
        """Build image generation prompt for GLM"""
        return f"""Professional presentation slide: {base_prompt}

Style: {style}
Aspect Ratio: {aspect_ratio}
Resolution: {resolution}

Quality Requirements:
- High resolution, professional quality
- Excellent composition and balance
- Clear, readable text if any
- Appropriate color scheme
- Modern, clean design suitable for business presentation
- Good visual hierarchy and typography"""

    def _get_image_size(self, aspect_ratio: str, resolution: str) -> str:
        """Map aspect ratio and resolution to GLM size"""
        # GLM-4V supports: "1024x1024", "768x1024", "1024x768", "512x512"
        resolution_map = {
            ("16:9", "2K"): "1344x768",
            ("16:9", "1080p"): "1024x576",
            ("16:9", "4K"): "2048x1152",
            ("4:3", "2K"): "1024x768",
            ("4:3", "1080p"): "768x576",
            ("1:1", "2K"): "768x768",
            ("1:1", "1080p"): "512x512",
        }
        return resolution_map.get((aspect_ratio, resolution), "1344x768")

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
                model="glm-4-flash",
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
            except:
                pass

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
                model="glm-4-flash",
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
                model="glm-4-flash",
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
