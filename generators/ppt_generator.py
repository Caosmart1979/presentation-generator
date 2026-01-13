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

        # 5. Generate images with fallback
        print(f"\n[IMAGE] Generating images...")
        print(f"       Strategy: GLM-4V (primary) -> Gemini (fallback)")

        images = self._generate_images_with_fallback(
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
                self._save_image(image_data, filepath)
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

    def _generate_images_with_fallback(
        self,
        prompts: List[str],
        resolution: str,
        style: str
    ) -> List[Optional[str]]:
        """
        Generate images with 3-level fallback:
        1. GLM-4V (primary)
        2. Gemini Imagen 4.0 (secondary)
        3. OpenRouter (tertiary)

        Args:
            prompts: Image prompt list
            resolution: Resolution
            style: Style

        Returns:
            Image data list (base64)
        """
        # Level 1: Try GLM-4V first
        if self.glm_client.client:
            print(f"[IMAGE] Level 1: Trying GLM-4V (CogView-3)...")
            glm_images = self.glm_client.generate_images(
                prompts=prompts,
                resolution=resolution,
                style=style
            )

            glm_success_count = sum(1 for img in glm_images if img is not None)
            print(f"[GLM] Generated: {glm_success_count}/{len(prompts)} images")

            if glm_success_count == len(prompts):
                print(f"[GLM] All images generated successfully!")
                return glm_images
            elif glm_success_count > 0:
                print(f"[GLM] Partial success, filling gaps...")
                return self._fill_gaps_with_fallback(prompts, glm_images, resolution, style)
            else:
                print(f"[GLM] All failed, falling back to Level 2...")
                # Fall back to Level 2
                return self._try_level_2_fallback(prompts, resolution, style)

        # No GLM client, go directly to Level 2
        return self._try_level_2_fallback(prompts, resolution, style)

    def _try_level_2_fallback(
        self,
        prompts: List[str],
        resolution: str,
        style: str
    ) -> List[Optional[str]]:
        """Level 2: Try Gemini Imagen 4.0"""
        try:
            print(f"[IMAGE] Level 2: Trying Gemini (Imagen 4.0)...")
            gemini_images = self.gemini_client.generate_slides(
                prompts=prompts,
                resolution=resolution,
                style=style
            )

            gemini_success_count = sum(1 for img in gemini_images if img is not None)
            print(f"[GEMINI] Generated: {gemini_success_count}/{len(prompts)} images")

            if gemini_success_count == len(prompts):
                print(f"[GEMINI] All images generated successfully!")
                return gemini_images
            elif gemini_success_count > 0:
                print(f"[GEMINI] Partial success, filling gaps with Level 3...")
                return self._fill_gaps_with_openrouter(prompts, gemini_images, resolution, style)
            else:
                print(f"[GEMINI] All failed, falling back to Level 3...")
                return self._try_level_3_fallback(prompts, resolution, style)

        except Exception as e:
            print(f"[GEMINI] Level 2 failed: {str(e)}")
            return self._try_level_3_fallback(prompts, resolution, style)

    def _try_level_3_fallback(
        self,
        prompts: List[str],
        resolution: str,
        style: str
    ) -> List[Optional[str]]:
        """Level 3: Try OpenRouter (final fallback)"""
        if self.openrouter_client.client:
            print(f"[IMAGE] Level 3: Trying OpenRouter (FLUX/Gemini-3)...")
            return self.openrouter_client.generate_images(
                prompts=prompts,
                resolution=resolution,
                style=style
            )
        else:
            print(f"[OPENROUTER] No client available, all levels failed!")
            return [None] * len(prompts)

    def _fill_gaps_with_fallback(
        self,
        prompts: List[str],
        partial_images: List[Optional[str]],
        resolution: str,
        style: str
    ) -> List[Optional[str]]:
        """Fill failed images with Level 2 then Level 3"""
        result = partial_images.copy()
        for i, img in enumerate(partial_images):
            if img is None:
                print(f"[FALLBACK] Filling slide {i+1} (trying Level 2)...")
                try:
                    gemini_img = self.gemini_client.generate_image(
                        prompt=prompts[i],
                        resolution=resolution,
                        style=style
                    )
                    result[i] = gemini_img
                except Exception as e:
                    print(f"[FALLBACK] Level 2 failed for slide {i+1}, trying Level 3...")
                    result[i] = self._try_single_openrouter(prompts[i], resolution, style)
        return result

    def _fill_gaps_with_openrouter(
        self,
        prompts: List[str],
        partial_images: List[Optional[str]],
        resolution: str,
        style: str
    ) -> List[Optional[str]]:
        """Fill failed images with Level 3 (OpenRouter)"""
        result = partial_images.copy()
        for i, img in enumerate(partial_images):
            if img is None:
                print(f"[FALLBACK] Filling slide {i+1} with OpenRouter...")
                result[i] = self._try_single_openrouter(prompts[i], resolution, style)
        return result

    def _try_single_openrouter(
        self,
        prompt: str,
        resolution: str,
        style: str
    ) -> Optional[str]:
        """Try generating single image with OpenRouter"""
        if not self.openrouter_client.client:
            return None
        try:
            return self.openrouter_client.generate_image(
                prompt=prompt,
                size=self._get_size_for_openrouter(resolution)
            )
        except Exception as e:
            print(f"[OPENROUTER] Single image failed: {str(e)}")
            return None

    def _get_size_for_openrouter(self, resolution: str) -> str:
        """Map resolution to OpenRouter size"""
        size_map = {
            "2K": "1344x768",
            "1080p": "1024x576",
            "4K": "2048x1152"
        }
        return size_map.get(resolution, "1344x768")

    def _save_image(self, image_base64: str, filepath: str) -> None:
        """Save image to file (unified for both GLM and Gemini)"""
        import base64

        try:
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',', 1)[1]

            image_data = base64.b64decode(image_base64)
            with open(filepath, "wb") as f:
                f.write(image_data)

            print(f"[SAVE] {filepath}")

        except Exception as e:
            print(f"[ERROR] Failed to save {filepath}: {str(e)}")

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
