# 矢量插画风格 (Vector Illustration)

## 视觉特点

- **色彩方案**：温暖复古配色
  - 主色：米黄 (#F5E6D3)、珊瑚红 (#E57373)、青绿 (#81C784)
  - 辅色：淡紫 (#BA68C8)、橙黄 (#FFB74D)
  - 点缀：深灰 (#424242) 用于轮廓
- **线条**：统一的黑色粗轮廓线
- **风格**：扁平化、几何化简化、玩具模型般的可爱感
- **布局**：居中构图、对称平衡

## 适用场景

- 教育培训
- 创意提案
- 儿童相关内容
- 温暖品牌故事
- 轻松主题演讲

---

## 提示词模板

### 封面页 (Cover)

```
You are a professional illustrator specializing in flat vector illustration style.

Create a 16:9 presentation cover page with the following content:

TITLE: {title}
SUBTITLE: {subtitle}

Style Requirements:
- Flat vector illustration style
- Warm, retro color palette (beige, coral red, teal green, lavender, orange)
- Bold black contour lines around all elements
- Geometric simplification
- Toy-like, cute, playful aesthetic
- Centered composition
- Simple shapes and clean lines

Illustration Elements:
- Add relevant vector illustrations related to the topic
- Use simple geometric shapes
- Bold black outlines (2-3px)
- Flat colors without gradients
- Whimsical, approachable feel

Technical Details:
- Aspect ratio: 16:9
- Resolution: {resolution}
- Style: Flat vector with black outlines
- Background: Light beige or soft warm color
```

### 内容页 (Content)

```
You are a professional illustrator specializing in flat vector illustration style.

Create a 16:9 presentation content page with the following information:

{content}

Style Requirements:
- Flat vector illustration style
- Content in illustrated containers/cards
- Simple black border around content areas
- Warm, inviting colors
- Playful icons or illustrations for each point
- Easy to read, friendly appearance

Layout:
- Title at top with illustrated accent
- Content points with small vector icons
- Generous spacing
- Consistent black outline style

Technical Details:
- Aspect ratio: 16:9
- Resolution: {resolution}
- Background: Light warm color
```

### 数据页 (Data)

```
You are a professional illustrator specializing in flat vector illustration style.

Create a 16:9 presentation data page with the following information:

{data_content}

Style Requirements:
- Flat vector illustration style
- Simple chart/graph styling
- Bold colors for data visualization
- Black outlines on all elements
- Cute, approachable data presentation
- Use illustrated icons for data points

Layout:
- Title at top
- Data visualization with illustrated elements
- Key metrics highlighted
- Simple, clear charts

Technical Details:
- Aspect ratio: 16:9
- Resolution: {resolution}
```

---

## 调色板

```css
/* 主色调 - 温暖复古 */
--primary-beige: #F5E6D3;
--primary-coral: #E57373;
--primary-teal: #81C784;
--primary-lavender: #BA68C8;
--primary-orange: #FFB74D;

/* 中性色 */
--neutral-dark: #424242;      /* 轮廓线 */
--neutral-medium: #757575;
--neutral-light: #F5F5F5;

/* 背景 */
--bg-cream: #FFF8E1;
--bg-peach: #FFF3E0;
--bg-mint: #E8F5E9;

/* 文字 */
--text-primary: #424242;
--text-secondary: #757575;
--text-accent: #E57373;
```
