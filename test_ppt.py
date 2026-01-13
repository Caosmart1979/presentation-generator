"""
简单的 PPT 生成测试脚本
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from generators.ppt_generator import PPTGenerator


def test_simple_ppt():
    """测试生成一个简单的 3 页 PPT"""
    print("=" * 50)
    print("Presentation Generator - Test Run")
    print("=" * 50)

    # 创建生成器
    generator = PPTGenerator()

    # 生成 PPT
    result = generator.generate(
        content="人工智能的未来发展",
        page_count=3,
        style="gradient-glass",
        resolution="2K"
    )

    print("\n" + "=" * 50)
    print("Generation Complete!")
    print("=" * 50)
    print(f"Output directory: {result['output_dir']}")
    print(f"Pages generated: {result['page_count']}")
    print(f"Style: {result['style']}")
    print(f"\nOpen viewer.html in your browser to view the presentation!")
    print(f"Path: {result['viewer_path']}")


if __name__ == "__main__":
    test_simple_ppt()
