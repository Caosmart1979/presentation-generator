"""
PPT Generator - Main generator
Coordinates the entire PPT generation workflow
Priority: GLM-4V (primary) -> Gemini (secondary) -> OpenRouter (tertiary)
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.gemini_client import GeminiClient
from core.glm_client import GLMClient
from core.openrouter_client import OpenRouterClient
from core.style_manager import StyleManager
from core.config import ResolutionConfig
from core.image_utils import save_base64_image
from core.generation_chain import ImageGenerationChain
from generators.prompt_generator import PromptGenerator


class PPTGenerator:
    """Main PPT Generator with 3-level fallback"""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        glm_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None
    ):
        """
        Initialize generator

        Args:
            gemini_api_key: Gemini API key (secondary fallback)
            glm_api_key: GLM API key (primary for images)
            openrouter_api_key: OpenRouter API key (tertiary fallback)
        """
        self.gemini_client = GeminiClient(gemini_api_key)
        self.glm_client = GLMClient(glm_api_key)
        self.openrouter_client = OpenRouterClient(openrouter_api_key)
        self.style_manager = StyleManager()
        self.prompt_generator = PromptGenerator()

        # Create generation chain (GLM -> Gemini -> OpenRouter)
        self.generation_chain = ImageGenerationChain([
            self.glm_client,
            self.gemini_client,
            self.openrouter_client
        ])

    def generate(
        self,
        content: str,
        page_count: int = 5,
        style: str = "gradient-glass",
        resolution: str = "2K",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete PPT

        Args:
            content: Document content or topic
            page_count: Number of pages
            style: Style name
            resolution: Resolution (2K/4K)
            output_dir: Output directory

        Returns:
            Generation result info
        """
        print(f"[PPT] Starting generation...")
        print(f"   Pages: {page_count}")
        print(f"   Style: {style}")
        print(f"   Resolution: {resolution}")

        # 1. Create output directory
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"outputs/{timestamp}"

        os.makedirs(output_dir, exist_ok=True)
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # 2. Generate content plan
        print(f"\n[PLAN] Generating content plan...")
        slides_plan = self._generate_slides_plan(content, page_count)

        # Save plan
        plan_path = os.path.join(output_dir, "slides_plan.json")
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(slides_plan, f, ensure_ascii=False, indent=2)

        # 3. Load style
        print(f"\n[STYLE] Loading style: {style}")
        style_config = self.style_manager.load_style(style)

        # 4. Generate image prompts
        print(f"\n[PROMPT] Generating image prompts...")
        prompts = self.prompt_generator.generate_prompts(
            slides_plan=slides_plan,
            style_config=style_config,
            resolution=resolution
        )

        # Save prompts
        prompts_path = os.path.join(output_dir, "prompts.json")
        with open(prompts_path, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)

        # 5. Generate images with fallback chain
        print(f"\n[IMAGE] Generating images...")
        available_clients = self.generation_chain.get_available_clients()
        print(f"       Strategy: {' -> '.join(available_clients)}")

        images = self.generation_chain.generate_images(
            prompts=prompts,
            resolution=resolution,
            style=style
        )

        # Save images
        image_paths = []
        for i, image_data in enumerate(images):
            if image_data:
                filename = f"slide_{i+1:02d}_{slides_plan['slides'][i]['page_type']}.png"
                filepath = os.path.join(images_dir, filename)
                save_base64_image(image_data, filepath)
                image_paths.append(filepath)

        # 6. Generate transitions (optional)
        transitions = []
        if self.glm_client.client:
            print(f"\n[TRANSITION] Generating transition descriptions...")
            transitions = self._generate_transitions(image_paths, style)

        # 7. Generate viewer
        print(f"\n[VIEWER] Generating viewer...")
        viewer_html = self._generate_viewer(
            image_paths=image_paths,
            slides_plan=slides_plan,
            output_dir=output_dir
        )

        viewer_path = os.path.join(output_dir, "viewer.html")
        with open(viewer_path, 'w', encoding='utf-8') as f:
            f.write(viewer_html)

        # 8. Generate log
        log = {
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "page_count": page_count,
            "style": style,
            "resolution": resolution,
            "slides": slides_plan,
            "images": image_paths,
            "transitions": transitions
        }

        log_path = os.path.join(output_dir, "generation_log.json")
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

        # 9. Return result
        result = {
            "success": True,
            "output_dir": output_dir,
            "page_count": len(image_paths),
            "style": style,
            "resolution": resolution,
            "images": image_paths,
            "viewer_path": viewer_path,
            "plan_path": plan_path
        }

        print(f"\n[OK] Generation complete!")
        print(f"[DIR] Output: {output_dir}")
        print(f"[COUNT] Pages: {len(image_paths)}")
        print(f"[STYLE] {style}")
        print(f"[RES] {resolution}")
        print(f"\n[VIEW] Open in browser: {viewer_path}")

        return result



    def _generate_slides_plan(self, content: str, page_count: int) -> Dict[str, Any]:
        """Generate content plan"""
        # Use GLM to generate plan, or use default plan
        if self.glm_client.client:
            plan = self.glm_client.generate_slide_plan(content, page_count)
            return {
                "title": plan.get("title", content[:50]),
                "total_slides": len(plan.get("slides", [])),
                "slides": plan.get("slides", [])
            }
        else:
            # Default plan
            slides = []
            slides.append({"page_type": "cover", "content": content})
            for i in range(page_count - 2):
                slides.append({"page_type": "content", "content": f"Point {i+1} about {content}"})
            slides.append({"page_type": "summary", "content": f"{content} Summary"})

            return {
                "title": content[:50],
                "total_slides": page_count,
                "slides": slides
            }

    def _generate_transitions(
        self,
        image_paths: List[str],
        style: str
    ) -> List[Dict[str, Any]]:
        """Generate transition descriptions"""
        transitions = []
        for i in range(len(image_paths) - 1):
            transition = self.glm_client.generate_transition(
                from_image=image_paths[i],
                to_image=image_paths[i + 1],
                style=style
            )
            transitions.append(transition)
        return transitions

    def _generate_viewer(
        self,
        image_paths: List[str],
        slides_plan: Dict[str, Any],
        output_dir: str
    ) -> str:
        """Generate viewer HTML"""
        # Read template
        template_path = os.path.join(
            os.path.dirname(__file__),
            "../templates/viewer.html"
        )

        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Build slide data
        slides_data = []
        for i, path in enumerate(image_paths):
            rel_path = os.path.relpath(path, output_dir)
            slide_info = slides_plan['slides'][i] if i < len(slides_plan['slides']) else {}
            slides_data.append({
                "number": i + 1,
                "image": rel_path,
                "type": slide_info.get('page_type', 'content'),
                "content": slide_info.get('content', '')
            })

        # Replace template variables
        html = template.replace("{{SLIDES_DATA}}", json.dumps(slides_data))
        html = html.replace("{{TOTAL_SLIDES}}", str(len(slides_data)))
        html = html.replace("{{TITLE}}", slides_plan.get('title', 'Presentation'))

        return html
