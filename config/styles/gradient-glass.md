# 渐变毛玻璃卡片风格 (Gradient Glass)

## 视觉特点

- **色彩方案**：霓虹紫 (#8B5CF6) / 电光蓝 (#3B82F6) / 珊瑚橙 (#F97316)
- **字体**：Inter / SF Pro Display / 苹方
- **效果**：玻璃拟态 (Glassmorphism)、3D 玻璃物体、霓虹渐变
- **光照**：电影级光照、边缘发光
- **布局**：卡片式布局、大量留白

## 适用场景

- 科技产品发布
- 商务演示
- 数据报告
- 企业品牌展示

---

## 提示词模板

### 封面页 (Cover)

```
You are a professional presentation designer specializing in modern tech aesthetics.

Create a 16:9 presentation cover page with the following content:

TITLE: {title}
SUBTITLE: {subtitle}

Style Requirements:
- Gradient glassmorphism style with purple/blue/orange neon gradients
- 3D glass objects floating in space
- Cinematic lighting with edge glow effects
- Clean, minimalist layout inspired by Apple Keynote
- Large, bold typography for the title
- Frosted glass card effect with blur background
- Plenty of negative space
- High-end tech aesthetic

Technical Details:
- Aspect ratio: 16:9
- Resolution: {resolution}
- Style: Modern gradient glass
- Color palette: Purple (#8B5CF6), Blue (#3B82F6), Orange (#F97316)
- Background: Dark gradient with subtle animated particles
```

### 内容页 (Content)

```
You are a professional presentation designer specializing in modern tech aesthetics.

Create a 16:9 presentation content page with the following information:

{content}

Style Requirements:
- Gradient glassmorphism style
- Glass card for content container with frosted effect
- Clean hierarchy with bullet points or numbered lists
- Subtle gradient accents
- Professional and readable
- Consistent with cover page style

Layout:
- Title at top (optional, if provided)
- Content in centered glass card
- Generous spacing between elements
- Visual hierarchy with size and color

Technical Details:
- Aspect ratio: 16:9
- Resolution: {resolution}
- Background: Dark gradient matching cover style
- Text: White/light gray for readability
```

### 数据页 (Data)

```
You are a professional presentation designer specializing in modern tech aesthetics.

Create a 16:9 presentation data page with the following information:

{data_content}

Style Requirements:
- Gradient glassmorphism style
- Data visualization with glass card containers
- Clean chart/graph styling
- Highlight key metrics with gradient accents
- Professional and clear data presentation

Layout:
- Title at top
- Data visualization in center
- Key insights highlighted with gradient cards
- Supporting details below

Technical Details:
- Aspect ratio: 16:9
- Resolution: {resolution}
- Color scheme matching other slides
```

### 总结页 (Summary)

```
You are a professional presentation designer specializing in modern tech aesthetics.

Create a 16:9 presentation summary/conclusion page with the following content:

{summary_content}

Style Requirements:
- Gradient glassmorphism style
- Clean, impactful conclusion
- Call-to-action or key takeaway highlighted
- Consistent with overall presentation style

Layout:
- Centered content
- Larger text for key takeaways
- Gradient accents for emphasis
- "Thank you" or contact info if applicable

Technical Details:
- Aspect ratio: 16:9
- Resolution: {resolution}
```

---

## 转场描述模板

用于 GLM-4.7 生成页面转场描述：

```
分析以下两张PPT页面的视觉元素，生成转场效果描述：

页面 A: {from_page_description}
页面 B: {to_page_description}

请生成：
1. 从 A 到 B 的流畅转场描述
2. 适合的转场类型（淡入淡出、滑动、缩放、粒子效果等）
3. 转场时长建议（1-3秒）
4. 视觉效果细节

风格要求：保持渐变毛玻璃的连贯性，使用流畅的粒子或光线过渡效果。
```

---

## 调色板

```css
/* 主色调 */
--primary-purple: #8B5CF6;
--primary-blue: #3B82F6;
--primary-orange: #F97316;

/* 渐变 */
--gradient-main: linear-gradient(135deg, #8B5CF6, #3B82F6, #F97316);
--gradient-subtle: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(59, 130, 246, 0.3));

/* 背景 */
--bg-dark: #0F0F1A;
--bg-gradient: radial-gradient(circle at center, #1A1A2E, #0F0F1A);

/* 文字 */
--text-primary: #FFFFFF;
--text-secondary: #A0A0B0;
--text-accent: #8B5CF6;

/* 玻璃效果 */
--glass-bg: rgba(255, 255, 255, 0.1);
--glass-border: rgba(255, 255, 255, 0.2);
--glass-blur: blur(20px);
```
