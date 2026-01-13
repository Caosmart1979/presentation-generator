"""
Image Utilities - 图片处理工具
提供统一的图片保存、编码、解码等功能
"""

import base64
from typing import Optional


def save_base64_image(image_base64: str, filepath: str) -> None:
    """
    保存 base64 编码的图片到文件

    Args:
        image_base64: Base64 编码的图片数据 (可能包含 data URL 前缀)
        filepath: 保存路径

    Raises:
        Exception: 保存失败时抛出异常
    """
    try:
        # 移除 data URL 前缀 (如 "data:image/png;base64,")
        if ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]

        # 解码并保存
        image_data = base64.b64decode(image_base64)
        with open(filepath, "wb") as f:
            f.write(image_data)

        print(f"[SAVE] Image saved: {filepath}")

    except base64.binascii.Error as e:
        raise Exception(f"Invalid base64 data: {str(e)}")
    except IOError as e:
        raise Exception(f"Failed to write file {filepath}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to save image: {str(e)}")


def encode_image_to_base64(filepath: str) -> str:
    """
    读取图片文件并编码为 base64

    Args:
        filepath: 图片文件路径

    Returns:
        Base64 编码的图片数据

    Raises:
        Exception: 读取或编码失败时抛出异常
    """
    try:
        with open(filepath, "rb") as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')

    except IOError as e:
        raise Exception(f"Failed to read file {filepath}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to encode image: {str(e)}")


def validate_base64_image(image_base64: str) -> bool:
    """
    验证 base64 字符串是否有效

    Args:
        image_base64: Base64 编码的图片数据

    Returns:
        是否有效
    """
    try:
        # 移除可能的 data URL 前缀
        if ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]

        # 尝试解码
        base64.b64decode(image_base64)
        return True

    except Exception:
        return False


def get_image_format_from_base64(image_base64: str) -> Optional[str]:
    """
    从 base64 数据中提取图片格式

    Args:
        image_base64: Base64 编码的图片数据 (可能包含 data URL)

    Returns:
        图片格式 (如 "png", "jpeg") 或 None
    """
    if image_base64.startswith('data:image/'):
        # 提取格式 "data:image/png;base64,..." -> "png"
        format_part = image_base64.split(';')[0]
        return format_part.split('/')[-1]

    return None


def add_data_url_prefix(image_base64: str, image_format: str = "png") -> str:
    """
    为 base64 数据添加 data URL 前缀

    Args:
        image_base64: Base64 编码的图片数据
        image_format: 图片格式 (默认 "png")

    Returns:
        带 data URL 前缀的 base64 数据
    """
    if image_base64.startswith('data:'):
        return image_base64

    return f"data:image/{image_format};base64,{image_base64}"


def remove_data_url_prefix(image_base64: str) -> str:
    """
    移除 base64 数据的 data URL 前缀

    Args:
        image_base64: 可能带 data URL 前缀的 base64 数据

    Returns:
        纯 base64 数据
    """
    if ',' in image_base64 and image_base64.startswith('data:'):
        return image_base64.split(',', 1)[1]

    return image_base64
