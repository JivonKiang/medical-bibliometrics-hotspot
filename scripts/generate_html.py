#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成HTML报告页面
将JSON数据转换为丝滑的Web展示页面
使用纯CSS/SVG图表，无需外部依赖
"""

import json
from pathlib import Path
from datetime import datetime


def load_reports(data_dir: Path) -> dict:
    """加载所有时间范围的报告数据"""
    reports = {}
    for f in data_dir.glob("report_*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            reports[data["time_label"]] = data
    return reports


def generate_html(reports: dict, output_path: Path):
    """生成完整的HTML报告"""

    # 构建数据JSON
    reports_json = json.dumps(reports, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="color-scheme" content="only light">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#f8fafc">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <title>医学研究热点文献计量报告</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #7c3aed;
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
            --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            color-scheme: only light;
        }}
        /* Force light mode regardless of device setting */
        @media (prefers-color-scheme: dark) {{
            :root {{
                color-scheme: only light;
                --primary: #2563eb; --primary-dark: #1d4ed8; --secondary: #7c3aed;
                --accent: #06b6d4; --success: #10b981; --warning: #f59e0b; --danger: #ef4444;
                --bg: #f8fafc; --card-bg: #ffffff; --text: #1e293b; --text-light: #64748b;
                --border: #e2e8f0;
            }}
            body {{ background: #f8fafc; color: #1e293b; }}
            .header {{ background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); color: white; }}
            .footer {{ background: #f8fafc; color: #1e293b; }}
            table thead {{ background: #f1f5f9; }}
            .keyword-tag {{ background: linear-gradient(135deg,#eff6ff 0%,#f0f9ff 100%); border-color:#bfdbfe; }}
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            forced-color-adjust: none;
            -webkit-tap-highlight-color: transparent;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 3rem 1rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            opacity: 0.3;
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            position: relative;
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
            position: relative;
        }}

        .header .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            margin-top: 1rem;
            position: relative;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}

        .time-selector {{
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}

        .time-btn {{
            padding: 0.75rem 1.5rem;
            border: 2px solid var(--border);
            background: var(--card-bg);
            border-radius: 9999px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 500;
            transition: all 0.3s ease;
            color: var(--text);
        }}

        .time-btn:hover {{
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }}

        .time-btn.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: white;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: var(--card-bg);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            border: 1px solid var(--border);
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }}

        .stat-card .icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}

        .stat-card .icon.blue {{ background: #dbeafe; }}
        .stat-card .icon.purple {{ background: #f3e8ff; }}
        .stat-card .icon.green {{ background: #d1fae5; }}
        .stat-card .icon.orange {{ background: #fef3c7; }}
        .stat-card .icon.cyan {{ background: #cffafe; }}

        .stat-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--text);
        }}

        .stat-card .label {{
            font-size: 0.875rem;
            color: var(--text-light);
            margin-top: 0.25rem;
        }}

        .section {{
            background: var(--card-bg);
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section-title .icon {{
            font-size: 1.25rem;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
        }}

        /* SVG Charts */
        .svg-chart {{
            width: 100%;
            height: 350px;
        }}

        .svg-chart text {{
            font-family: inherit;
            font-size: 12px;
        }}

        .domain-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }}

        .domain-card {{
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 0.75rem;
            padding: 1.25rem;
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .domain-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary);
        }}

        .domain-card .domain-name {{
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }}

        .domain-card .domain-count {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--primary);
        }}

        .domain-card .domain-bar {{
            height: 6px;
            background: var(--border);
            border-radius: 3px;
            margin-top: 0.75rem;
            overflow: hidden;
        }}

        .domain-card .domain-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            border-radius: 3px;
            transition: width 1s ease;
        }}

        .keywords-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        .keyword-tag {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.4rem 0.8rem;
            background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 9999px;
            font-size: 0.875rem;
            color: var(--primary-dark);
            transition: all 0.2s ease;
        }}

        .keyword-tag:hover {{
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        }}

        .keyword-tag .count {{
            background: var(--primary);
            color: white;
            font-size: 0.75rem;
            padding: 0.1rem 0.4rem;
            border-radius: 9999px;
            font-weight: 600;
        }}

        .articles-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}

        .articles-table th {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 2px solid var(--border);
            font-weight: 600;
            color: var(--text-light);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .articles-table td {{
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
        }}

        .articles-table tr:hover td {{
            background: #f8fafc;
        }}

        .articles-table .title {{
            font-weight: 500;
            color: var(--primary-dark);
            text-decoration: none;
        }}

        .articles-table .title:hover {{
            text-decoration: underline;
        }}

        .articles-table .meta {{
            font-size: 0.8rem;
            color: var(--text-light);
        }}

        .footer {{
            text-align: center;
            padding: 3rem 1rem;
            color: var(--text-light);
            font-size: 0.875rem;
        }}

        .footer a {{
            color: var(--primary);
            text-decoration: none;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .animate-in {{
            animation: fadeIn 0.6s ease forwards;
        }}

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.75rem; }}
            .header {{ padding: 2rem max(1rem,env(safe-area-inset-right,1rem)) 2rem max(1rem,env(safe-area-inset-left,1rem)); }}
            .container {{ padding: 1rem max(1rem,env(safe-area-inset-right,1rem)) 4rem max(1rem,env(safe-area-inset-left,1rem)); }}
            .charts-grid {{ grid-template-columns: 1fr; }}
            .domain-grid {{ grid-template-columns: 1fr; }}
            .time-selector {{ gap: 0.35rem; }}
            .time-btn {{ padding: 0.5rem 1rem; font-size: 0.85rem; }}
        }}

        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg);
        }}

        ::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>医学研究热点文献计量报告</h1>
        <p>基于 PubMed/MEDLINE 公共数据库的实时文献计量分析</p>
        <span class="badge" id="update-time">加载中...</span>
    </header>

    <div class="container">
        <div class="time-selector" id="time-selector">
            <button class="time-btn active" data-time="past_week">过去一周</button>
            <button class="time-btn" data-time="past_month">过去一月</button>
            <button class="time-btn" data-time="past_6months">过去半年</button>
            <button class="time-btn" data-time="past_year">过去一年</button>
        </div>

        <div class="stats-grid" id="stats-grid">
            <div class="stat-card">
                <div class="icon blue">&#128218;</div>
                <div class="value" id="stat-total">-</div>
                <div class="label">收录文献总数</div>
            </div>
            <div class="stat-card">
                <div class="icon purple">&#127919;</div>
                <div class="value" id="stat-domains">-</div>
                <div class="label">研究领域数</div>
            </div>
            <div class="stat-card">
                <div class="icon green">&#128161;</div>
                <div class="value" id="stat-keywords">-</div>
                <div class="label">热点关键词</div>
            </div>
            <div class="stat-card">
                <div class="icon orange">&#128195;</div>
                <div class="value" id="stat-journals">-</div>
                <div class="label">活跃期刊数</div>
            </div>
            <div class="stat-card">
                <div class="icon cyan">&#128197;</div>
                <div class="value" id="stat-range">-</div>
                <div class="label">数据时间范围</div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title"><span class="icon">&#128202;</span> 领域分布与趋势</h2>
            <div class="charts-grid">
                <div id="domain-chart-container"></div>
                <div id="keyword-chart-container"></div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title"><span class="icon">&#127942;</span> 各领域发文量</h2>
            <div class="domain-grid" id="domain-grid"></div>
        </div>

        <div class="section">
            <h2 class="section-title"><span class="icon">&#128293;</span> 热门关键词</h2>
            <div class="keywords-container" id="keywords-container"></div>
        </div>

        <div class="section">
            <h2 class="section-title"><span class="icon">&#128220;</span> 代表性文献</h2>
            <div style="overflow-x: auto;">
                <table class="articles-table" id="articles-table">
                    <thead>
                        <tr>
                            <th>标题</th>
                            <th>期刊</th>
                            <th>作者</th>
                            <th>日期</th>
                        </tr>
                    </thead>
                    <tbody id="articles-tbody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>数据来源：<a href="https://pubmed.ncbi.nlm.nih.gov/" target="_blank">PubMed/MEDLINE (NCBI)</a> | 分析方法：文献计量学 (Bibliometrics)</p>
        <p>本报告基于公共数据库自动生成，仅供学术研究参考</p>
        <p style="margin-top: 0.5rem;">生成时间：<span id="footer-time"></span></p>
    </footer>

    <script>
        const REPORTS = {reports_json};

        let currentTimeRange = 'past_week';

        const TIME_LABELS = {{
            'past_week': '过去一周',
            'past_month': '过去一月',
            'past_6months': '过去半年',
            'past_year': '过去一年'
        }};

        const COLORS = [
            '#2563eb', '#7c3aed', '#06b6d4', '#10b981',
            '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6',
            '#14b8a6', '#f97316'
        ];

        document.addEventListener('DOMContentLoaded', () => {{
            setupTimeSelector();
            render(currentTimeRange);
        }});

        function setupTimeSelector() {{
            const buttons = document.querySelectorAll('.time-btn');
            buttons.forEach(btn => {{
                btn.addEventListener('click', () => {{
                    buttons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentTimeRange = btn.dataset.time;
                    render(currentTimeRange);
                }});
            }});
        }}

        function render(timeRange) {{
            const data = REPORTS[timeRange];
            if (!data) {{
                console.error('No data for', timeRange);
                return;
            }}

            updateStats(data);
            renderDomainChart(data);
            renderKeywordChart(data);
            renderDomainCards(data);
            renderKeywords(data);
            renderArticles(data);
            updateTime(data);
        }}

        function updateStats(data) {{
            document.getElementById('stat-total').textContent = data.summary.total_articles.toLocaleString();
            document.getElementById('stat-domains').textContent = data.summary.domains_analyzed;
            document.getElementById('stat-keywords').textContent = data.global_keywords.length;

            const journals = new Set();
            data.domains.forEach(d => {{
                d.top_journals.forEach(j => journals.add(j.name));
            }});
            document.getElementById('stat-journals').textContent = journals.size;
            document.getElementById('stat-range').textContent = TIME_LABELS[timeRange] || timeRange;
        }}

        function renderDomainChart(data) {{
            const container = document.getElementById('domain-chart-container');
            const domains = data.domains;
            const total = domains.reduce((sum, d) => sum + d.count, 0);
            
            let svg = '<svg class="svg-chart" viewBox="0 0 500 350">';
            svg += '<text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">各领域文献占比</text>';
            
            let currentAngle = 0;
            const centerX = 180;
            const centerY = 190;
            const radius = 100;
            
            domains.forEach((d, i) => {{
                const angle = (d.count / total) * 2 * Math.PI;
                const x1 = centerX + radius * Math.cos(currentAngle);
                const y1 = centerY + radius * Math.sin(currentAngle);
                const x2 = centerX + radius * Math.cos(currentAngle + angle);
                const y2 = centerY + radius * Math.sin(currentAngle + angle);
                const largeArc = angle > Math.PI ? 1 : 0;
                
                svg += `<path d="M ${{centerX}},${{centerY}} L ${{x1}},${{y1}} A ${{radius}},${{radius}} 0 ${{largeArc}},1 ${{x2}},${{y2}} Z" fill="${{COLORS[i % COLORS.length]}}" stroke="white" stroke-width="2"/>`;
                currentAngle += angle;
            }});
            
            // Legend
            domains.forEach((d, i) => {{
                const y = 80 + i * 28;
                svg += `<rect x="320" y="${{y-8}}" width="16" height="16" rx="4" fill="${{COLORS[i % COLORS.length]}}"/>`;
                svg += `<text x="345" y="${{y+4}}" font-size="12" fill="#334155">${{d.domain}} (${{d.count}})</text>`;
            }});
            
            svg += '</svg>';
            container.innerHTML = svg;
        }}

        function renderKeywordChart(data) {{
            const container = document.getElementById('keyword-chart-container');
            const keywords = data.global_keywords.slice(0, 15);
            const maxCount = Math.max(...keywords.map(k => k.count));
            
            let svg = '<svg class="svg-chart" viewBox="0 0 500 350">';
            svg += '<text x="250" y="20" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Top 15 热门关键词</text>';
            
            const barHeight = 18;
            const gap = 4;
            const startY = 45;
            const maxBarWidth = 300;
            const labelWidth = 140;
            
            keywords.forEach((k, i) => {{
                const y = startY + i * (barHeight + gap);
                const barWidth = (k.count / maxCount) * maxBarWidth;
                
                svg += `<text x="${{labelWidth-5}}" y="${{y+13}}" text-anchor="end" font-size="11" fill="#475569">${{k.term}}</text>`;
                svg += `<rect x="${{labelWidth+5}}" y="${{y}}" width="${{barWidth}}" height="${{barHeight}}" rx="4" fill="rgba(37,99,235,0.7)"/>`;
                svg += `<text x="${{labelWidth+10+barWidth}}" y="${{y+13}}" font-size="11" fill="#64748b">${{k.count}}</text>`;
            }});
            
            svg += '</svg>';
            container.innerHTML = svg;
        }}

        function renderDomainCards(data) {{
            const container = document.getElementById('domain-grid');
            const maxCount = Math.max(...data.domains.map(d => d.count));

            container.innerHTML = data.domains.map((d, i) => {{
                const percent = maxCount > 0 ? (d.count / maxCount * 100) : 0;
                return `
                    <div class="domain-card animate-in" style="animation-delay: ${{i * 0.05}}s">
                        <div class="domain-name">${{d.domain}}</div>
                        <div class="domain-count">${{d.count.toLocaleString()}}</div>
                        <div class="domain-bar">
                            <div class="domain-bar-fill" style="width: ${{percent}}%"></div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function renderKeywords(data) {{
            const container = document.getElementById('keywords-container');
            container.innerHTML = data.global_keywords.slice(0, 40).map((k, i) => `
                <span class="keyword-tag animate-in" style="animation-delay: ${{i * 0.02}}s">
                    ${{k.term}}
                    <span class="count">${{k.count}}</span>
                </span>
            `).join('');
        }}

        function renderArticles(data) {{
            const tbody = document.getElementById('articles-tbody');
            const allArticles = [];
            data.domains.forEach(d => {{
                d.articles.forEach(a => {{
                    allArticles.push({{...a, domain: d.domain}});
                }});
            }});

            allArticles.sort((a, b) => new Date(b.pubdate || 0) - new Date(a.pubdate || 0));
            const topArticles = allArticles.slice(0, 20);

            tbody.innerHTML = topArticles.map(a => `
                <tr>
                    <td>
                        <a href="https://pubmed.ncbi.nlm.nih.gov/${{a.pmid}}/" target="_blank" class="title">${{a.title || 'Untitled'}}</a>
                        <div class="meta">PMID: ${{a.pmid}} | 领域: ${{a.domain}}</div>
                    </td>
                    <td>${{a.journal || '-'}}</td>
                    <td>${{(a.authors || []).slice(0, 3).join(', ')}}${{(a.authors || []).length > 3 ? ' et al.' : ''}}</td>
                    <td>${{a.pubdate || '-'}}</td>
                </tr>
            `).join('');
        }}

        function updateTime(data) {{
            const date = new Date(data.generated_at);
            const fmt = date.toLocaleString('zh-CN');
            document.getElementById('update-time').textContent = `更新时间: ${{fmt}}`;
            document.getElementById('footer-time').textContent = fmt;
        }}
    </script>
</body>
</html>
'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML报告已生成: {output_path}")


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"
    output_path = Path(__file__).parent.parent / "index.html"

    reports = load_reports(data_dir)
    if reports:
        generate_html(reports, output_path)
    else:
        print("未找到报告数据，请先运行 fetch_pubmed.py")
