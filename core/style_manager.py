"""
Style Manager - 风格管理器
加载和管理 PPT 风格配置
"""

import os
import json
from typing import Dict, Any


class StyleManager:
    """风格管理器"""

    def __init__(self):
        """初始化风格管理器"""
        self.styles_dir = os.path.join(
            os.path.dirname(__file__),
            "../config/styles"
        )
        self._cache = {}

    def load_style(self, style_name: str) -> Dict[str, Any]:
        """
        加载风格配置

        Args:
            style_name: 风格名称

        Returns:
            风格配置字典
        """
        if style_name in self._cache:
            return self._cache[style_name]

        style_path = os.path.join(self.styles_dir, f"{style_name}.md")

        if not os.path.exists(style_path):
            print(f"警告: 风格 '{style_name}' 不存在，使用默认风格")
            return self._default_style()

        with open(style_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析风格文件
        style_config = self._parse_style_file(content, style_name)
        self._cache[style_name] = style_config

        return style_config

    def _parse_style_file(self, content: str, style_name: str) -> Dict[str, Any]:
        """解析风格文件"""
        # 这里简化处理，实际可以更精确地解析 Markdown
        lines = content.split('\n')

        config = {
            "name": style_name,
            "description": "",
            "templates": {}
        }

        current_section = None
        current_template = []

        for line in lines:
            if line.startswith("## "):
                # 新的章节
                if current_section and current_template:
                    template_text = "\n".join(current_template)
                    config["templates"][current_section] = template_text

                current_section = line[3:].strip().lower()
                current_template = []

            elif line.strip() and current_section:
                current_template.append(line)

        # 添加最后一个模板
        if current_section and current_template:
            template_text = "\n".join(current_template)
            config["templates"][current_section] = template_text

        return config

    def _default_style(self) -> Dict[str, Any]:
        """默认风格配置"""
        return {
            "name": "default",
            "description": "默认专业风格",
            "templates": {
                "cover": "Create a professional presentation cover with title: {content}. Style: Modern, clean, professional.",
                "content": "Create a professional presentation content page with: {content}. Style: Clean, readable, professional.",
                "data": "Create a professional presentation data page with: {content}. Style: Clear data visualization.",
                "summary": "Create a professional presentation summary page with: {content}. Style: Clean, impactful conclusion."
            }
        }

    def list_styles(self) -> list[str]:
        """列出所有可用风格"""
        if not os.path.exists(self.styles_dir):
            return ["default"]

        styles = []
        for file in os.listdir(self.styles_dir):
            if file.endswith(".md"):
                styles.append(file[:-3])

        return styles if styles else ["default"]
