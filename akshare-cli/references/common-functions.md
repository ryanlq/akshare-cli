# AKShare 常用函数参考

## A股行情

| 函数 | 说明 | 参数 |
|------|------|------|
| `stock_zh_a_hist` | A股历史K线 | `--symbol`, `--period daily/weekly/monthly`, `--start-date`, `--end-date`, `--adjust qfq/hfq` |
| `stock_zh_a_spot_em` | A股实时行情（全市场） | 无 |
| `stock_zh_a_daily` | 新浪A股日线 | `--symbol sh600000`, `--start-date`, `--end-date`, `--adjust` |
| `stock_zh_a_min_em` | A股分时数据 | `--symbol`, `--period 1/5/15/30/60` |
| `stock_individual_info_em` | 个股信息 | `--symbol` |
| `stock_zh_a_new_em` | 新股列表 | 无 |

## A股特色数据

| 函数 | 说明 | 参数 |
|------|------|------|
| `stock_lhb_detail_em` | 龙虎榜明细 | `--start-date`, `--end-date` |
| `stock_dzt_detail_em` | 大宗交易 | `--start-date`, `--end-date` |
| `stock_margin_detail_sse` | 融资融券（沪） | `--start-date`, `--end-date` |
| `stock_margin_underlying_info_szse` | 融资融券标的（深） | 无 |
| `stock_board_concept_name_em` | 概念板块列表 | 无 |
| `stock_board_concept_cons_em` | 概念板块成分 | `--symbol` |
| `stock_board_industry_name_em` | 行业板块列表 | 无 |
| `stock_board_industry_cons_em` | 行业板块成分 | `--symbol` |
| `stock_hsgt_north_net_flow_in_em` | 北向资金净流入 | 无 |

## 基本面/财务

| 函数 | 说明 | 参数 |
|------|------|------|
| `stock_financial_analysis_indicator_em` | 财务分析指标 | `--symbol` |
| `stock_balance_sheet_by_report_em` | 资产负债表 | `--symbol` |
| `stock_cash_flow_statement_by_report_em` | 现金流量表 | `--symbol` |
| `stock_profit_sheet_by_report_em` | 利润表 | `--symbol` |
| `stock_a_indicator_lg` | 个股指标 | `--symbol` |
| `stock_research_report_em` | 研究报告 | `--symbol` |

## 指数

| 函数 | 说明 | 参数 |
|------|------|------|
| `index_zh_a_hist` | 指数历史行情 | `--symbol`, `--period`, `--start-date`, `--end-date` |
| `stock_board_industry_index_em` | 行业指数 | `--symbol`, `--start-date`, `--end-date` |

## 基金/ETF

| 函数 | 说明 | 参数 |
|------|------|------|
| `fund_etf_hist_em` | ETF历史行情 | `--symbol`, `--period`, `--start-date`, `--end-date`, `--adjust` |
| `fund_etf_spot_em` | ETF实时行情 | 无 |
| `fund_name_em` | 基金名称列表 | 无 |
| `fund_individual_basic_info_xq` | 基金基本信息 | `--symbol` |
| `fund_rating` | 基金评级 | 无 |

## 债券/可转债

| 函数 | 说明 | 参数 |
|------|------|------|
| `bond_zh_cov_info_ths` | 可转债信息 | 无 |
| `bond_zh_cov` | 可转债数据 | 无 |
| `bond_cb_jsl` | 集思录可转债 | 无 |
| `bond_zh_hs_cov_spot` | 可转债实时行情 | 无 |
| `bond_zh_hs_cov_daily` | 可转债历史行情 | `--symbol` |
| `bond_china_yield` | 国债收益率曲线 | 无 |

## 宏观经济

| 函数 | 说明 | 参数 |
|------|------|------|
| `macro_china_gdp` | GDP | 无 |
| `macro_china_cpi` | CPI | 无 |
| `macro_china_ppi` | PPI | 无 |
| `macro_china_ppi_yearly` | PPI年率 | 无 |
| `macro_china_pm` | PMI | 无 |
| `macro_china_shrzgm` | 社融规模 | 无 |
| `macro_china_money_supply` | 货币供应量 | 无 |
| `macro_bank_china_interest_rate` | 中国利率决议 | 无 |
| `macro_china_lpr` | LPR利率 | 无 |
| `macro_china_new_house_price` | 新房价格指数 | 无 |

## 期货

| 函数 | 说明 | 参数 |
|------|------|------|
| `futures_main_sina` | 主力合约行情 | `--symbol`, `--start-date`, `--end-date` |
| `futures_zh_spot` | 期货实时行情 | `--symbol` |
| `futures_display_main_sina` | 主力合约展示 | `--symbol` |

## 新闻

| 函数 | 说明 | 参数 |
|------|------|------|
| `news_economic_baidu` | 百度财经新闻 | 无 |
| `stock_news_em` | 个股新闻 | `--symbol` |
