import re
import urllib.request
from html import unescape
from html.parser import HTMLParser
from typing import Dict, List

from fetcher.cleaner import clean_text, summarize_text


USER_AGENT = "brush-blog-skill/0.1 (+https://github.com/Dalaoyuan2020/brush-blog-skill)"


def fetch_full_article_text(url: str, timeout: int = 6, max_chars: int = 6000) -> Dict[str, str]:
    """
    Fetch web page and extract readable article text.
    """
    if not url:
        return {"text": "", "status": "empty_url"}

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8", errors="ignore")

    html_text = _remove_noise_blocks(payload)
    article_html = _extract_article_block(html_text)
    plain_text = _html_to_text(article_html)
    plain_text = _normalize_article_text(plain_text)

    if len(plain_text) > max_chars:
        plain_text = plain_text[: max_chars - 1].rstrip() + "…"

    return {
        "text": plain_text,
        "status": "ok" if plain_text else "no_content",
    }


def build_plain_language_explanation(title: str, summary: str, body_text: str) -> str:
    """
    Build an easy-to-read explanation for non-expert users.
    """
    title_clean = clean_text(title or "这篇文章")
    short_summary = summarize_text(summary or body_text or "", max_sentences=2, max_chars=220)
    scene = _pick_scene(body_text)
    impact = _pick_impact(body_text)
    example = _pick_example(body_text)

    return (
        "一句话：这篇主要在讲“{0}”。\n"
        "场景：{1}\n"
        "重点：{2}\n"
        "举例：{3}\n"
        "建议：先看“原文链接”里的前 3 段，再回来看这里会更容易消化。".format(
            title_clean,
            scene,
            short_summary,
            example if example else impact,
        )
    )


def build_deep_read_snippet(body_text: str, max_chars: int = 900) -> str:
    """
    Return readable excerpt from full article body.
    """
    cleaned = clean_text(body_text)
    if not cleaned:
        return "暂无正文摘录，可点击原文查看完整内容。"
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "…"


def _remove_noise_blocks(html_text: str) -> str:
    text = html_text
    patterns = [
        r"(?is)<script[^>]*>.*?</script>",
        r"(?is)<style[^>]*>.*?</style>",
        r"(?is)<noscript[^>]*>.*?</noscript>",
        r"(?is)<svg[^>]*>.*?</svg>",
        r"(?is)<nav[^>]*>.*?</nav>",
        r"(?is)<footer[^>]*>.*?</footer>",
        r"(?is)<header[^>]*>.*?</header>",
        r"(?is)<aside[^>]*>.*?</aside>",
        r"(?is)<!--.*?-->",
    ]
    for pattern in patterns:
        text = re.sub(pattern, " ", text)
    return text


def _extract_article_block(html_text: str) -> str:
    for pattern in [
        r"(?is)<article[^>]*>(.*?)</article>",
        r"(?is)<main[^>]*>(.*?)</main>",
        r"(?is)<body[^>]*>(.*?)</body>",
    ]:
        match = re.search(pattern, html_text)
        if match:
            return match.group(1)
    return html_text


class _SimpleHTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        HTMLParser.__init__(self)
        self.parts = []  # type: List[str]
        self.break_tags = {"p", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "div", "section"}

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in self.break_tags:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.break_tags:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)

    def text(self) -> str:
        return "".join(self.parts)


def _html_to_text(html_text: str) -> str:
    parser = _SimpleHTMLTextParser()
    parser.feed(html_text)
    parser.close()
    return unescape(parser.text())


def _normalize_article_text(text: str) -> str:
    lines = []
    for raw in text.splitlines():
        line = clean_text(raw)
        if len(line) < 30:
            continue
        if line.lower().startswith(("cookie", "privacy", "subscribe", "share this", "related posts")):
            continue
        lines.append(line)
    return "\n".join(lines[:25])


def _pick_scene(body_text: str) -> str:
    lower = (body_text or "").lower()
    if any(word in lower for word in ["team", "团队", "collaboration", "协作"]):
        return "适合团队协作或项目推进时参考。"
    if any(word in lower for word in ["model", "ai", "llm", "机器学习"]):
        return "适合想快速理解 AI/模型思路的人。"
    if any(word in lower for word in ["product", "用户", "体验", "design"]):
        return "适合做产品和用户体验决策时阅读。"
    return "适合你想快速抓住一篇技术文章核心观点时使用。"


def _pick_impact(body_text: str) -> str:
    short = summarize_text(body_text or "", max_sentences=1, max_chars=100)
    if short == "暂无摘要":
        return "作者强调了一个可直接落地的实践思路。"
    return short


def _pick_example(body_text: str) -> str:
    sentences = re.split(r"(?<=[。！？.!?])\s+", clean_text(body_text or ""))
    for sentence in sentences:
        s = sentence.strip()
        if len(s) < 20:
            continue
        if any(key in s.lower() for key in ["for example", "例如", "比如", "case", "案例"]):
            return s[:120]
    for sentence in sentences:
        s = sentence.strip()
        if len(s) >= 40:
            return s[:120]
    return ""
