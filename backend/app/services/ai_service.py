"""AI service for article analysis using OpenAI-compatible API."""
import json
from typing import Dict, Optional, List
from openai import AsyncOpenAI
from ..config import settings


class AIService:
    """Service for AI-powered article analysis."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.OPENAI_MODEL

    async def _chat(self, system: str, user: str, temperature=0.3, max_tokens=1000, json_mode=True) -> str:
        """Send chat request."""
        kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()

    async def analyze_article(self, title: str, content: str) -> Dict:
        """
        一次性完成文章的全面分析：
        - 分类（article_type）
        - 摘要
        - 关键词
        - 标签（labels）
        - 论文信息（如果是论文解读）
        - 数据集信息（如果是数据集分享）
        """
        prompt = f"""请对以下微信公众号文章进行全面分析。

标题：{title}

内容：
{content[:4000]}

请以 JSON 格式返回分析结果，严格按照以下结构：
{{
    "article_type": "paper_review|dataset|tool|tutorial|news|other",
    "summary": "200字以内的中文摘要",
    "keywords": ["关键词1", "关键词2", ...],
    "labels": ["标签1", "标签2", ...],
    "papers": [
        {{
            "title": "英文论文标题",
            "title_cn": "中文论文标题（如果有）",
            "authors": ["作者1", "作者2"],
            "journal": "期刊或会议名称",
            "year": 2024,
            "doi": "DOI号（如果能识别）",
            "arxiv_id": "arXiv ID（如 2401.12345，如果有）",
            "abstract": "论文摘要（如果文章中有提到）",
            "main_findings": "主要发现/贡献"
        }}
    ],
    "datasets": [
        {{
            "name": "数据集名称",
            "description": "数据集简介",
            "data_type": "数据类型（图像/文本/音频等）",
            "scale": "数据规模",
            "domain": "所属领域",
            "download_url": "下载链接（如果文章中有）",
            "access_method": "获取方式说明",
            "tutorial": "获取教程（如果文章中有详细步骤）",
            "related_papers": ["相关论文标题或DOI"]
        }}
    ]
}}

分析规则：
1. article_type 分类说明：
   - paper_review: 文章主要内容是解读/介绍学术论文
   - dataset: 文章主要内容是分享/介绍公开数据集
   - tool: 文章主要内容是介绍工具/软件/代码库
   - tutorial: 文章主要内容是技术教程/操作指南
   - news: 行业资讯/新闻动态
   - other: 其他类型

2. labels 是面向用户的标签，用于兴趣画像和检索，要求：
   - 包含领域标签（如"医学影像"、"深度学习"、"NLP"）
   - 包含主题标签（如"扩散MRI"、"目标检测"、"图像分割"）
   - 包含方法标签（如"Transformer"、"GAN"、"强化学习"）
   - 5-10个标签，中文为主

3. papers 数组：只有 article_type 为 paper_review 时才填写，否则为空数组
   - 一篇文章可能解读多篇论文
   - 尽量提取 DOI 和 arXiv ID

4. datasets 数组：只有 article_type 为 dataset 时才填写，否则为空数组
   - 一篇文章可能介绍多个数据集
   - 尽量提取下载链接和获取方式

5. keywords 是技术关键词，用于搜索，3-8个"""

        system = "你是一个专业的学术文章分析助手，擅长从微信公众号文章中提取结构化信息。请严格按照 JSON 格式返回结果。"

        raw = await self._chat(system, prompt, max_tokens=2000)
        result = json.loads(raw)

        # 确保必要字段存在
        result.setdefault("article_type", "other")
        result.setdefault("summary", "")
        result.setdefault("keywords", [])
        result.setdefault("labels", [])
        result.setdefault("papers", [])
        result.setdefault("datasets", [])

        return result
