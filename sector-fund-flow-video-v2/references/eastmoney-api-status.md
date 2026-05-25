# 东方财富 API 连接状态

## push2.eastmoney.com 当前状态（2026-05-19）

**状态：不稳定** — `push2.eastmoney.com` 连接被对方重置，返回 HTTP 000。

```
http.client.RemoteDisconnected: Remote end closed connection without response
```

### 已验证连通性

| 域名 | 状态 | 说明 |
|------|------|------|
| `www.eastmoney.com` | ✅ 200 | 主站正常 |
| `push2.eastmoney.com` | ❌ HTTP 000 | 分时数据 API 连接被重置 |
| `push2delay.eastmoney.com` | ⚠️ 404 | 延迟行情 |

### 替代方案探索

1. **行业板块列表 API** (`push2.eastmoney.com/api/qt/clist/get?fs=m:90+t:3`) — 同受影响，返回 000
2. **已有 CSV 数据**：`/Users/mac/Downloads/Data/sector_data/` 存有 25 个板块历史分时数据，文件完好
3. **可用板块（25个）**：存储芯片、电网设备、云计算、人工智能、半导体材料设备、消费电子、CPO、通信、半导体、电力、大科技、光伏、国产算力、先进制造、军工、商业航天、AI应用、油气资源、有色金属、医疗器械、医疗服务、医药生物、新能源汽车、白色家电、化学原料

### 待验证替代 API

- `stock.eastmoney.com/ishmarket/api/qt/clist/get` — 板块列表
- `push2his.eastmoney.com` — 历史分时数据（需验证连通性）
- `nufm.dfcfw.com/api/rt/rtquote` — 实时行情（需 secid）

### 下一步

用 `curl -v` 抓包确认是 DNS/TCP 层面被阻断还是应用层返回的连接关闭，先测试 `push2his.eastmoney.com` 连通性。
