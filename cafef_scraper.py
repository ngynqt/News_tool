#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cafef Article Scraper Tool
A utility to scrape detailed content from Cafef articles.
"""

import os
import sys
import json
import logging
import argparse
from urllib.parse import urljoin
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup, Tag
import google.generativeai as genai

# Set up logging to stderr so stdout can be reserved for clean JSON output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("cafef_scraper")



def resolve_url(base_url: str, url: Optional[str]) -> str:
    """
    Resolves relative URLs into absolute ones.
    """
    if not url:
        return ""
    return urljoin(base_url, url.strip())


def find_image_caption(img: Tag, content_area: Tag) -> str:
    """
    Finds the caption of an image tag inside the article content.
    Uses multiple fallback strategies for different layout structures.
    """
    # 1. Check for a figure or VCSortableInPreviewMode parent container
    container = img.find_parent(class_="VCSortableInPreviewMode") or img.find_parent("figure")
    if container:
        caption_tag = (
            container.find(class_="PhotoCMS_Caption") or 
            container.find("figcaption") or 
            container.find(class_="PhotoCMS_Description") or
            container.find(class_="img-caption")
        )
        if caption_tag:
            p_inside = caption_tag.find("p")
            text = p_inside.get_text().strip() if p_inside else caption_tag.get_text().strip()
            if text:
                return text

    # 2. Look inside the parent tag for elements matching caption classes
    parent = img.parent
    if parent:
        caption_tag = parent.find(class_=lambda x: x and any(word in x.lower() for word in ["caption", "description"]))
        if caption_tag and caption_tag != img:
            text = caption_tag.get_text().strip()
            if text:
                return text

        # 3. Check next siblings of parent in DOM
        sibling = parent.next_sibling
        while sibling:
            if isinstance(sibling, Tag):
                if sibling.name in ["p", "div", "span"]:
                    sibling_classes = sibling.get("class") or []
                    sibling_class_str = " ".join(sibling_classes).lower()
                    if any(word in sibling_class_str for word in ["caption", "description"]):
                        text = sibling.get_text().strip()
                        if text:
                            return text
                    break
                else:
                    # Encountered another block tag that is not text/caption, stop
                    break
            sibling = sibling.next_sibling

    # 4. Fallback to image alt/title if it looks descriptive
    alt_text = img.get("alt") or img.get("title") or ""
    alt_text = alt_text.strip()
    if alt_text and len(alt_text) > 15:
        return alt_text

    return ""


def generate_facebook_summary(title: str, sapo: str, content: str, url: str, api_key: str, model_name: str = "gemini-3.1-flash-lite") -> Optional[str]:
    """
    Uses Gemini API to generate an engaging Facebook post summary.
    """
    try:
        logger.info(f"Initializing Gemini API using model '{model_name}' and generating Facebook post summary...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
Bạn là một chuyên gia biên tập và sáng tạo nội dung mạng xã hội. Hãy viết một bài đăng Facebook hấp dẫn để tóm tắt bài báo dưới đây.

Yêu cầu bài đăng:
1. Có tiêu đề thu hút người đọc, sử dụng các biểu tượng cảm xúc (emoji) phù hợp.
2. Tóm tắt ngắn gọn các thông tin chính, số liệu quan trọng hoặc phân tích cốt lõi dưới dạng các gạch đầu dòng (bullet points) ngắn gọn, súc tích.
3. Giọng văn lôi cuốn, dễ hiểu và chuyên nghiệp, phù hợp với độc giả Facebook quan tâm đến kinh tế/tin tức.
4. Thêm các hashtag liên quan ở cuối bài viết (ví dụ: #tintuc #kinhte #taichinh #vietnam #cafef...).
5. Ở cuối bài, chèn một dòng kêu gọi người đọc xem chi tiết kèm theo link bài viết gốc: {url}
6. CHỈ TRẢ VỀ DUY NHẤT nội dung bài đăng Facebook để copy. TUYỆT ĐỐI KHÔNG viết thêm bất kỳ lời dẫn đầu, lời chào, hay lời giải thích nào khác ngoài bài viết (ví dụ: KHÔNG được viết câu như "Tuyệt vời! Dưới đây là bài đăng Facebook...").

Dữ liệu bài viết:
- Tiêu đề bài báo: {title}
- Sapo: {sapo}
- Nội dung chi tiết:
{content}
"""
        response = model.generate_content(prompt)
        if response and response.text:
            text = response.text.strip()
            # Programmatic fallback cleanup for conversational prefixes
            lines = text.split('\n')
            if lines and any(word in lines[0].lower() for word in ["tuyệt vời", "dưới đây là", "đây là bài đăng", "bài viết facebook", "chào bạn"]):
                lines = lines[1:]
                while lines and not lines[0].strip():
                    lines = lines[1:]
                text = '\n'.join(lines).strip()
            return text
    except Exception as e:
        logger.error(f"Error generating Facebook summary with Gemini using model {model_name}: {e}")
    return None


def scrape_cafef_article(url: str, api_key: Optional[str] = None, model_name: str = "gemini-3.1-flash-lite") -> Dict[str, Any]:
    """
    Scrapes a Cafef article URL and extracts title, sapo, publish time,
    paragraphs content, and images with captions.
    
    If api_key is provided, uses Gemini API to generate a Facebook summary.
    
    Returns a dictionary with the extracted fields.
    """
    result: Dict[str, Any] = {
        "url": url,
        "title": None,
        "sapo": None,
        "publish_time": None,
        "content": "",
        "images": [],
        "facebook_summary": None
    }

    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        logger.info(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch page. Status code: {response.status_code}")
            return result
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. Scope search within container class "left_cate totalcontentdetail"
        container = soup.find(class_="left_cate totalcontentdetail") or soup.find(class_="totalcontentdetail")
        if not container:
            logger.warning("Main container 'left_cate totalcontentdetail' not found. Falling back to body.")
            container = soup.find("body") or soup
            
        # 2. Extract Title
        try:
            title_tag = (
                container.find("h1", class_="title") or 
                container.find("h1", attrs={"data-role": "title"}) or 
                container.find("h1", attrs={"itemprop": "headline"}) or
                container.find("h1")
            )
            if title_tag:
                result["title"] = title_tag.get_text().strip()
        except Exception as e:
            logger.warning(f"Error parsing title: {e}")
            
        # 3. Extract Sapo (short description)
        try:
            sapo_tag = (
                container.find("p", class_="sapo") or 
                container.find(class_="sapo") or
                container.find(attrs={"data-role": "sapo"}) or
                container.find(attrs={"itemprop": "description"})
            )
            if sapo_tag:
                result["sapo"] = sapo_tag.get_text().strip()
        except Exception as e:
            logger.warning(f"Error parsing sapo: {e}")
            
        # 4. Extract Publish Time
        try:
            # Look for elements with class 'pdate' or containing 'time'/'date' in class
            pdate_tag = container.find(class_="pdate")
            if not pdate_tag:
                # Find all tags inside container and look for date/time indicators in class
                for tag in container.find_all(class_=True):
                    classes = tag.get("class") or []
                    class_str = " ".join(classes).lower()
                    # Check for pdate or specific metadata classes
                    if "pdate" in class_str or ("time" in class_str and "live" not in class_str and "ago" not in class_str):
                        pdate_tag = tag
                        break
            if pdate_tag:
                result["publish_time"] = pdate_tag.get_text().strip()
        except Exception as e:
            logger.warning(f"Error parsing publish time: {e}")
            
        # 5. Locate content area for text & images
        content_area = container.find(class_="detail-content") or container.find(class_="contentdetail") or container
        
        # 6. Extract Text Content (Filter out caption texts from the main body paragraphs)
        try:
            body_paragraphs = []
            for p in content_area.find_all("p"):
                # Identify if the paragraph belongs to a caption or footer links to exclude it
                is_caption_or_related = False
                
                # Check current p's class
                p_classes = p.get("class") or []
                p_class_str = " ".join(p_classes).lower()
                if any(word in p_class_str for word in ["caption", "description", "link-content-footer"]):
                    is_caption_or_related = True
                
                # Check parent classes
                if not is_caption_or_related:
                    for parent in p.parents:
                        if parent == content_area:
                            break
                        parent_classes = parent.get("class") or []
                        parent_class_str = " ".join(parent_classes).lower()
                        if any(word in parent_class_str for word in ["vcsortableinpreviewmode", "caption", "description", "link-content-footer"]) or parent.name == "figcaption":
                            is_caption_or_related = True
                            break
                
                if not is_caption_or_related:
                    text = p.get_text().strip()
                    # Clean up weird empty characters or layout space placeholders
                    if text and text not in ["﻿", ""]:
                        body_paragraphs.append(text)
            
            result["content"] = "\n\n".join(body_paragraphs)
        except Exception as e:
            logger.warning(f"Error parsing text content: {e}")
            
        # 7. Extract Images & Captions (Cover + all inline article images)
        try:
            import re as _re
            images_list = []
            seen_urls = set()

            def get_best_img_url(img_tag):
                """Get highest quality URL, converting thumb CDN prefix to full-size."""
                raw = (
                    img_tag.get("data-original") or
                    img_tag.get("data-src") or
                    img_tag.get("data-lazy-src") or
                    img_tag.get("src") or ""
                )
                if not raw or raw.startswith("data:"):
                    return ""
                abs_url = resolve_url(url, raw.strip())
                # Strip Cafef CDN thumbnail prefix: /thumb_w/640/ -> /
                abs_url = _re.sub(r"(cafefcdn\.com)/thumb_w/\d+/", r"\1/", abs_url)
                return abs_url

            def is_junk_url(img_url):
                """
                Filter out UI/tracking/ad elements only.
                NOTE: Do NOT filter on 'avatar' or 'logo' — Cafef uses these words
                in real article photo filenames (e.g. avatar1783436531808.jpg).
                """
                lower = img_url.lower()
                if lower.startswith("data:"):
                    return True
                junk_patterns = [
                    r"/tracking[/?]", r"/pixel[/?]", r"\.gif(\?|$)",
                    r"/zoom/\d+_\d+/",  # Sidebar/related article thumbnails
                    r"/ads?[/_]", r"googlesyndication", r"doubleclick\.net",
                    r"loading[\.-_]", r"spinner[\.-_]", r"/icons?/", r"favicon",
                ]
                return any(_re.search(p, lower) for p in junk_patterns)

            def is_too_small(img_tag):
                """Skip tiny sprites/icons based on explicit width/height."""
                try:
                    w = int(img_tag.get("width") or 0)
                    h = int(img_tag.get("height") or 0)
                    if 0 < w < 50 or 0 < h < 50:
                        return True
                except (ValueError, TypeError):
                    pass
                return False

            def add_image(img_tag, caption_override=None, force=False):
                img_url = get_best_img_url(img_tag)
                if not img_url or img_url in seen_urls:
                    return
                if not force:
                    if is_junk_url(img_url) or is_too_small(img_tag):
                        return
                seen_urls.add(img_url)
                caption = caption_override or find_image_caption(img_tag, container)
                images_list.append({
                    "url": img_url,
                    "caption": caption if caption else None
                })
                logger.info(f"  + Image captured: {img_url[:90]}")

            # Strategy 1: Cover image — force=True to bypass junk filter
            cover_img = container.find("img", attrs={"data-role": "cover"})
            if cover_img:
                cap = cover_img.get("alt") or cover_img.get("title") or None
                if cap and len(cap.strip()) < 15:
                    cap = None
                add_image(cover_img, cap, force=True)
                logger.info("Found cover image (data-role=\'cover\')")
            else:
                logger.info("No cover image (data-role=\'cover\') found in page")

            # Strategy 2: All inline images in VCSortableInPreviewMode media blocks
            media_blocks = container.find_all(class_="VCSortableInPreviewMode")
            logger.info(f"Found {len(media_blocks)} VCSortableInPreviewMode blocks")
            for block in media_blocks:
                for img in block.find_all("img"):
                    add_image(img)

            # Strategy 3: Remaining images directly in content_area
            for img in content_area.find_all("img"):
                add_image(img)

            # Strategy 4: Broader scan across entire container
            for img in container.find_all("img"):
                add_image(img)

            result["images"] = images_list
            logger.info(f"Total images extracted: {len(images_list)}")
        except Exception as e:
            logger.warning(f"Error parsing images: {e}")
        # 8. Generate Facebook summary if API Key is available
        if api_key and result["title"] and result["content"]:
            result["facebook_summary"] = generate_facebook_summary(
                title=result["title"],
                sapo=result["sapo"] or "",
                content=result["content"],
                url=url,
                api_key=api_key,
                model_name=model_name
            )
            
    except Exception as e:
        logger.error(f"An unexpected error occurred during scraping: {e}")
        
    return result


def load_config() -> Dict[str, Any]:
    """
    Loads configurations from config.json.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading config.json: {e}")
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrapes article data from Cafef, optionally generates a Facebook post summary using Gemini, and outputs JSON format."
    )
    parser.add_argument("url", help="The Cafef article URL to scrape.")
    parser.add_argument(
        "-o", "--output",
        default="output.json",
        help="Path to save the JSON output file (default: output.json)."
    )
    parser.add_argument(
        "-c", "--compact",
        action="store_true",
        help="Format JSON in compact single-line mode instead of pretty print."
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Gemini API Key. If not provided, checks the GEMINI_API_KEY environment variable or config.json."
    )
    parser.add_argument(
        "-m", "--model",
        help="Gemini Model to use (default: gemini-2.5-flash or model saved in config.json)."
    )
    
    args = parser.parse_args()
    
    # Retrieve Gemini API key and model name from argument, environment, or config file
    config = load_config()
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY") or config.get("gemini_api_key")
    model_name = args.model or config.get("gemini_model") or "gemini-3.1-flash-lite"
    
    if not api_key:
        logger.info("Gemini API key not found. Skipping Facebook post summary generation.")
        logger.info("To generate summaries, save the key in config.json or pass -k/--api-key.")
        
    data = scrape_cafef_article(args.url, api_key=api_key, model_name=model_name)
    
    indent = None if args.compact else 4
    json_str = json.dumps(data, ensure_ascii=False, indent=indent)
    
    # Save to file (defaulting to output.json)
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        logger.info(f"Successfully saved scraped data to: {args.output}")
    except Exception as e:
        logger.error(f"Failed to write output to file: {e}")
        sys.exit(1)
        
    # Print directly to stdout for immediate display
    print(json_str)
    
    # Print the Facebook summary if generated
    if data.get("facebook_summary"):
        summary_msg = (
            f"\n{'='*55}\n"
            f"📝 DỰ THẢO BÀI ĐĂNG FACEBOOK (GEMINI AI):\n"
            f"{'='*55}\n"
            f"{data['facebook_summary']}\n"
            f"{'='*55}\n"
        )
        if sys.stdout.isatty():
            print(summary_msg)
        else:
            sys.stderr.write(summary_msg + "\n")


if __name__ == "__main__":
    main()


