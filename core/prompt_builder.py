"""
Prompt Builder - 提示词构建器
提供统一的图片生成提示词构建功能
"""

from typing import Optional
from core.config import PromptConfig, GenerationConfig


class ImagePromptBuilder:
    """统一的图片生成提示词构建器"""

    @staticmethod
    def build_prompt(
        base_prompt: str,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        style: Optional[str] = None,
        include_quality_requirements: bool = True
    ) -> str:
        """
        构建完整的图片生成提示词

        Args:
            base_prompt: 基础提示词内容
            aspect_ratio: 宽高比 (如 "16:9")
            resolution: 分辨率 (如 "2K", "4K")
            style: 风格描述
            include_quality_requirements: 是否包含质量要求

        Returns:
            完整的提示词
        """
        # 使用默认值
        aspect_ratio = aspect_ratio or GenerationConfig.DEFAULT_ASPECT_RATIO
        resolution = resolution or GenerationConfig.DEFAULT_RESOLUTION
        style = style or GenerationConfig.DEFAULT_STYLE

        # 构建提示词各部分
        parts = [
            f"Professional presentation slide: {base_prompt}",
            "",
            PromptConfig.STYLE_TEMPLATE.format(style=style),
            PromptConfig.ASPECT_RATIO_TEMPLATE.format(aspect_ratio=aspect_ratio),
            PromptConfig.RESOLUTION_TEMPLATE.format(resolution=resolution),
        ]

        # 添加质量要求
        if include_quality_requirements:
            parts.extend(["", PromptConfig.QUALITY_REQUIREMENTS])

        return "\n".join(parts)

    @staticmethod
    def build_simple_prompt(
        base_prompt: str,
        style: Optional[str] = None
    ) -> str:
        """
        构建简化版提示词 (用于某些 API)

        Args:
            base_prompt: 基础提示词内容
            style: 风格描述

        Returns:
            简化的提示词
        """
        style = style or GenerationConfig.DEFAULT_STYLE

        return f"""Professional presentation slide: {base_prompt}

Create a high-quality, professional presentation slide with:
- Clean, modern design
- Excellent composition and balance
- Clear visual hierarchy
- Professional color scheme
- Suitable for business presentation
- 16:9 aspect ratio

Quality: High resolution, professional design, clean layout."""

    @staticmethod
    def enhance_prompt_with_style(
        base_prompt: str,
        style_description: str
    ) -> str:
        """
        使用自定义风格描述增强提示词

        Args:
            base_prompt: 基础提示词
            style_description: 自定义风格描述

        Returns:
            增强后的提示词
        """
        return f"""{base_prompt}

Additional Style Requirements:
{style_description}"""

    @staticmethod
    def extract_keywords(prompt: str, max_keywords: int = 5) -> list:
        """
        从提示词中提取关键词 (简化实现)

        Args:
            prompt: 提示词
            max_keywords: 最大关键词数量

        Returns:
            关键词列表
        """
        # 简单实现：提取大写开头的词
        import re
        words = re.findall(r'\b[A-Z][a-z]+\b', prompt)
        return words[:max_keywords]
