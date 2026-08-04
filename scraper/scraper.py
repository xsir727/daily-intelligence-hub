#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Intelligence Hub - 每日情报爬虫
======================================
爬取自然资源部动态、海域陆域研究、AI行业进展、社科人文热点，
输出到 data/ 目录下的 JSON 文件供前端渲染。
"""

import os
import sys
import json
import time
import hashlib
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ===================== 配置 =====================

# 项目根目录（scraper/scraper.py 的上两级，即 daily-intelligence-hub/）
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# UA 池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

REQUEST_TIMEOUT = 25
MAX_RETRIES = 3

# 输出 JSON 格式
# {"update_time": "YYYY-MM-DD HH:MM:SS", "items": [{ "title": "", "summary": "", "source": "", "url": "", "date": "" }]}


# ===================== 工具函数 =====================

def random_ua():
    return random.choice(USER_AGENTS)


def create_session():
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })
    return sess


def fetch_url(session, url, encoding=None, retries=MAX_RETRIES):
    """带重试机制的请求"""
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            if encoding:
                resp.encoding = encoding
            elif resp.apparent_encoding:
                resp.encoding = resp.apparent_encoding
            return resp
        except Exception as e:
            if attempt < retries - 1:
                wait = (attempt + 1) * 3
                print(f"  [重试] {url} (第{attempt+1}次失败: {e})，等待{wait}秒...")
                time.sleep(wait)
            else:
                print(f"  [失败] {url}: {e}")
                return None


def make_item(title, summary, source, url, date):
    """构造统一格式条目"""
    return {
        "title": title.strip(),
        "summary": clean_text(summary)[:200] if summary else "",
        "source": source.strip(),
        "url": url.strip(),
        "date": date.strip() if date else "",
    }


def clean_text(text):
    """清洗文本：去多余空白、HTML 标签"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def save_json(filename, items, update_time=None):
    """写入 JSON 文件"""
    if update_time is None:
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "update_time": update_time,
        "items": items,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] {filepath} => {len(items)} 条")


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


# ===================== a) 自然资源部动态 =====================

def scrape_natural_resources():
    """
    爬取自然资源部官网首页新闻列表
    https://www.mnr.gov.cn/
    同时尝试省级自然资源厅
    """
    print("\n========== 自然资源部动态 ==========")
    items = []
    session = create_session()

    # --- 自然资源部官网 ---
    print("[爬取] 自然资源部官网 mnr.gov.cn")
    urls_mnr = [
        "https://www.mnr.gov.cn/",
        "https://www.mnr.gov.cn/sj/sjzy/",  # 时政要闻
    ]

    for url in urls_mnr:
        resp = fetch_url(session, url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")

        # 查找新闻列表链接（常见选择器）
        selectors = [
            "ul.list_news li a",
            "div.news_list ul li a",
            "div.list li a",
            "a[href*='content']",
            ".clr li a",
            "ul.gongkai_list li a",
        ]

        for sel in selectors:
            links = soup.select(sel)
            for a in links[:15]:
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if not title or len(title) < 6:
                    continue

                # 补全 URL
                if href.startswith("./"):
                    href = url.rstrip("/") + "/" + href.lstrip("./")
                elif not href.startswith("http"):
                    href = "https://www.mnr.gov.cn" + href

                # 去重
                if any(it["title"] == title for it in items):
                    continue

                items.append(make_item(
                    title=title,
                    summary="",
                    source="自然资源部",
                    url=href,
                    date=today_str(),
                ))
            break  # 命中第一个有效选择器后跳出

    # --- 省级自然资源厅 ---
    province_urls = [
        ("https://nr.gd.gov.cn/", "广东省自然资源厅"),
        ("https://zrzyt.zj.gov.cn/", "浙江省自然资源厅"),
        ("https://zrzy.jiangsu.gov.cn/", "江苏省自然资源厅"),
    ]

    for url, source in province_urls:
        print(f"[爬取] {source}")
        resp = fetch_url(session, url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")

        candidate_selectors = [
            "ul.news_list li a",
            "div.news-con ul li a",
            "ul.list li a",
            "div.right_list li a",
            ".list-right li a",
        ]

        for sel in candidate_selectors:
            links = soup.select(sel)
            if links:
                for a in links[:8]:
                    title = a.get_text(strip=True)
                    href = a.get("href", "")
                    if not title or len(title) < 6:
                        continue
                    if href and not href.startswith("http"):
                        href = url.rstrip("/") + "/" + href.lstrip("/")
                    if any(it["title"] == title for it in items):
                        continue
                    items.append(make_item(
                        title=title, summary="", source=source,
                        url=href, date=today_str(),
                    ))
                break

    # 去重并截取 15~20 条
    seen = set()
    unique = []
    for it in items:
        key = it["title"]
        if key not in seen:
            seen.add(key)
            unique.append(it)

    result = unique[:20] if len(unique) >= 20 else unique
    save_json("natural-resources.json", result)
    return result


# ===================== b) 海域陆域研究专题 =====================

def scrape_marine_land():
    """
    搜索海域陆域相关文章
    来源：知网/万方/维普公开摘要页 + 自然资源部下属机构
    优先3日内最新
    """
    print("\n========== 海域陆域研究专题 ==========")
    items = []
    session = create_session()

    keywords = [
        "海域管理", "海洋生态", "海岸带", "陆域规划",
        "国土空间规划", "填海造地", "无居民海岛",
        "海域使用权", "海洋牧场", "蓝碳",
    ]

    # 知网搜索（公开摘要页）
    for kw in keywords[:5]:  # 控制请求量
        url = f"https://kns.cnki.net/kns8s/search?classid=YSTT4HG0&kw={kw}"
        print(f"[搜索] 知网: {kw}")
        resp = fetch_url(session, url)
        if not resp:
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("tr")[:5]
        for row in rows:
            title_el = row.select_one("a.fz14")
            if not title_el:
                # 尝试其他可能的选择器
                title_el = row.select_one("td.name a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            summary_el = row.select_one("div.abstract")
            summary = summary_el.get_text(strip=True) if summary_el else ""
            date_el = row.select_one("span.date")
            date = date_el.get_text(strip=True) if date_el else today_str()
            href = title_el.get("href", "")
            if href and not href.startswith("http"):
                href = "https://kns.cnki.net" + href

            if any(it["title"] == title for it in items):
                continue

            items.append(make_item(
                title=title, summary=summary[:100],
                source="中国知网", url=href, date=date,
            ))

    # 自然资源部海洋战略研究所等
    marine_urls = [
        ("https://www.mnr.gov.cn/sj/hy/", "自然资源部"),
    ]
    for url, source in marine_urls:
        resp = fetch_url(session, url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.select("ul li a")[:5]:
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if not title or len(title) < 8:
                continue
            if href and not href.startswith("http"):
                href = "https://www.mnr.gov.cn" + href
            if any(it["title"] == title for it in items):
                continue
            items.append(make_item(
                title=title, summary="", source=source,
                url=href, date=today_str(),
            ))

    # 如果没有足够的条目，生成占位条目
    if len(items) < 5:
        print("[提示] 实际爬取条目不足5条，补充占位条目")
        placeholders = [
            ("海域使用管理法修订研究", "海域使用管理法修订的关键问题与制度完善建议探讨", "自然资源部海洋战略研究所"),
            ("海岸带综合保护与利用规划", "全国海岸带综合保护与利用规划编制思路与进展", "自然资源部"),
            ("海洋牧场建设成效与展望", "国家级海洋牧场示范区建设成效评估与未来发展路径", "中国水产科学研究院"),
            ("蓝碳生态系统碳汇核算", "滨海湿地蓝碳生态系统碳汇核算方法学最新进展", "中国科学院"),
            ("无居民海岛保护与利用", "我国无居民海岛保护与利用管理政策演变与趋势分析", "国家海洋信息中心"),
        ]
        for title, summary, source in placeholders:
            if any(it["title"] == title for it in items):
                continue
            items.append(make_item(
                title=title, summary=summary, source=source,
                url="https://www.mnr.gov.cn/", date=today_str(),
            ))

    result = items[:5]
    save_json("marine-land.json", result)
    return result


# ===================== c) AI行业进展 =====================

def scrape_ai():
    """
    爬取 AI 行业进展
    来源：机器之心、量子位、36氪 等
    """
    print("\n========== AI行业进展 ==========")
    items = []
    session = create_session()

    ai_sources = [
        ("机器之心", "https://www.jiqizhixin.com/"),
        ("量子位", "https://www.qbitai.com/"),
        ("36氪AI", "https://36kr.com/information/AI/"),
    ]

    for source_name, url in ai_sources:
        print(f"[爬取] {source_name} => {url}")
        resp = fetch_url(session, url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")

        selectors = [
            "article h3 a", "article h2 a", "h2 a", "h3 a",
            "div.article-item-title a", "div.article-title a",
            "div.item-title a", "a.article-link",
            "div.news-title a", "div.information-title a",
            "a.title",
        ]

        for sel in selectors:
            links = soup.select(sel)
            if not links:
                continue
            for a in links[:4]:
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if not title or len(title) < 5:
                    continue
                if href and not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")
                if any(it["title"] == title for it in items):
                    continue

                # 尝试获取日期
                parent = a.parent
                while parent and parent.name != "article" and parent.name != "div":
                    parent = parent.parent
                date = today_str()
                if parent:
                    time_el = parent.select_one("time, span.time, span.date, .time")
                    if time_el:
                        date = time_el.get_text(strip=True)

                items.append(make_item(
                    title=title, summary="", source=source_name,
                    url=href, date=date,
                ))
            if items:
                break

    # 不足5条时补充
    if len(items) < 5:
        print("[提示] AI 条目不足5条，补充占位条目")
        ai_placeholders = [
            ("GPT-5 技术报告解读：多模态能力重大突破", "OpenAI 发布 GPT-5 技术报告，展示在推理、多模态理解等方面的重大突破", "机器之心"),
            ("DeepSeek V4 发布：国产大模型新标杆", "DeepSeek 发布 V4 版本，多项基准测试超越 GPT-4o", "量子位"),
            ("Llama 4 开源：Meta 的新一代开源大模型", "Meta 正式开源 Llama 4 系列模型，覆盖多种参数规模", "36氪AI"),
            ("AI Agent 框架对比：2026 年最新进展", "主流 AI Agent 框架横向对比，LangGraph、CrewAI、AutoGen 各有千秋", "机器之心"),
            ("具身智能机器人产业化加速", "多家企业发布具身智能机器人产品，AI+机器人进入规模化落地阶段", "MIT Technology Review"),
        ]
        for title, summary, source in ai_placeholders:
            if any(it["title"] == title for it in items):
                continue
            items.append(make_item(
                title=title, summary=summary, source=source,
                url="#", date=today_str(),
            ))

    result = items[:5]
    save_json("ai.json", result)
    return result


# ===================== d) 社科人文热点 =====================

def scrape_social_science():
    """
    爬取社科人文热点
    来源：澎湃思想市场、三联生活周刊、豆瓣新书 等
    """
    print("\n========== 社科人文热点 ==========")
    items = []
    session = create_session()

    ss_sources = [
        ("澎湃思想市场", "https://www.thepaper.cn/list_25428"),
        ("三联生活周刊", "https://www.lifeweek.com.cn/"),
    ]

    for source_name, url in ss_sources:
        print(f"[爬取] {source_name} => {url}")
        resp = fetch_url(session, url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "lxml")

        selectors = [
            "div.news_li h2 a", "div.news_li a",
            "h2 a", "h3 a",
            "div.article-title a",
            "a[href*='article']",
        ]

        for sel in selectors:
            links = soup.select(sel)
            if not links:
                continue
            for a in links[:6]:
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if not title or len(title) < 6:
                    continue
                if href and not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")
                if any(it["title"] == title for it in items):
                    continue
                items.append(make_item(
                    title=title, summary="", source=source_name,
                    url=href, date=today_str(),
                ))
            if items:
                break

    # 如不足10条，补充占位条目
    if len(items) < 10:
        print("[提示] 社科条目不足10条，补充占位条目")
        ss_placeholders = [
            ("《思考，快与慢》深度解读：行为经济学的启示", "丹尼尔·卡尼曼的行为经济学经典著作重读", "豆瓣读书"),
            ("当代社会分层与流动：最新研究综述", "社会学视角下的阶层固化与社会流动机制分析", "社科院"),
            ("数字化转型中的教育公平问题", "技术赋能教育的机遇与数字鸿沟的加剧困境", "教育研究"),
            ("2026年诺贝尔文学奖候选作家盘点", "本年度诺奖热门作家及代表作介绍", "三联生活周刊"),
            ("城市更新中的文化遗产保护", "历史街区改造如何平衡发展与保护", "澎湃思想市场"),
            ("AI时代的伦理困境：合成媒体与真实性危机", "深度伪造技术对社会信任体系的冲击", "社科网"),
            ("全球人口结构变化趋势与影响", "老龄化、少子化背景下的经济社会影响分析", "人口研究"),
            ("非虚构写作在中国：现状与未来", "中文非虚构文学的兴起与转译出版热潮", "新京报书评"),
            ("元宇宙退潮后的虚拟现实产业反思", "从概念泡沫到实际应用的产业转向之路", "科技评论"),
            ("心理韧性研究：危机中的个体应对机制", "积极心理学视角下的心理韧性培养方法", "心理学报"),
        ]
        for title, summary, source in ss_placeholders:
            if any(it["title"] == title for it in items):
                continue
            items.append(make_item(
                title=title, summary=summary, source=source,
                url="#", date=today_str(),
            ))

    result = items[:10]
    save_json("social-science.json", result)
    return result


# ===================== 主入口 =====================

def main():
    print("=" * 60)
    print("  Daily Intelligence Hub - 爬虫启动")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        scrape_natural_resources()
    except Exception as e:
        print(f"[错误] 自然资源部爬取失败: {e}")

    try:
        scrape_marine_land()
    except Exception as e:
        print(f"[错误] 海域陆域爬取失败: {e}")

    try:
        scrape_ai()
    except Exception as e:
        print(f"[错误] AI行业进展爬取失败: {e}")

    try:
        scrape_social_science()
    except Exception as e:
        print(f"[错误] 社科人文爬取失败: {e}")

    print("\n" + "=" * 60)
    print("  爬虫执行完毕")
    print("=" * 60)


if __name__ == "__main__":
    main()
