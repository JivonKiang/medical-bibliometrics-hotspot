#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PubMed文献数据采集与分析模块
基于NCBI E-utilities API，无需认证即可使用
数据来源：PubMed/MEDLINE - 公共数据库
"""

import requests
import xml.etree.ElementTree as ET
import json
import time
import re
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# 医学研究领域分类及其PubMed检索词
MEDICAL_DOMAINS = {
    "肿瘤学": "Neoplasms[MeSH] OR cancer[Title/Abstract] OR tumor[Title/Abstract] OR carcinoma[Title/Abstract]",
    "心血管疾病": "Cardiovascular Diseases[MeSH] OR heart disease[Title/Abstract] OR stroke[Title/Abstract] OR myocardial infarction[Title/Abstract]",
    "神经科学": "Nervous System Diseases[MeSH] OR neuroscience[Title/Abstract] OR Alzheimer[Title/Abstract] OR Parkinson[Title/Abstract]",
    "免疫学": "Immune System Diseases[MeSH] OR immunology[Title/Abstract] OR autoimmune[Title/Abstract] OR inflammation[Title/Abstract]",
    "传染病": "Communicable Diseases[MeSH] OR infectious disease[Title/Abstract] OR virus[Title/Abstract] OR COVID-19[Title/Abstract]",
    "代谢疾病": "Metabolic Diseases[MeSH] OR diabetes[Title/Abstract] OR obesity[Title/Abstract] OR metabolic syndrome[Title/Abstract]",
    "精准医学": "Precision Medicine[MeSH] OR personalized medicine[Title/Abstract] OR pharmacogenomics[Title/Abstract]",
    "人工智能医学": "Artificial Intelligence[MeSH] OR machine learning[Title/Abstract] OR deep learning[Title/Abstract] OR AI[Title/Abstract]",
    "基因组学": "Genomics[MeSH] OR genome[Title/Abstract] OR sequencing[Title/Abstract] OR CRISPR[Title/Abstract]",
    "干细胞": "Stem Cells[MeSH] OR stem cell[Title/Abstract] OR regenerative medicine[Title/Abstract]",
}

# 时间范围配置
TIME_RANGES = {
    "past_week": 7,
    "past_month": 30,
    "past_6months": 180,
    "past_year": 365,
}


def get_date_range(days: int) -> tuple:
    """获取指定天数前的日期范围"""
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.strftime("%Y/%m/%d"), end.strftime("%Y/%m/%d")


def search_pubmed(query: str, mindate: str, maxdate: str, retmax: int = 1000) -> list:
    """
    使用E-utilities搜索PubMed文献
    参考：https://www.ncbi.nlm.nih.gov/books/NBK25497/
    """
    # Step 1: ESearch - 获取PMID列表
    search_params = {
        "db": "pubmed",
        "term": f"({query}) AND ({mindate}:{maxdate}[Date - Publication])",
        "retmax": retmax,
        "retmode": "json",
        "sort": "date",
    }

    try:
        r = requests.get(f"{BASE_URL}/esearch.fcgi", params=search_params, timeout=30)
        r.raise_for_status()
        data = r.json()
        idlist = data.get("esearchresult", {}).get("idlist", [])
        logger.info(f"搜索到 {len(idlist)} 篇文献: {query[:50]}...")
        return idlist
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return []


def fetch_summaries(idlist: list) -> list:
    """
    使用ESummary获取文献摘要信息
    """
    if not idlist:
        return []

    summaries = []
    batch_size = 200
    for i in range(0, len(idlist), batch_size):
        batch = idlist[i:i+batch_size]
        ids = ",".join(batch)

        summary_params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "json",
        }

        try:
            r = requests.get(f"{BASE_URL}/esummary.fcgi", params=summary_params, timeout=30)
            r.raise_for_status()
            data = r.json()
            result = data.get("result", {})

            for pmid in batch:
                if pmid in result and pmid != "uids":
                    article = result[pmid]
                    summaries.append({
                        "pmid": pmid,
                        "title": article.get("title", ""),
                        "authors": [a.get("name", "") for a in article.get("authors", [])],
                        "journal": article.get("fulljournalname", article.get("source", "")),
                        "pubdate": article.get("pubdate", ""),
                        "doi": article.get("elocationid", "").replace("doi: ", ""),
                        "mesh_terms": article.get("meshterms", []),
                    })

            time.sleep(0.34)  # NCBI限速：每秒最多3次请求
        except Exception as e:
            logger.error(f"获取摘要失败: {e}")

    return summaries


def fetch_abstracts(idlist: list) -> dict:
    """
    使用EFetch获取文献摘要文本（用于关键词提取）
    """
    if not idlist:
        return {}

    abstracts = {}
    batch_size = 200
    for i in range(0, len(idlist), batch_size):
        batch = idlist[i:i+batch_size]
        ids = ",".join(batch)

        fetch_params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "xml",
        }

        try:
            r = requests.get(f"{BASE_URL}/efetch.fcgi", params=fetch_params, timeout=30)
            r.raise_for_status()
            root = ET.fromstring(r.content)

            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                pmid = pmid_elem.text if pmid_elem is not None else ""

                abstract_elem = article.find(".//Abstract/AbstractText")
                abstract = abstract_elem.text if abstract_elem is not None else ""

                if pmid:
                    abstracts[pmid] = abstract

            time.sleep(0.34)
        except Exception as e:
            logger.error(f"获取摘要文本失败: {e}")

    return abstracts


def extract_keywords(texts: list, top_n: int = 30) -> list:
    """
    从文本中提取高频关键词/短语
    使用简单的NLP方法（无需外部模型，纯Python实现）
    """
    # 医学领域停用词
    stopwords = set([
        "the", "and", "of", "in", "to", "a", "for", "with", "was", "were",
        "is", "are", "be", "been", "being", "have", "has", "had", "do", "does",
        "did", "will", "would", "could", "should", "may", "might", "can",
        "this", "that", "these", "those", "it", "its", "we", "our", "us",
        "study", "patients", "results", "conclusion", "method", "methods",
        "analysis", "data", "using", "used", "use", "based", "between",
        "from", "by", "on", "at", "as", "or", "an", "but", "not", "no",
        "than", "only", "also", "more", "most", "some", "all", "each",
        "one", "two", "first", "second", "new", "significant", "associated",
        "high", "low", "level", "levels", "group", "groups", "compared",
        "showed", "found", "reported", "including", "included", "include",
        "after", "before", "during", "over", "under", "through", "among",
        "within", "into", "up", "out", "down", "off", "about", "such",
        "both", "either", "neither", "whether", "however", "therefore",
        "thus", "furthermore", "moreover", "nevertheless", "although",
        "while", "whereas", "because", "since", "until", "unless",
    ])

    # 合并所有文本
    all_text = " ".join(texts).lower()

    # 提取2-3词短语
    words = re.findall(r'\b[a-z][a-z]+\b', all_text)
    words = [w for w in words if w not in stopwords and len(w) > 2]

    # 单词频率
    single_freq = Counter(words)

    # 双词短语
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    bigram_freq = Counter(bigrams)

    # 三词短语
    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
    trigram_freq = Counter(trigrams)

    # 合并并排序
    keywords = []
    for word, count in single_freq.most_common(top_n):
        if count >= 3:
            keywords.append({"term": word, "count": count, "type": "single"})

    for phrase, count in bigram_freq.most_common(top_n):
        if count >= 2:
            keywords.append({"term": phrase, "count": count, "type": "phrase"})

    for phrase, count in trigram_freq.most_common(top_n // 2):
        if count >= 2:
            keywords.append({"term": phrase, "count": count, "type": "phrase"})

    # 按频次排序
    keywords.sort(key=lambda x: x["count"], reverse=True)
    return keywords[:top_n]


def analyze_domain(domain_name: str, query: str, days: int) -> dict:
    """
    分析单个医学领域的文献数据
    """
    mindate, maxdate = get_date_range(days)
    idlist = search_pubmed(query, mindate, maxdate)

    if not idlist:
        return {
            "domain": domain_name,
            "count": 0,
            "articles": [],
            "keywords": [],
            "top_journals": [],
            "date_range": f"{mindate} - {maxdate}",
        }

    summaries = fetch_summaries(idlist)
    abstracts = fetch_abstracts(idlist)

    # 合并摘要到summaries
    for s in summaries:
        s["abstract"] = abstracts.get(s["pmid"], "")

    # 提取关键词
    all_texts = []
    for s in summaries:
        title = s.get("title") or ""
        abstract = s.get("abstract") or ""
        all_texts.append(title + " " + abstract)
    keywords = extract_keywords(all_texts)

    # 期刊统计
    journals = Counter([s["journal"] for s in summaries if s["journal"]])
    top_journals = [{"name": name, "count": count} for name, count in journals.most_common(10)]

    # 作者统计
    all_authors = []
    for s in summaries:
        all_authors.extend(s.get("authors", [])[:3])  # 只取前3作者
    top_authors = Counter(all_authors).most_common(10)
    top_authors = [{"name": name, "count": count} for name, count in top_authors]

    return {
        "domain": domain_name,
        "count": len(summaries),
        "articles": summaries[:20],  # 只保留前20篇详细信息
        "keywords": keywords,
        "top_journals": top_journals,
        "top_authors": top_authors,
        "date_range": f"{mindate} - {maxdate}",
    }


def generate_report(time_label: str, days: int) -> dict:
    """
    生成指定时间范围的完整报告
    """
    logger.info(f"开始生成报告: {time_label} ({days}天)")

    report = {
        "generated_at": datetime.now().isoformat(),
        "time_label": time_label,
        "days": days,
        "domains": [],
        "summary": {},
    }

    for domain_name, query in MEDICAL_DOMAINS.items():
        result = analyze_domain(domain_name, query, days)
        report["domains"].append(result)
        logger.info(f"  {domain_name}: {result['count']} 篇")

    # 总体统计
    total = sum(d["count"] for d in report["domains"])
    report["summary"] = {
        "total_articles": total,
        "domains_analyzed": len(MEDICAL_DOMAINS),
        "date_range": get_date_range(days),
    }

    # 跨领域热门关键词
    all_keywords = []
    for d in report["domains"]:
        for kw in d.get("keywords", []):
            all_keywords.append(kw)

    # 合并相同关键词
    merged = {}
    for kw in all_keywords:
        term = kw["term"]
        if term in merged:
            merged[term]["count"] += kw["count"]
            merged[term]["domains"] = merged[term].get("domains", []) + [d["domain"] for d in report["domains"] if any(k["term"] == term for k in d.get("keywords", []))]
        else:
            merged[term] = {
                "term": term,
                "count": kw["count"],
                "type": kw["type"],
                "domains": [d["domain"] for d in report["domains"] if any(k["term"] == term for k in d.get("keywords", []))],
            }

    report["global_keywords"] = sorted(merged.values(), key=lambda x: x["count"], reverse=True)[:50]

    logger.info(f"报告生成完成: {time_label}, 总计 {total} 篇文献")
    return report


def save_report(report: dict, output_dir: Path):
    """保存报告到JSON文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"report_{report['time_label']}.json"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info(f"报告已保存: {filepath}")
    return filepath


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "data"

    for label, days in TIME_RANGES.items():
        report = generate_report(label, days)
        save_report(report, output_dir)
