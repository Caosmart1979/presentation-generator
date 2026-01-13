"""
API Adapter - 统一的 API 接口层
提供 Gemini 和 GLM 的统一调用接口
"""

from .gemini_client import GeminiClient
from .glm_client import GLMClient

__all__ = ['GeminiClient', 'GLMClient']
