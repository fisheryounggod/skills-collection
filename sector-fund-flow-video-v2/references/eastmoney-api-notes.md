# 东方财富资金流 API 备忘

## push2delay — 当日分钟数据
- URL: `https://push2delay.eastmoney.com/api/qt/stock/fflow/kline/get?lmt=0&klt=1&secid={secid}&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63`
- klt=1: 当日分钟级数据，lmt=0 返回全部（9:31起每分钟一条）
- **只能返回当天数据，收盘后最多到15:00**
- mainForce 单位是元，不是亿，绘图需除以 1e8

## push2his — 历史日线数据
- URL: `https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid={secid}&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58`
- 返回日线数据（每行一天），字段包含主力/小单/中单/大单/超大单净流入
- **不是分钟级，无法与当日分钟线叠加对比**

## 结论
- 今日 vs 昨日分钟线对比：**不可行**，历史分钟数据不向公众开放
- 今日 vs 昨日日线对比：**可行**，用 push2his 的日线数据
- 单板块分钟视频：直接用 push2delay + klt=1 即可
