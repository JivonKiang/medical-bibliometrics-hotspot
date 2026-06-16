# 医学研究热点文献计量报告

基于 **PubMed/MEDLINE** 公共数据库的医学研究热点自动追踪与文献计量分析系统。

## 项目概述

本项目通过文献计量学 (Bibliometrics) 方法，自动追踪和分析过去一周、一月、半年、一年等多个时间维度内全球医学研究的热点趋势。所有数据来源于 **NCBI PubMed** 公共数据库，无需任何付费订阅或特殊权限。

## 数据来源

- **数据库**: [PubMed/MEDLINE](https://pubmed.ncbi.nlm.nih.gov/) (NCBI)
- **API**: [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/)
- **覆盖领域**: 肿瘤学、心血管疾病、神经科学、免疫学、传染病、代谢疾病、精准医学、AI医学、基因组学、干细胞

## 技术架构

```
scripts/
  fetch_pubmed.py      # PubMed数据采集与分析
  generate_html.py     # HTML报告生成
data/
  report_*.json        # 各时间范围的分析结果
.github/workflows/
  update-report.yml    # GitHub Actions自动更新
index.html             # GitHub Pages展示页面
```

## 自动化更新

通过 GitHub Actions 实现全自动更新：
- **每日更新**: 每天凌晨自动抓取最新数据
- **手动触发**: 支持在 Actions 页面手动运行

## 查看报告

访问 GitHub Pages 查看实时报告：
https://jivonkiang.github.io/medical-bibliometrics-hotspot/

## 本地运行

```bash
# 克隆仓库
git clone https://github.com/JivonKiang/medical-bibliometrics-hotspot.git
cd medical-bibliometrics-hotspot

# 安装依赖
pip install requests

# 生成报告
python scripts/fetch_pubmed.py
python scripts/generate_html.py

# 打开 index.html 查看
```

## 文献参考

本项目的分析方法基于以下文献计量学最佳实践：

1. **Shi J, et al.** "Mapping the Bibliometrics Landscape of AI in Medicine: Methodological Study." *J Med Internet Res.* 2023;25:e45815. [DOI:10.2196/45815](https://doi.org/10.2196/45815)

2. **Aria M, Cuccurullo C.** "bibliometrix: An R-tool for comprehensive science mapping analysis." *J Informetr.* 2017;11(4):959-975.

3. **van Eck NJ, Waltman L.** "Software survey: VOSviewer, a computer program for bibliometric mapping." *Scientometrics.* 2010;84(2):523-538.

4. **Chen C.** "CiteSpace II: Detecting and visualizing emerging trends and transient patterns in scientific literature." *J Am Soc Inf Sci Technol.* 2006;57(3):359-377.

5. **Zhang Z, et al.** "A Bibliometric Analysis of 8,276 Publications During the Past 25 Years on Cholangiocarcinoma by Machine Learning." *Front Oncol.* 2021;11:687904.

## 许可证

MIT License - 本项目完全开源，欢迎 fork 和贡献。

## 免责声明

本报告基于公共数据库自动生成，仅供学术研究参考。具体临床决策请遵循专业医学指南。
