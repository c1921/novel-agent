from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import settings

Message = dict[str, str]


def _use_mock() -> bool:
    return settings.llm_provider == "mock" or (
        settings.llm_provider == "auto" and not settings.openai_api_key
    )


def _all_content(messages: list[Message]) -> str:
    return "\n".join(message.get("content", "") for message in messages)


def _mock_chat(messages: list[Message]) -> str:
    content = _all_content(messages)
    if "章节正文" in content or "正文写作助手" in content:
        return (
            "雨声贴着旧楼的铁皮檐滑下来，像一串被压低的脚步。林澈推开储物间的门时，"
            "手电光先照见了墙角那只褪色的书包。那是妹妹林夏失踪前一直背着的书包，拉链"
            "坏了一半，挂着她亲手缝上的蓝色布扣。\n\n"
            "他没有立刻上前。空气里有潮湿的灰尘味，也有一点淡淡的柠檬糖气息。那是林夏"
            "常带在身上的味道。林澈蹲下去，翻开书包内侧，发现夹层里塞着一张车票和半页撕"
            "下来的地图。地图上用铅笔圈出了旧港仓库，旁边写着一句很短的话：不要相信来接"
            "我的人。\n\n"
            "门外忽然传来管理员的咳嗽声。林澈把地图折进掌心，强迫自己不去猜最坏的可能。"
            "他知道这不是答案，只是一条线索，也可能是别人故意留下的诱饵。但至少从这一刻"
            "起，妹妹的失踪不再是一团空白。\n\n"
            "他离开旧楼时，雨已经停了。街灯在积水里晃动，旧港方向的天空压着一层铁灰色的"
            "云。林澈握紧那半页地图，第一次清楚地意识到，有人一直在等他走到那里。"
        )
    if "润色助手" in content:
        return (
            "雨沿着旧楼的铁皮檐一线线滑落，压低了整条巷子的声响。林澈推开储物间的门，"
            "手电光扫过潮湿的墙面，最终停在墙角那只褪色书包上。那是林夏失踪前背过的书包，"
            "坏掉的拉链旁，还缝着她亲手补上的蓝色布扣。\n\n"
            "他在门口停了几秒，才慢慢蹲下。灰尘被光束照得浮起来，潮味里混着极淡的柠檬糖"
            "气息。林澈翻开内侧夹层，摸出一张旧车票和半页地图。地图上，旧港仓库被铅笔圈住，"
            "旁边只有一句字迹仓促的话：不要相信来接我的人。\n\n"
            "门外响起管理员的咳嗽声。林澈把地图收进掌心，没有让自己继续往最坏处想。它不"
            "一定是真相，也可能是别人故意留下的误导，但至少妹妹的失踪终于不再只是一片空白。\n\n"
            "他走出旧楼时，雨已经停了。街灯碎在积水里，旧港方向的云层低得像铁。林澈握紧"
            "那半页地图，意识到有人把这条路铺到了他脚下。"
        )
    if "章节大纲" in content:
        return (
            "## 本章标题\n旧楼里的半页地图\n\n"
            "## 本章目标\n男主发现妹妹失踪前留下的线索，但暂时无法确认妹妹是否安全。\n\n"
            "## 主要冲突\n男主想确认线索真伪，却必须在时间压力和外部监视下做出下一步选择。\n\n"
            "## 场景列表\n"
            "1. 男主进入旧楼储物间，发现妹妹曾经使用过的物品。\n"
            "2. 他在夹层里找到车票和半页地图，线索指向旧港仓库。\n"
            "3. 外部动静打断调查，暗示有人关注他的行动。\n"
            "4. 男主离开旧楼，决定先追查旧港线索。\n\n"
            "## 情绪曲线\n压抑怀疑 -> 震动与克制 -> 警觉 -> 带着希望和不安行动。\n\n"
            "## 结尾钩子\n旧港方向出现新的未知等待，线索可能是真相，也可能是陷阱。\n\n"
            "## 需要埋下或回收的伏笔\n埋下旧港仓库、神秘接送者、妹妹留下的警告。"
        )
    return "这是 Mock LLM 回复。"


def _mock_json(messages: list[Message]) -> dict[str, Any]:
    content = _all_content(messages)
    if "一致性检查" in content:
        return {
            "summary": "草稿整体遵守已确认大纲，未发现会改变主线的新增重大剧情。",
            "issues": [
                {
                    "severity": "low",
                    "type": "style",
                    "description": "个别环境描写可以更贴合项目既定风格。",
                    "suggestion": "保存后可在编辑器中按风格指南进一步微调用词。",
                }
            ],
        }
    return {
        "questions": [
            {
                "id": "q1",
                "type": "must_ask",
                "question": "本章是否要确认妹妹仍然活着？",
                "reason": "这会直接改变主线推进方向和男主的行动动机。",
                "options": ["确认仍然活着", "只发现疑似线索", "发现线索可能是误导"],
            },
            {
                "id": "q2",
                "type": "must_ask",
                "question": "线索最终要指向谁或哪个地点？",
                "reason": "线索归属会影响后续章节的调查路线。",
                "options": ["旧港仓库", "神秘接送者", "妹妹曾经的同学"],
            },
            {
                "id": "q3",
                "type": "optional",
                "question": "本章结尾的氛围更偏希望还是危险？",
                "reason": "这会影响章节钩子的情绪落点，但不必改变主线。",
                "options": ["带来希望", "制造危险", "希望与危险并存"],
            },
        ],
        "auto_decidable": ["天气", "路人对白", "普通动作衔接", "非关键环境描写"],
    }


def _extract_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    start_positions = [pos for pos in [text.find("{"), text.find("[")] if pos >= 0]
    if not start_positions:
        raise ValueError("LLM response did not contain JSON")
    start = min(start_positions)
    end = max(text.rfind("}"), text.rfind("]"))
    if end <= start:
        raise ValueError("LLM response did not contain complete JSON")
    return json.loads(text[start : end + 1])


def chat_completion(messages: list[Message], temperature: float = 0.7) -> str:
    if _use_mock():
        return _mock_chat(messages)

    url = settings.openai_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    payload = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": temperature,
    }
    with httpx.Client(timeout=120) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    return data["choices"][0]["message"]["content"]


def json_completion(messages: list[Message], temperature: float = 0.3) -> dict[str, Any]:
    if _use_mock():
        return _mock_json(messages)

    text = chat_completion(messages, temperature=temperature)
    parsed = _extract_json(text)
    if not isinstance(parsed, dict):
        raise ValueError("LLM JSON response must be an object")
    return parsed
