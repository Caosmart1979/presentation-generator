# 代码优化分析报告

## 项目概述
Presentation Generator - AI 驱动的 PPT 生成器，使用 Gemini、GLM 和 OpenRouter 等多个 API。

## 发现的优化空间

### 1. 代码重复问题 (高优先级)

#### 1.1 图片提示词构建重复
**位置**:
- `gemini_client.py:79-94` (_build_prompt)
- `glm_client.py:118-138` (_build_image_prompt)
- `openrouter_client.py:138-150` (_build_image_prompt)

**问题**: 三个客户端都有几乎相同的提示词构建逻辑

**建议**: 创建一个基类或工具函数来统一管理提示词构建

```python
# 建议添加: core/prompt_builder.py
class ImagePromptBuilder:
    @staticmethod
    def build_prompt(base_prompt: str, aspect_ratio: str,
                     resolution: str, style: str) -> str:
        """统一的提示词构建逻辑"""
        return f"""Professional presentation slide: {base_prompt}

Style: {style}
Aspect Ratio: {aspect_ratio}
Resolution: {resolution}

Quality: High resolution, professional design, clean layout,
suitable for business presentation."""
```

#### 1.2 图片尺寸映射重复
**位置**:
- `glm_client.py:140-152` (_get_image_size)
- `openrouter_client.py:152-163` (_get_image_size)
- `ppt_generator.py:331-338` (_get_size_for_openrouter)

**问题**: 分辨率映射逻辑在多处重复定义

**建议**: 创建配置文件或常量类

```python
# 建议添加: core/config.py
class ResolutionConfig:
    RESOLUTION_MAP = {
        ("16:9", "2K"): "1344x768",
        ("16:9", "1080p"): "1024x576",
        ("16:9", "4K"): "2048x1152",
        ("4:3", "2K"): "1024x768",
        ("4:3", "1080p"): "768x576",
        ("1:1", "2K"): "768x768",
        ("1:1", "1080p"): "512x512",
    }

    @classmethod
    def get_size(cls, aspect_ratio: str, resolution: str) -> str:
        return cls.RESOLUTION_MAP.get((aspect_ratio, resolution), "1344x768")
```

#### 1.3 图片保存逻辑重复
**位置**:
- `gemini_client.py:125-145` (save_image)
- `ppt_generator.py:340-356` (_save_image)

**问题**: 相同的 base64 解码和保存逻辑出现两次

**建议**: 统一到一个工具模块

```python
# 建议添加: core/image_utils.py
def save_base64_image(image_base64: str, filepath: str) -> None:
    """统一的图片保存逻辑"""
    import base64

    if ',' in image_base64:
        image_base64 = image_base64.split(',', 1)[1]

    image_data = base64.b64decode(image_base64)
    with open(filepath, "wb") as f:
        f.write(image_data)
```

### 2. 复杂的回退逻辑 (中优先级)

#### 2.1 多层回退逻辑可以简化
**位置**: `ppt_generator.py:178-272`

**问题**:
- 回退逻辑嵌套过深
- `_fill_gaps_with_fallback` 和 `_fill_gaps_with_openrouter` 逻辑重复

**建议**: 使用责任链模式简化

```python
# 建议重构为:
class ImageGenerationChain:
    def __init__(self, clients: List[ImageClient]):
        self.clients = clients

    def generate_images(self, prompts, resolution, style):
        results = [None] * len(prompts)

        for client in self.clients:
            if not client.is_available():
                continue

            # 尝试生成所有失败的图片
            for i, result in enumerate(results):
                if result is None:
                    results[i] = client.generate_image(prompts[i], resolution, style)

            # 如果全部成功，提前返回
            if all(r is not None for r in results):
                return results

        return results
```

### 3. 类型注解不一致 (低优先级)

**问题**: 混用 `list[str]` 和 `List[str]`

**位置**:
- `gemini_client.py:98` 使用 `list[str]`
- `glm_client.py:80` 使用 `List[str]`

**建议**: 统一使用 `from typing import List` 或升级到 Python 3.9+ 并全部使用小写

### 4. 配置管理问题 (中优先级)

#### 4.1 API 模型名称硬编码
**位置**:
- `gemini_client.py:29` - "imagen-4.0-generate-001"
- `glm_client.py:63` - "cogview-3"
- `glm_client.py:195` - "glm-4-flash"
- `openrouter_client.py:31` - "google/gemini-3-pro-image-preview"

**建议**: 集中配置管理

```python
# 建议添加: core/config.py
class ModelConfig:
    GEMINI_IMAGE_MODEL = "imagen-4.0-generate-001"
    GLM_IMAGE_MODEL = "cogview-3"
    GLM_CHAT_MODEL = "glm-4-flash"
    OPENROUTER_MODEL = "google/gemini-3-pro-image-preview"
```

### 5. 错误处理改进 (中优先级)

#### 5.1 JSON 解析错误处理
**位置**: `glm_client.py:210-218`

**问题**: 使用裸 `except: pass`，吞掉所有错误

**建议**: 具体化异常处理

```python
def _parse_plan_response(self, content: str) -> Dict[str, Any]:
    json_match = re.search(r'\{[^{}]*"slides"[^{}]*\}', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"[GLM] JSON parse failed: {e}")
        except Exception as e:
            print(f"[GLM] Unexpected error: {e}")

    return self._parse_fallback_plan(content)
```

### 6. 代码结构优化 (低优先级)

#### 6.1 默认计划逻辑重复
**位置**:
- `glm_client.py:345-357` (_default_plan)
- `ppt_generator.py:358-380` (_generate_slides_plan 的 else 分支)

**问题**: 相同的默认计划生成逻辑出现两次

**建议**: 提取到共享工具函数

#### 6.2 导入优化
**位置**: 多个文件中 `base64` 在函数内部导入

**建议**: 统一在文件顶部导入

```python
# 当前 (ppt_generator.py:342):
def _save_image(self, image_base64: str, filepath: str) -> None:
    import base64  # 函数内导入

# 建议:
import base64  # 文件顶部导入
```

### 7. 性能优化建议 (低优先级)

#### 7.1 风格文件缓存
**位置**: `style_manager.py:20-48`

**优点**: 已经实现了缓存机制 ✓

**可能改进**: 考虑使用 LRU 缓存限制内存使用

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def load_style(self, style_name: str) -> Dict[str, Any]:
    # ...
```

## 优化优先级总结

### 高优先级 (建议立即优化)
1. **代码重复消除** - 减少维护成本
   - 统一提示词构建
   - 统一图片尺寸映射
   - 统一图片保存逻辑

### 中优先级 (建议近期优化)
2. **回退逻辑简化** - 提高可读性
3. **配置集中管理** - 便于维护和修改
4. **错误处理改进** - 增强健壮性

### 低优先级 (可选优化)
5. **类型注解统一** - 代码一致性
6. **代码结构优化** - 小幅改进
7. **性能优化** - 边际收益

## 潜在重构建议

### 建议的新文件结构
```
core/
├── __init__.py
├── api_adapter.py
├── config.py           # 新增: 统一配置管理
├── image_utils.py      # 新增: 图片处理工具
├── prompt_builder.py   # 新增: 提示词构建
├── base_client.py      # 新增: 客户端基类
├── gemini_client.py
├── glm_client.py
├── openrouter_client.py
└── style_manager.py
```

### 基类抽象建议

```python
# core/base_client.py
from abc import ABC, abstractmethod

class BaseImageClient(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None

    @abstractmethod
    def generate_image(self, prompt: str, **kwargs) -> Optional[str]:
        """生成单张图片"""
        pass

    def generate_images(self, prompts: List[str], **kwargs) -> List[Optional[str]]:
        """批量生成图片 - 通用实现"""
        images = []
        for i, prompt in enumerate(prompts):
            try:
                image_result = self.generate_image(prompt, **kwargs)
                images.append(image_result)
            except Exception as e:
                print(f"[{self.__class__.__name__}] Slide {i+1} failed: {e}")
                images.append(None)
        return images

    def is_available(self) -> bool:
        """检查客户端是否可用"""
        return self.client is not None
```

## 代码质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | 9/10 | 功能完善，三层回退机制 |
| 代码复用 | 6/10 | 存在较多重复代码 |
| 可维护性 | 7/10 | 结构清晰但有改进空间 |
| 错误处理 | 7/10 | 基本覆盖但不够精细 |
| 代码规范 | 8/10 | 整体规范，少数不一致 |
| 性能 | 8/10 | 合理，有缓存机制 |
| **总体评分** | **7.5/10** | 良好，有优化空间 |

## 估算优化收益

- **代码行数减少**: 预计减少 15-20% (约 100-150 行)
- **维护成本降低**: 30-40% (集中化配置和逻辑)
- **可测试性提升**: 40-50% (更好的模块化)
- **扩展性提升**: 50%+ (基于基类更容易添加新客户端)

## 下一步行动建议

1. **阶段一**: 消除代码重复 (2-3小时工作量)
   - 创建 `config.py`, `image_utils.py`, `prompt_builder.py`
   - 重构三个客户端使用统一工具

2. **阶段二**: 简化回退逻辑 (1-2小时工作量)
   - 创建 `base_client.py` 基类
   - 重构 PPTGenerator 使用责任链模式

3. **阶段三**: 改进错误处理和类型注解 (1小时工作量)
   - 统一类型注解风格
   - 改进 JSON 解析错误处理

**总预估工作量**: 4-6 小时
**预期收益**: 代码质量从 7.5 提升到 8.5+

---

*分析日期: 2026-01-13*
*分析工具: Claude Code (code-simplifier)*
