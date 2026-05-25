# Weread 笔记分词与领域分析

> ⚠️ 完整版分析脚本已迁移到 `scripts/weread-full-stats.py`，直接运行即可生成所有可视化图表。本文件保留为基础参考。

## 快速运行

```bash
# 一次性生成所有图表
python3 scripts/weread-full-stats.py

# 依赖（首次需安装）
pip3 install jieba wordcloud matplotlib numpy pillow -q
```

## 脚本输出

- `~/hermes/cards/wordcloud.png` — 词云
- `~/hermes/cards/domain_chart.png` — 领域分布柱图
- `~/hermes/cards/bigram_chart.png` — 双词组合柱图
- `~/hermes/cards/heatmap.png` — 月度阅读热力图
- `~/hermes/cards/reading_time_dist.png` — 阅读时长分布

```python
import os, glob, re, yaml
from collections import Counter
import jieba
import jieba.analyse

vault = "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/oneinall/raw/Weread"
files = glob.glob(os.path.expanduser(vault + "/*.md"))

# ── 1. 提取高亮 ──────────────────────────────────────────
all_highlights = []
for f in files:
    with open(f, 'r', errors='ignore') as fh:
        content = fh.read()
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') and len(stripped) > 10:
            text = re.sub(r'\s*\[\[.*?\]\]\s*$', '', stripped)   # 去[[日期]]
            text = re.sub(r'\s*\^[\w-]+\s*$', '', text)          # 去^引用ID
            text = text.strip()
            if len(text) > 5:
                all_highlights.append(text)

print(f"总高亮数：{len(all_highlights)}")

# ── 2. 已读完书籍（progress=100% + finishedDate）────────
finished = []
for f in files:
    with open(f, 'r', errors='ignore') as fh:
        content = fh.read()
    if not content.startswith('---'):
        continue
    parts = content.split('---', 2)
    if len(parts) < 3:
        continue
    try:
        meta = yaml.safe_load(parts[1])
    except:
        continue
    if meta.get('progress') == '100%' and meta.get('finishedDate'):
        name = os.path.basename(f).replace('.md', '')
        title = name.rsplit('-', 1)[0].strip() if '-' in name else name.strip()
        fd = meta.get('finishedDate', '')
        if hasattr(fd, 'strftime'):
            fd = fd.strftime('%Y-%m-%d')
        finished.append({
            'title': title,
            'author': str(meta.get('author', '')),
            'finishedDate': fd,
            'readingTime': str(meta.get('readingTime', '')),
            'noteCount': int(meta.get('noteCount', 0) or 0),
        })

finished.sort(key=lambda x: x['finishedDate'] or '', reverse=True)
print(f"已读完：{len(finished)} 本")

# ── 3. 分词与词频 ───────────────────────────────────────
stopwords = set(['的','是','在','了','和','与','就','都','而','及','着','或',
    '一个','一','也','不','有','这','个','人','他','她','它','们','那','你',
    '我','要','会','可以','没有','什么','怎么','如果','因为','所以','但是',
    '但','还','又','只','很','最','被','把','让','从','到','对','以','能',
    '可','说','做','去','来','看','想','知道','认为','可能','已经','自己',
    '这种','这样','那样','一些','其实','当然','然后','虽然','或者','而且',
    '并且','因此','这个','那个','为了','关于','对于','通过','按照','根据',
    '作为','除了','以及','之后','之前','之中','之间','时候','东西','事情',
    '问题','方式','过程','结果','原因','意义','价值','目标','方法','能力',
    '水平','状态','关系','条件','环境','资源','资料','信息','知识','概念',
    '理论','思想','观点','看法','态度','情感','心理','行为','习惯','规律',
    '原则','规则','标准','特点','特征','类型','分类','时期','时代','阶段',
    '层面','角度','领域','方面','范围','程度','速度','规模','数量','质量',
    '效果','影响','作用','功能','结构','系统','模式','机制','模型','框架',
    '路径','路线','策略','计划','方案','建议','意见','评价','分析','研究',
    '讨论','说明','解释','理解','认识','发现','提出','强调','注重','关注',
    '重视','涉及','包括','属于','形成','产生','出现','存在','表现','体现',
    '反映','揭示','表明','证明','实现','完成','开始','继续','结束','改变',
    '改善','改进','提高','加强','建立','发展','提供','获得','取得','达到',
    '得到','失去','缺乏','需要','要求','希望','愿意','能够','应该','必须',
    '不得','只好','只有','只要','无论','不管','即使','哪怕','尽管','不过',
    '然而','反而','相反','此外','另外','总之','总体','一般','通常','往往',
    '常常','经常','总是','从不','从未','曾经','正在','将要','马上','立刻',
    '逐渐','渐渐','慢慢','日益','越来越','一点','一样','一起','一直','一定',
    '一切','其他','其余','其中','当','每','各','某','本','其','该','这些',
    '那些','以上','以下','之内','之外','之上','之下','之处','之际','之势',
    '之力','之道','之法','之术','之心','之意','之情','之理','之论','之说',
    '之言','之行','为','比','更','越','还','再','才','便','即','则','且',
    '乃','乎','焉','哉','矣','嘛','呢','吧','啊','么','得','地','着','过',
    '起来','出来','进来','回来','下来','上来','过去','过来','下去','回去',
    '我们','就是','他们','她们','它们','一种','不是','两个','那么','只是',
    '而是','由于','所有','任何','不能','这些','那些','这么','那么','还是'])

word_freq = Counter()
for text in all_highlights:
    for w in jieba.cut(text):
        w = w.strip()
        if len(w) >= 2 and w not in stopwords and not w.isdigit() and not re.match(r'^[\W_]+$', w):
            word_freq[w] += 1

print(f"独特词数：{len(word_freq)}")
print("TOP 20:", word_freq.most_common(20))

# ── 4. TF-IDF ───────────────────────────────────────────
all_text = '\n'.join(all_highlights)
tfidf = jieba.analyse.extract_tags(all_text, topK=60, withWeight=True)
for word, weight in tfidf:
    print(f"  {word}: {weight:.4f}")

# ── 5. 双词组合 ─────────────────────────────────────────
words_all = [w.strip() for w in jieba.cut(all_text) if w.strip() and len(w.strip()) >= 2]
bigrams = Counter()
for i in range(len(words_all) - 1):
    w1, w2 = words_all[i], words_all[i+1]
    if w1 not in stopwords and w2 not in stopwords and len(w1) >= 2 and len(w2) >= 2:
        bigrams[f"{w1}_{w2}"] += 1
print("Bigrams TOP 20:", bigrams.most_common(20))

# ── 6. 领域覆盖分析 ─────────────────────────────────────
domains = {
    'CBDC/货币':   ['货币','央行','数字货币','CBDC','DC/EP','比特币','加密货币','货币政策','利率','流动性','存款','准备金','铸币税','外汇','汇率','美元','人民币'],
    '宏观经济':    ['经济','GDP','通胀','通货膨胀','通缩','滞胀','增长','衰退','产出','总需求','总供给','财政','预算','税收','国债','M2','信贷','杠杆'],
    '投资/金融':   ['投资','资本','资产','收益率','回报','风险','溢价','波动','配置','组合','期货','期权','衍生品','债券','股票','股权','估值','现金流'],
    '制度/政治':   ['制度','政府','国家','政治','监管','合规','法律','法规','政策','体制','治理','腐败','权力','民主','法治'],
    '经济学理论':  ['模型','假设','变量','函数','均衡','博弈','博弈论','纳什','信息不对称','委托代理','激励','约束','最优化','效用','偏好'],
    '历史/思想史': ['历史','哲学','学派','重农学派','重商主义','古典经济学','凯恩斯','弗里德曼','哈耶克','马克思','亚当斯密','李嘉图'],
    '科学方法论':  ['数据','实证','计量','回归','因果','显著性','置信区间','假设检验','样本','面板','时间序列','自然实验','断点回归','双重差分','工具变量'],
}
for domain, keywords in domains.items():
    total = sum(word_freq.get(k, 0) for k in keywords)
    top_k = sorted([(k, word_freq.get(k,0)) for k in keywords if word_freq.get(k,0)>0], key=lambda x:-x[1])
    print(f"\n【{domain}】{total}次")
    for k, c in top_k[:8]:
        print(f"  {k}: {c}")
```

## 关键坑

- **pip vs pip3**：jieba 安装在 `/opt/anaconda3/bin/python3`，sandbox 用的是另一个 Python。直接 `python3` 或 `pip3 install jieba -q` 再跑脚本。
- **frontmatter date类型**：yaml.safe_load 解析后 `finishedDate` 可能是 `datetime.date` 对象，调用 `.strftime('%Y-%m-%d')` 前先判 `hasattr(fd, 'strftime')`。
- **URL干扰**：图片CDN链接（`https://cdn.jsdelivr.net/...`）会进bigrams，需在stopwords里加 `fisheryounggod_picsbed`、`picsbed_uPic` 等噪声词。
- **书名解析**：文件名格式为 `书名-作者`，`.rsplit('-', 1)[0]` 取第一部分得书名（中文书名本身含`-`的另处理）。

## 输出卡片

结果用 `ljg-card -i`（信息图）做成阅读报告卡，输出到 `~/hermes/cards/`。
