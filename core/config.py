"""
Configuration Management - 统一配置管理
集中管理所有配置项，包括模型名称、分辨率映射等
"""

from typing import Dict, Tuple


class ModelConfig:
    """API 模型配置"""

    # Gemini Models
    GEMINI_IMAGE_MODEL = "imagen-4.0-generate-001"

    # GLM Models
    GLM_IMAGE_MODEL = "cogview-3"
    GLM_CHAT_MODEL = "glm-4-flash"

    # OpenRouter Models
    OPENROUTER_IMAGE_MODEL = "google/gemini-3-pro-image-preview"


class ResolutionConfig:
    """分辨率和尺寸映射配置"""

    # 分辨率映射表
    RESOLUTION_MAP: Dict[Tuple[str, str], str] = {
        # 16:9 比例
        ("16:9", "2K"): "1344x768",
        ("16:9", "1080p"): "1024x576",
        ("16:9", "4K"): "2048x1152",
        # 4:3 比例
        ("4:3", "2K"): "1024x768",
        ("4:3", "1080p"): "768x576",
        # 1:1 比例
        ("1:1", "2K"): "768x768",
        ("1:1", "1080p"): "512x512",
    }

    # 默认尺寸
    DEFAULT_SIZE = "1344x768"

    @classmethod
    def get_size(cls, aspect_ratio: str = "16:9", resolution: str = "2K") -> str:
        """
        获取图片尺寸

        Args:
            aspect_ratio: 宽高比
            resolution: 分辨率

        Returns:
            尺寸字符串 (如 "1344x768")
        """
        return cls.RESOLUTION_MAP.get((aspect_ratio, resolution), cls.DEFAULT_SIZE)


class GenerationConfig:
    """图片生成配置"""

    # 默认宽高比
    DEFAULT_ASPECT_RATIO = "16:9"

    # 默认分辨率
    DEFAULT_RESOLUTION = "2K"

    # 默认风格
    DEFAULT_STYLE = "realistic"

    # 生成超时 (秒)
    GENERATION_TIMEOUT = 60

    # 重试次数
    MAX_RETRIES = 3


class PromptConfig:
    """提示词配置"""

    # 质量要求描述
    QUALITY_REQUIREMENTS = """Quality Requirements:
- High resolution, professional quality
- Excellent composition and balance
- Clear, readable text if any
- Appropriate color scheme
- Modern, clean design suitable for business presentation
- Good visual hierarchy and typography"""

    # 风格描述模板
    STYLE_TEMPLATE = "Style: {style}"

    # 宽高比描述模板
    ASPECT_RATIO_TEMPLATE = "Aspect Ratio: {aspect_ratio}"

    # 分辨率描述模板
    RESOLUTION_TEMPLATE = "Resolution: {resolution}"
