# -*- coding: UTF-8 -*-
"""AI 意图理解客户端。

对接任意 OpenAI 兼容接口（可自定义 base_url），将用户的自然语言输入解析为
结构化的搜索意图，供机器人选择合适的爬虫 / API 进行资源搜索。
"""

import json
import logging
import re

import requests

LOG = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个 Telegram 资源搜索机器人的「意图理解」模块。用户会用自然语言描述想要的资源，可能包括：
- AV 番号（如 ABP-123、FC2-PPV-12345）
- 演员名字
- 电影 / 电视剧名称
- 一段剧情、台词或影片描述
- 电影类型 / 题材（如「悬疑电影」「科幻片」）

请解析用户输入，并只输出一个 JSON 对象（不要输出任何其他文字），字段如下：
{
  "intent": "av_id | actor | genre | keyword | plot | general",
  "target": "解析后的搜索目标（番号 / 演员名 / 关键词 / 推测出的片名）",
  "source": "javdb | javbus | sukebei | dmm | apibay | auto",
  "explain": "用一句话说明你理解到的搜索目标"
}

规则：
- intent=av_id：输入是明确的番号；target 保持番号原样（英文字母大写、连字符保留）
- intent=actor：输入是演员名或明显在找某位演员；target 为演员名
- intent=genre：输入是电影类型 / 题材；target 为该类型关键词（如「悬疑」）
- intent=plot：输入是剧情 / 台词 / 描述；target 为推测出的最可能片名（不确定也给一个最接近的）
- intent=keyword：输入是电影 / 电视剧名称或其他明确关键词；target 为精简后的关键词
- intent=general：无法明确分类时使用；target 为原始输入的精简版
- source 表示最合适的数据源：AV 相关用 javdb/javbus/sukebei/dmm，电影 / 电视剧 / 通用关键词用 apibay，拿不准用 auto
- target 尽量精简，去掉语气词和多余描述
"""


class AiClient:
    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "gpt-4o-mini",
        proxy: str = "",
        timeout: int = 60,
    ):
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key or ""
        self.model = model or "gpt-4o-mini"
        self.proxy = proxy or ""
        self.proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        self.timeout = timeout

    @property
    def enabled(self):
        return bool(self.base_url and self.api_key)

    def chat(self, messages, temperature=0.2, max_tokens=800):
        if not self.enabled:
            return None
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                proxies=self.proxies,
                timeout=self.timeout,
            )
        except Exception as e:
            LOG.error(f"AI request failed: {e}")
            return None
        if resp.status_code != 200:
            LOG.error(
                f"AI request failed with status {resp.status_code}: {resp.text[:300]}"
            )
            return None
        try:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            LOG.error(f"AI response parse failed: {e}")
            return None

    def understand(self, text: str):
        """将自然语言输入解析为搜索意图 dict，失败返回 None。"""
        if not self.enabled:
            return None
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        content = self.chat(messages)
        if not content:
            return None
        LOG.info(f"AI 原始返回: {content}")
        intent = self._parse_json(content)
        LOG.info(f"AI 解析意图: {intent}")
        return intent

    @staticmethod
    def _parse_json(content: str):
        content = (content or "").strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        try:
            return json.loads(content)
        except Exception:
            pass
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            LOG.error(f"AI returned non-JSON content: {content[:300]}")
            return None
        try:
            return json.loads(content[start : end + 1])
        except Exception as e:
            LOG.error(f"AI JSON parse failed: {e}, content: {content[:300]}")
            return None
