#!/usr/bin/env python3
"""
weread-full-stats.py — 微信读书完整统计分析 + 可视化
依赖：pip3 install jieba wordcloud matplotlib numpy pillow -q
"""
import os, glob, re, yaml, sys
from collections import Counter, defaultdict
from datetime import datetime
import jieba
import jieba.analyse

# ── Config ─────────────────────────────────────────────────────────────────
VAULT = os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/oneinall/raw/Weread")
OUT_DIR = os.path.expanduser("~/hermes/cards")
FONT_CJK = "/System/Library/Fonts/STHeiti Medium.ttc"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Font setup ──────────────────────────────────────────────────────────────
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from wordcloud import WordCloud
from PIL import Image
import numpy as np

plt.rcParams['font.sans-serif'] = ['STHeiti Medium', 'Hiragino Sans GB']
plt.rcParams['axes.unicode_minus'] = False

files = glob.glob(VAULT + "/*.md")
print(f"📚 藏书：{len(files)} 本")

# ── 1. 提取高亮 ────────────────────────────────────────────────────────────
all_highlights = []
book_finished = []
book_meta_map = {}

for f in files:
    with open(f, 'r', errors='ignore') as fh:
        content = fh.read()
    name = os.path.basename(f).replace('.md', '')
    title = name.rsplit('-', 1)[0].strip() if '-' in name else name.strip()

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1])
                progress = str(meta.get('progress', ''))
                finished = meta.get('finishedDate', '')
                if hasattr(finished, 'strftime'):
                    finished = finished.strftime('%Y-%m-%d')
                book_meta_map[name] = {
                    'title': title,
                    'author': str(meta.get('author', '')),
                    'progress': progress,
                    'finished': finished,
                    'readingTime': str(meta.get('readingTime', '')),
                    'noteCount': int(meta.get('noteCount', 0) or 0),
                }
                if progress == '100%' and finished:
                    book_finished.append({
                        'date': finished, 'title': title,
                        'author': str(meta.get('author', '')),
                        'readingTime': str(meta.get('readingTime', '')),
                        'noteCount': int(meta.get('noteCount', 0) or 0)
                    })
            except:
                pass

    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') and len(stripped) > 10:
            text = re.sub(r'\s*\[\[.*?\]\]\s*$', '', stripped)
            text = re.sub(r'\s*\^[\w-]+\s*$', '', text).strip()
            if len(text) > 5:
                all_highlights.append(text)

book_finished.sort(key=lambda x: x['date'] or '', reverse=True)
total_chars = sum(os.path.getsize(f) for f in files)
total_lines = sum(open(ff, errors='ignore').read().count('\n') for ff in files)
print(f"📝 笔记：{total_chars/1024/1024:.1f} MB / {total_lines:,} 行")
print(f"✅ 已读完：{len(book_finished)} 本")
print(f"💬 高亮笔记：{len(all_highlights)} 条")

# Reading time total
total_min = 0
for b in book_finished:
    rt = b.get('readingTime', '')
    if '小时' in rt:
        parts = rt.split('小时')
        h = int(parts[0]) if parts[0] else 0
        m = int(parts[1].replace('分钟','').strip()) if len(parts) > 1 and '分钟' in parts[1] else 0
        total_min += h * 60 + m
print(f"⏱ 累计阅读时长：{total_min//60}h {total_min%60}min")

# ── 2. 分词与词频 ──────────────────────────────────────────────────────────
STOPWORDS = set(['的','是','在','了','和','与','就','都','而','及','着','或',
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
    '而是','由于','所有','任何','不能','这些','那些','这么','那么','还是',
    'fisheryounggod_picsbed','https_cdn','cdn_jsdelivr','jsdelivr_net',
    'net_gh','gh_fisheryounggod','picsbed_uPic','400_https','of_the',
    '一篇_文章','非常_重要'])

word_freq = Counter()
for text in all_highlights:
    for w in jieba.cut(text):
        w = w.strip()
        if len(w) >= 2 and w not in STOPWORDS and not w.isdigit() and not re.match(r'^[\W_]+$', w):
            word_freq[w] += 1

all_text = '\n'.join(all_highlights)
print(f"🏷 独特词汇：{len(word_freq):,}")

# ── 3. 双词组合 ────────────────────────────────────────────────────────────
words_all = [w.strip() for w in jieba.cut(all_text) if w.strip() and len(w.strip()) >= 2]
bigrams = Counter()
for i in range(len(words_all) - 1):
    w1, w2 = words_all[i], words_all[i+1]
    if w1 not in STOPWORDS and w2 not in STOPWORDS and len(w1) >= 2 and len(w2) >= 2:
        bigrams[f"{w1}_{w2}"] += 1

# ── 4. 领域覆盖 ───────────────────────────────────────────────────────────
DOMAINS = {
    '制度/政治':   ['国家','政府','政治','制度','政策','权力','民主','法律','治理','体制','监管','合规','腐败','法治','分权'],
    '宏观经济':    ['经济','增长','GDP','财政','通胀','产出','预算','税收','国债','衰退','滞胀','总需求','总供给'],
    '投资/金融':   ['投资','资本','资产','风险','债券','股票','收益率','波动','溢价','配置','组合','期货','期权','衍生品','估值'],
    'CBDC/货币':   ['货币','利率','汇率','美元','流动性','央行','存款','准备金','外汇','人民币','广义货币','货币供给'],
    '经济学理论':  ['变量','假设','函数','均衡','博弈','博弈论','纳什','信息不对称','委托代理','激励','约束','效用','偏好'],
    '历史/思想史': ['历史','哲学','学派','凯恩斯','马克思','哈耶克','弗里德曼','李嘉图','亚当斯密','瓦尔拉斯','边际革命'],
    '科学方法论':  ['数据','回归','样本','实验','实证','因果','计量','显著性','置信区间','假设检验','面板','时间序列'],
}

domain_data = {}
for domain, keywords in DOMAINS.items():
    total = sum(word_freq.get(k, 0) for k in keywords)
    kw_sorted = sorted([(k, word_freq.get(k,0)) for k in keywords if word_freq.get(k,0) > 0], key=lambda x: -x[1])
    domain_data[domain] = {'total': total, 'keywords': kw_sorted}

# ── 5. 可视化 ────────────────────────────────────────────────────────────
COLORS_7 = ['#E85D75','#5B8EDB','#E8945A','#7CB97A','#9B7EBD','#E0A030','#5AB8B0']
BG = '#F7F5F0'

# 5a. 词云
print("🖼 生成词云...")
wc_data = {w: c for w, c in word_freq.most_common(300)}
wc = WordCloud(font_path=FONT_CJK, width=1600, height=900,
               background_color='#1A1A2E', max_words=200, max_font_size=130,
               min_font_size=12,
               colormap=LinearSegmentedColormap.from_list('custom', ['#7CB97A','#B8D8BE','#E8F5E9','#FFFFFF']),
               random_state=42)
wc.generate_from_frequencies(wc_data)
wc.to_file(f"{OUT_DIR}/wordcloud.png")
print(f"   → {OUT_DIR}/wordcloud.png")

# 5b. 领域柱图
print("📊 生成领域柱图...")
fig, ax = plt.subplots(figsize=(14, 7))
domains_list = list(domain_data.keys())
totals = [domain_data[d]['total'] for d in domains_list]
bars = ax.barh(domains_list[::-1], totals[::-1], color=COLORS_7[::-1], height=0.6, edgecolor='none')
for bar, val in zip(bars, totals[::-1]):
    ax.text(val + 80, bar.get_y() + bar.get_height()/2, f'{val:,}', va='center', fontsize=13, color='#333')
ax.set_xlabel('出现频次', fontsize=12, color='#666')
ax.set_xlim(0, max(totals) * 1.12)
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=11)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
ax.spines['left'].set_color('#DDD'); ax.spines['bottom'].set_color('#DDD')
ax.set_facecolor('#FAFAFA'); fig.patch.set_facecolor(BG)
ax.set_title('微信读书笔记 · 领域分布', fontsize=18, fontweight='bold', color='#1A1A1A', pad=20)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/domain_chart.png", dpi=150, bbox_inches='tight'); plt.close()
print(f"   → {OUT_DIR}/domain_chart.png")

# 5c. 双词柱图
print("📊 生成双词柱图...")
fig, ax = plt.subplots(figsize=(14, 8))
top_bg = bigrams.most_common(20)
labels = [bg.replace('_', ' ') for bg, _ in top_bg]
values = [c for _, c in top_bg]
c_list = ['#E85D75' if i < 5 else '#5B8EDB' if i < 10 else '#7CB97A' for i in range(len(labels))]
bars = ax.barh(labels[::-1], values[::-1], color=c_list[::-1], height=0.65, edgecolor='none')
for bar, val in zip(bars, values[::-1]):
    ax.text(val + 3, bar.get_y() + bar.get_height()/2, str(val), va='center', fontsize=11, color='#555')
ax.set_xlabel('频次', fontsize=12, color='#666')
ax.set_xlim(0, max(values) * 1.15)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
ax.spines['left'].set_color('#DDD'); ax.spines['bottom'].set_color('#DDD')
ax.set_facecolor('#FAFAFA'); fig.patch.set_facecolor(BG)
ax.tick_params(axis='y', labelsize=13); ax.tick_params(axis='x', labelsize=11)
ax.set_title('高频双词组合 TOP 20', fontsize=18, fontweight='bold', color='#1A1A1A', pad=20)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/bigram_chart.png", dpi=150, bbox_inches='tight'); plt.close()
print(f"   → {OUT_DIR}/bigram_chart.png")

# 5d. 月度热力图
print("🗓 生成热力图...")
monthly = Counter()
for b in book_finished:
    d = b.get('date', '')
    if d and (d.startswith('2024-') or d.startswith('2025-') or d.startswith('2026-')):
        monthly[d[:7]] += 1

all_months = ([f"2024-{m:02d}" for m in range(1,13)] +
              [f"2025-{m:02d}" for m in range(1,13)] +
              [f"2026-{m:02d}" for m in range(1,13)])
all_months_f = [m for m in all_months if monthly.get(m,0) > 0 or m >= '2026-01']

if all_months_f:
    matrix_data = [[monthly.get(m, 0)] for m in all_months_f]
    fig, ax = plt.subplots(figsize=(4, max(8, len(all_months_f)*0.5)))
    matrix = np.array(matrix_data).T
    cmap = LinearSegmentedColormap.from_list('custom', ['#F7F5F0','#B8D8BE','#7CB97A','#2D6A30'])
    ax.imshow(matrix, cmap=cmap, aspect='auto', interpolation='nearest')
    ax.set_yticks([0]); ax.set_yticklabels(['阅读量']); ax.set_xticks([])
    ax.set_yticks(range(len(all_months_f)))
    ax.set_yticklabels(all_months_f, fontsize=9)
    for i, row in enumerate(matrix_data):
        if row[0] > 0:
            ax.text(-0.3, i, str(row[0]), va='center', ha='right', fontsize=9, color='#333')
    ax.set_title('月度阅读量热力图\n(2024–2026)', fontsize=12, fontweight='bold', color='#1A1A1A')
    fig.patch.set_facecolor(BG)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/heatmap.png", dpi=150, bbox_inches='tight'); plt.close()
    print(f"   → {OUT_DIR}/heatmap.png")

# 5e. 阅读时长分布
print("📊 生成阅读时长分布图...")
bins = [30, 60, 120, 300, 600]
labels_bin = ['<30分钟', '30-60分', '1-2h', '2-5h', '5-10h', '>10h']
counts_bin = [0, 0, 0, 0, 0, 0]
for b in book_finished:
    rt = b.get('readingTime', '')
    mins = 0
    if '小时' in rt:
        parts = rt.split('小时')
        mins = int(parts[0]) * 60 if parts[0] else 0
        if len(parts) > 1 and '分钟' in parts[1]:
            mins += int(parts[1].replace('分钟', '').strip())
    if mins < 30:
        counts_bin[0] += 1
    elif mins < 60:
        counts_bin[1] += 1
    elif mins < 120:
        counts_bin[2] += 1
    elif mins < 300:
        counts_bin[3] += 1
    elif mins < 600:
        counts_bin[4] += 1
    else:
        counts_bin[5] += 1

fig, ax = plt.subplots(figsize=(10, 5))
colors_bin = ['#B8D8BE','#7CB97A','#5B8EDB','#9B7EBD','#E8945A','#E85D75']
bars = ax.bar(labels_bin, counts_bin, color=colors_bin, edgecolor='none', width=0.6)
for bar, val in zip(bars, counts_bin):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1, str(val),
            ha='center', va='bottom', fontsize=13, fontweight='bold', color='#333')
ax.set_ylabel('书籍数量', fontsize=12, color='#666')
ax.set_ylim(0, max(counts_bin)*1.15)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
ax.spines['left'].set_color('#DDD'); ax.spines['bottom'].set_color('#DDD')
ax.set_facecolor('#FAFAFA'); fig.patch.set_facecolor(BG)
ax.tick_params(axis='x', labelsize=12); ax.tick_params(axis='y', labelsize=11)
ax.set_title('已读书籍阅读时长分布', fontsize=16, fontweight='bold', color='#1A1A1A', pad=16)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/reading_time_dist.png", dpi=150, bbox_inches='tight'); plt.close()
print(f"   → {OUT_DIR}/reading_time_dist.png")

print(f"\n✅ 完成！图表 → ~/hermes/cards/")
print("   wordcloud.png  domain_chart.png  bigram_chart.png  heatmap.png  reading_time_dist.png")
