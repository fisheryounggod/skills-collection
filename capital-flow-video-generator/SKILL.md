---
name: capital-flow-video-generator
description: This skill should be used when the user asks to "generate a capital flow video", "save capital flow animation", "convert capital flow to mp4", "create a sector dynamic video", "record sector animation", or mentions exporting capital flow videos. Provides comprehensive, offline-rendered video generation pipeline for A-share sector fund flows.
version: 0.1.0
---

# A股主力资金分时动态视频导出分析器

本 Skill 指导 Agent 在抓取东方财富主力资金数据的基础上，完成特定细分板块的分钟级分时动态变化视频（MP4/GIF 格式）的录制与物理导出。

## 核心前提

1. **依赖库**：验证系统已装载 `pandas`、`matplotlib` 以及 `openpyxl`。
2. **多媒体编码器**：验证系统已安装 macOS Homebrew 版本的 `ffmpeg`（绝对路径为 `/opt/homebrew/bin/ffmpeg`）。
3. **输出目录**：所有录制导出的视频及大图统一存放于 `/Users/mac/Downloads/主力资金数据/`。

---

## 运行与操作流程

若要根据用户指定的板块和时间导出资金分时动态视频，执行以下流程：

### 第一步：定位板块代码与分时数据

1. 检索核心板块代码映射。查询并确认目标板块所对应的东财标准代码，详细映射关系参见：
   * **`references/sector_codes.md`** —— 22 核心主力板块映射表。
2. 检索并确认本地分时数据源。检查以下路径是否已包含今日该板块的分时 CSV 数据：
   * `/Users/mac/Downloads/Data/sector_data/[板块名称]_fund_flow.csv`
3. 若数据不存在或已过期，调用数据爬虫先进行实时抓取：
   * **医疗板块**（医疗器械、医疗服务、医药生物）：运行 `python3 crawl_and_draw_medical.py [板块名称]`
   * **其他 19 个核心板块**：运行 `python3 eastmoney_sector_flow.py` 刷新缓存

---

### 第二步：执行后台静默高清压制渲染

使用共享核心绘制模块 `animation_player.py` 的物理压制模式，通过 Python 后台静默调用 `ffmpeg` 编码器导出 MP4 视频。

#### 核心脚本调用模式

在 `/Users/mac/Downloads/Data/` 路径下，通过 Python 交互式单行指令执行视频生成：

```python
import os
import sys
import pandas as pd

# 1. 载入目标分时数据
csv_path = "sector_data/有色金属_fund_flow.csv"  # 替换为目标板块
df = pd.read_csv(csv_path)

# 2. 提取日期标识
date_str = df['time'].iloc[0].split(' ')[0] if 'time' in df.columns else "今日"

# 3. 载入动态导出引擎
sys.path.append(os.getcwd())
from animation_player import play_capital_flow_animation

# 4. 指定视频输出绝对路径并执行录制
output_video_path = f"/Users/mac/Downloads/主力资金数据/{date_str}_有色金属主力资金分时动态.mp4"
play_capital_flow_animation(df=df, title_suffix=f"有色金属 ({date_str})", save_path=output_video_path)
```

---

### 第三步：验证视频与日志归档

1. 验证目标视频是否在 `/Users/mac/Downloads/主力资金数据/` 生成成功。
2. 检查输出终端是否打印 `🎉 动态视频文件保存完成！` 状态标识。
3. 检查视频编解码状态。默认压制参数已绑定 libx264 像素格式（yuv420p），完美兼容 macOS QuickTime，双击即可无卡顿流畅播放。

---

## 附加资源与参考

### 模块位置

* **核心绘图引擎**：[animation_player.py](file:///Users/mac/Downloads/Data/animation_player.py) (由 `draw.py`、`draw_sector.py` 及视频导出脚本共享)
* **独立视频生成器示例**：[generate_video_nonferrous.py](file:///Users/mac/Downloads/Data/generate_video_nonferrous.py)

### 常用命令参考

#### 1. 为任意板块极速生成 MP4 视频的 Shell 命令模板：
```bash
python3 -c "import sys, os, pandas as pd; sys.path.append('/Users/mac/Downloads/Data'); from animation_player import play_capital_flow_animation; df=pd.read_csv('/Users/mac/Downloads/Data/sector_data/[板块名称]_fund_flow.csv'); play_capital_flow_animation(df, '[板块名称]', '/Users/mac/Downloads/主力资金数据/[日期]_[板块名称]_fund_flow.mp4')"
```

#### 2. 生成 GIF 动图的命令模板（自动调用 pillow 后端驱动）：
```bash
python3 -c "import sys, os, pandas as pd; sys.path.append('/Users/mac/Downloads/Data'); from animation_player import play_capital_flow_animation; df=pd.read_csv('/Users/mac/Downloads/Data/sector_data/[板块名称]_fund_flow.csv'); play_capital_flow_animation(df, '[板块名称]', '/Users/mac/Downloads/主力资金数据/[日期]_[板块名称]_fund_flow.gif')"
```
