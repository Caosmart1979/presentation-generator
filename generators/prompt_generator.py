"""
Prompt Generator - 提示词生成器
根据内容和风格生成图片生成提示词
"""

import os
from typing import List, Dict, Any


class PromptGenerator:
    """提示词生成器"""

    def __init__(self):
        """初始化提示词生成器"""
        self.prompts_dir = os.path.join(
            os.path.dirname(__file__),
            "../config/prompts"
        )

    def generate_prompts(
        self,
        slides_plan: Dict[str, Any],
        style_config: Dict[str, Any],
        resolution: str = "2K"
    ) -> List[str]:
        """
        为每页生成图片提示词

        Args:
            slides_plan: 内容规划
            style_config: 风格配置
            resolution: 分辨率

        Returns:
            提示词列表
        """
        prompts = []

        for slide in slides_plan.get('slides', []):
            page_type = slide.get('page_type', 'content')
            content = slide.get('content', '')

            prompt = self._generate_single_prompt(
                page_type=page_type,
                content=content,
                style_config=style_config,
                resolution=resolution
            )

            prompts.append(prompt)

        return prompts

    def _generate_single_prompt(
        self,
        page_type: str,
        content: str,
        style_config: Dict[str, Any],
        resolution: str
    ) -> str:
        """生成单个页面的提示词"""
        # 获取风格模板
        template = style_config.get('templates', {}).get(page_type)

        if template:
            # 使用风格模板
            prompt = template.replace("{content}", content)
            prompt = prompt.replace("{resolution}", resolution)
        else:
            # 使用默认模板
            prompt = self._default_prompt(page_type, content, resolution)

        return prompt

    def _default_prompt(self, page_type: str, content: str, resolution: str) -> str:
        """默认提示词模板"""
        if page_type == "cover":
            return f"""Create a professional presentation cover page with:

TITLE: {content}

Style Requirements:
- Modern, professional design
- Clean typography with large, bold title
- High-quality visual aesthetic
- 16:9 aspect ratio
- Resolution: {resolution}

Design Elements:
- Centered composition
- Strong visual hierarchy
- Eye-catching but professional
- Suitable for business or academic presentation"""
        elif page_type == "content":
            return f"""Create a professional presentation content page with:

CONTENT: {content}

Style Requirements:
- Clean, readable layout
- Good visual hierarchy
- Professional design
- 16:9 aspect ratio
- Resolution: {resolution}

Layout:
- Content organized in clear sections
- Good spacing and readability
- Professional typography
- Suitable for presentation"""
        elif page_type == "summary":
            return f"""Create a professional presentation summary page with:

CONTENT: {content}

Style Requirements:
- Clean, impactful conclusion
- Professional design
- 16:9 aspect ratio
- Resolution: {resolution}

Layout:
- Centered content
- Clear conclusion or call-to-action
- Professional and memorable"""
        else:
            return f"""Create a professional presentation slide with: {content}

Style: Professional, modern, clean design
Aspect Ratio: 16:9
Resolution: {resolution}"""
