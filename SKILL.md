---
name: presentation-generator
version: 1.0.0
layer: qi
description: AI驱动的高质量PPT生成器，使用Gemini生成图片，GLM-4.7辅助转场描述与内容优化
triggers:
- PPT
- 演示文稿
- 幻灯片
- presentation
- slides
category: create
tags:
- presentation
- ppt
- ai
- gemini
- glm
- multmodal
provides:
- ppt-generation
- slide-design
- presentation-export
consumes:
- user-documents
- content-text
related:
- gemini-cli-integration
- b-01-prompt-pharmacist
- d-06-visual-poet
---

# Presentation Generator

> 基于 Gemini + GLM-4.7 的智能 PPT 生成技能

```
核心架构：文档分析 → 图片生成 → 交互演示

┌─────────────────────────────────────────────────────────────┐
│                    Presentation Generator                     │
├─────────────────────────────────────────────────────────────┤
│  1. 文档分析    →  内容结构规划                              │
│     (Claude Code / GLM-4.7)                                  │
│           ↓                                                  │
│  2. 风格加载    →  提示词生成                                │
│     (风格库 + 元提示词)                                       │
│           ↓                                                  │
│  3. Gemini 生成  →  16:9 高质量图片                          │
│     (Gemini 2.0 Pro / Flash)                                 │
│           ↓                                                  │
│  4. GLM-4.7 辅助  →  转场描述/内容优化                        │
│     (GLM-4.7 / GLM-4V)                                       │
│           ↓                                                  │
│  5. Web播放器  →  键盘控制交互演示                            │
│     (HTML5 + JS)                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 为什么需要这个技能？

| 能力 | 传统方案 | Presentation Generator |
|------|----------|------------------------|
| 图片生成 | 手动设计/素材库 | AI 自动生成 |
| 风格统一 | 难以保持一致 | 风格库保证一致性 |
| 内容规划 | 手动分页 | AI 智能规划 |
| 转场动画 | 手动添加 | AI 描述辅助 |
| 演示体验 | 普通 PDF | 交互式 Web 播放器 |

**核心价值**：从文档到演示，全程 AI 驱动

---

## Quick Start

### Step 1: 配置 API 密钥

创建 `.env` 文件：

```bash
# Gemini API (必需 - 用于图片生成)
GEMINI_API_KEY=your_gemini_api_key_here

# GLM-4.7 API (可选 - 用于转场描述和内容优化)
GLM_API_KEY=your_glm_api_key_here
```

### Step 2: 安装依赖

```bash
cd ~/.claude/skills/presentation-generator
pip install -r requirements.txt
```

### Step 3: 开始使用

在 Claude Code 中说：

```
调用 presentation-generator 为以下内容生成 5 页 PPT：
[你的文档内容或主题]
```

→ 详细使用指南见 `references/user-guide.md`

---

## Master Navigation

```
What do you need?
│
├─► 首次配置
│   └─► references/setup-guide.md
│       - API Key 配置
│       - 依赖安装
│       - 验证测试
│
├─► 理解架构
│   └─► See "Architecture" below
│
├─► 使用场景
│   └─► references/use-cases.md
│       - 文档转 PPT
│       - 主题生成 PPT
│       - 批量生成
│
├─► 风格库
│   └─► config/styles/
│       - gradient-glass.md (渐变毛玻璃)
│       - vector-illustration.md (矢量插画)
│       - minimalist-tech.md (极简科技)
│
└─► 技术细节
    └─► references/technical-details.md
        - API 调用逻辑
        - 提示词工程
        - 播放器实现
```

---

## Architecture

### 核心组件

```
presentation-generator/
├── core/                      # 核心模块
│   ├── api_adapter.py         # 统一 API 接口
│   ├── gemini_client.py       # Gemini 图片生成
│   ├── glm_client.py          # GLM-4.7 调用
│   ├── content_analyzer.py    # 文档分析
│   └── style_manager.py       # 风格管理
│
├── generators/                # 生成器
│   ├── ppt_generator.py       # 主生成器
│   ├── prompt_generator.py    # 提示词生成
│   └── video_composer.py      # 视频合成(可选)
│
├── config/                    # 配置
│   ├── styles/                # 风格库
│   └── prompts/               # 提示词模板
│
├── templates/                 # 模板
│   ├── viewer.html            # 图片播放器
│   └── video_viewer.html      # 视频播放器
│
└── agents/                    # Subagent
    └── ppt-executor.md        # 执行器定义
```

### 数据流

```
用户输入
    ↓
[content_analyzer] → 生成 slides_plan.json
    ↓
[prompt_generator] → 为每页生成图片提示词
    ↓
[gemini_client] → 调用 Gemini 生成图片
    ↓
[glm_client] → GLM-4.7 生成转场描述(可选)
    ↓
[video_composer] → 合成演示网页
    ↓
输出: outputs/TIMESTAMP/
    ├── images/           # 生成的图片
    ├── viewer.html       # 播放器
    └── plan.json         # 内容规划
```

---

## 风格系统

### 内置风格

| 风格 | 特点 | 适用场景 |
|------|------|----------|
| **gradient-glass** | 霓虹渐变、玻璃拟态 | 科技、商务、数据 |
| **vector-illustration** | 扁平矢量、黑色轮廓 | 教育、创意、儿童 |
| **minimalist-tech** | 极简黑白、Helvetica | 专业、学术、企业 |

### 自定义风格

在 `config/styles/` 创建新的 `.md` 文件：

```markdown
# 我的风格

## 视觉特点
- 色彩方案：...
- 字体选择：...
- 布局风格：...

## 提示词模板

### 封面页
You are a presentation designer. Create a cover page with...

### 内容页
You are a presentation designer. Create a content page with...
```

---

## API 适配层

### Gemini 图片生成

```python
from core.gemini_client import GeminiClient

client = GeminiClient(api_key="your_key")
image = client.generate_image(
    prompt="A modern tech presentation cover",
    aspect_ratio="16:9",
    style="gradient-glass"
)
```

### GLM-4.7 转场描述

```python
from core.glm_client import GLMClient

client = GLMClient(api_key="your_key")
description = client.generate_transition_prompt(
    from_slide="cover.png",
    to_slide="content1.png",
    style="professional"
)
```

---

## 输出格式

### 图片模式

```
outputs/20240113_120000/
├── images/
│   ├── slide_01_cover.png
│   ├── slide_02_content.png
│   └── ...
├── viewer.html              # 键盘控制播放器
├── slides_plan.json         # 内容规划
└── generation_log.json      # 生成日志
```

### 播放器控制

| 按键 | 功能 |
|------|------|
| `→` `↓` | 下一页 |
| `←` `↑` | 上一页 |
| `Home` | 首页 |
| `End` | 末页 |
| `F` | 全屏 |

---

## 部署检查清单

### 配置阶段
- [ ] Gemini API Key 已配置
- [ ] GLM-4.7 API Key 已配置(可选)
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] `.env` 文件已创建

### 测试阶段
- [ ] 能成功生成单页测试图片
- [ ] 播放器可正常展示
- [ ] 键盘控制功能正常
- [ ] 输出目录结构正确

---

## 常见触发语

Claude Code 会自动识别这些意图：

```
生成相关：
- "生成一个5页的PPT"
- "为这个文档制作演示文稿"
- "创建关于[主题]的slides"

风格相关：
- "用渐变毛玻璃风格生成PPT"
- "使用矢量插画风格"

辅助功能：
- "帮我规划PPT内容结构"
- "优化这个PPT的提示词"
```

---

## 与现有技能的集成

| 技能 | 集成方式 | 目的 |
|------|----------|------|
| `gemini-cli-integration` | 复用 Gemini 调用逻辑 | 多模态能力 |
| `b-01-prompt-pharmacist` | 协同优化提示词 | 提升生成质量 |
| `d-06-visual-poet` | 协同设计视觉风格 | 扩展风格库 |

---

## 配置选项

```yaml
# 生成选项
generation:
  resolution: "2K"           # 2K / 4K
  format: "png"              # png / jpg
  parallel: true             # 并行生成

# 质量选项
quality:
  temperature: 0.7           # 创意度
  top_p: 0.9
  top_k: 40

# 输出选项
output:
  include_viewer: true       # 生成播放器
  include_json: true         # 生成规划文件
  timestamp_dirs: true       # 时间戳目录
```

---

## 信心赋予

这个技能的核心价值不是"又多一个 PPT 工具"，而是：

**你开始像搭产品一样用 AI**

- 文档分析 → 内容结构化
- 风格系统 → 视觉一致性
- 双模型协作 → Gemini 图片 + GLM 描述
- 交互体验 → 超越传统 PPT

**Skills 负责理解意图，Core 负责执行生成，Templates 负责最终呈现。**

你不是在"生成 PPT"，你是在"创建一个完整的演示体验"。

---

## 技术债务与未来计划

### v1.0 (当前)
- ✅ Gemini 图片生成
- ✅ GLM-4.7 转场描述
- ✅ 基础播放器

### v1.1 (计划)
- ⏳ FFmpeg 视频合成
- ⏳ 动画转场效果
- ⏳ 更多内置风格

### v2.0 (展望)
- ⏳ AI 数字人讲解
- ⏳ 实时协作编辑
- ⏳ 云端部署方案
