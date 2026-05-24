---
name: akshare-cli
description: >
  AKShare 中国金融数据 CLI 工具。通过命令行获取 A股、基金、债券、期货、宏观经济等 1092+ 金融数据函数。
  当用户需要以下操作时使用此 skill：
  (1) 查询中国金融数据（股票行情、基金净值、债券、指数、宏观经济等）
  (2) 获取 A 股实时行情、历史K线、财务报表
  (3) 查询基金、ETF、可转债数据
  (4) 获取宏观经济指标（GDP、CPI、PMI、利率等）
  (5) 用户提到"股价"、"行情"、"财报"、"基金"、"债券"、"宏观"、"指数"等金融关键词
  (6) 用户要求获取东方财富、新浪财经等数据源的金融数据
---

# AKShare CLI — 中国金融数据工具

## 核心工作流

```
发现函数 → 查看参数 → 执行查询
```

所有命令均支持 `--format json` 输出结构化 JSON，便于解析。

## 1. 发现函数

```bash
ak list --format json                    # 类别概览（tier 1-2 核心+常用）
ak list --all --format json              # 全部类别
ak list --category stock --format json   # 某类所有函数
ak list --search KEYWORD --format json   # 关键词搜索（支持中文）
ak list --scene SCENE --format json      # 场景筛选
```

可用场景：`选股` `指数投资` `宏观研究` `债券固收` `期货衍生品` `海外市场`

## 2. 查看函数参数

```bash
ak info FUNC --format json
```

关键字段解读：
- `has_default: false` → 必填参数
- `choices: [...]` → 枚举值，只能从中选择
- `default` → 不传时的默认值

## 3. 执行函数

```bash
ak FUNC --param1 VAL1 --param2 VAL2 --format json --limit N
```

参数名用 `--` 前缀，下划线改连字符（`start_date` → `--start-date`）。

### 全局选项

| 选项 | 作用 |
|------|------|
| `--format json\|csv\|table\|excel` | 输出格式（默认 table） |
| `--limit N` | 限制返回行数 |
| `--columns C1,C2` | 选择特定列 |
| `--output FILE` | 输出到文件 |

## 常用函数速查

详细函数列表参见 [references/common-functions.md](references/common-functions.md)。

| 场景 | 函数 | 关键参数 |
|------|------|----------|
| A股日K线 | `stock_zh_a_hist` | `--symbol 000001 --period daily --start-date 20240101` |
| A股实时行情 | `stock_zh_a_spot_em` | 无参数 |
| 指数行情 | `index_zh_a_hist` | `--symbol 000001 --period daily` |
| 基金净值 | `fund_etf_hist_em` | `--symbol 159915 --period daily` |
| 可转债列表 | `bond_zh_cov_info_ths` | 无参数 |
| 宏观GDP | `macro_china_gdp` | 无参数 |
| 龙虎榜 | `stock_lhb_detail_em` | `--start-date 20240101 --end-date 20240110` |
| 沪深港通 | `stock_hsgt_north_net_flow_in_em` | 无参数 |

## 注意事项

- 日期格式：`YYYYMMDD`（如 `20240101`）
- 股票代码：纯数字（如 `000001`），大多数函数不需要 `sh`/`sz` 前缀
- 网络依赖：函数需访问数据源 API，可能因网络或限流失败
- 始终加 `--limit` 控制返回量，避免响应过大
