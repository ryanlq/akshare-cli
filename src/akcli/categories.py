"""Category mapping and tiering for akshare functions.

Tier 1: 核心 - A股、基金、指数、宏观经济
Tier 2: 常用 - 债券、期货、利率、新闻、期权
Tier 3: 专业 - 港股、美股、外汇、可转债
Tier 4: 小众 - 能源、现货、REITs、汽车、协会数据...
"""

# Category metadata: (label, tier, description)
CATEGORY_META = {
    # === Tier 1: 核心 ===
    "stock":            ("股票",     1, "A股个股行情、基本面、财务报表"),
    "stock_zh":         ("A股",      1, "A股行情数据"),
    "stock_feature":    ("A股特色",  1, "龙虎榜、大宗交易、融资融券"),
    "stock_fundamental":("基本面",   1, "财务报表、盈利预测、估值指标"),
    "fund":             ("基金",     1, "公募基金、基金净值、基金排行"),
    "fund_etf":         ("ETF",      1, "ETF行情、持仓、规模"),
    "index":            ("指数",     1, "上证、深证、中证等指数行情"),
    "macro":            ("宏观",     1, "GDP、CPI、PMI、社融等宏观经济数据"),

    # === Tier 2: 常用 ===
    "bond":             ("债券",     2, "国债、企业债、可转债行情与信息"),
    "futures":          ("期货",     2, "商品期货、金融期货行情"),
    "option":           ("期权",     2, "ETF期权、商品期权行情"),
    "rate":             ("利率",     2, "Shibor、LPR、国债收益率"),
    "interest":         ("利率",     2, "Shibor、LPR、国债收益率"),
    "news":             ("新闻",     2, "财经新闻、市场舆情"),

    # === Tier 3: 专业 ===
    "stock_hk":         ("港股",     3, "港股行情、港股通数据"),
    "stock_us":         ("美股",     3, "美股行情、中概股"),
    "forex":            ("外汇",     3, "人民币汇率、主要货币对"),
    "fx":               ("外汇衍生", 3, "外汇期权、远期"),
    "economic":         ("经济",     3, "专项经济数据"),
    "bank":             ("银行",     3, "银行理财、存款利率"),
    "currency":         ("货币",     3, "货币供应、信贷数据"),
    "fund_feature":     ("基金特色", 3, "基金分析、评级"),

    # === Tier 4: 小众 ===
    "spot":             ("现货",     4, "大宗商品现货价格"),
    "energy":           ("能源",     4, "原油、天然气、煤炭价格"),
    "crypto":           ("加密货币", 4, "比特币、以太坊行情"),
    "reits":            ("REITs",    4, "公募REITs数据"),
    "hf":               ("港美股指", 4, "恒生指数、纳斯达克"),
    "stock_stock":      ("股票扩展", 4, "A股扩展数据"),
    "stock_em":         ("东财股票", 4, "东方财富特色数据"),
    "nlp":              ("NLP",      4, "自然语言处理数据"),
    "pro":              ("Pro",      4, "AKShare Pro 接口"),

    # Tier 5: 杂项
    "air":              ("空气质量", 5, "城市空气质量数据"),
    "movie":            ("电影",     5, "电影票房数据"),
    "game":             ("游戏",     5, "游戏热度排行"),
}

# Prefix matching order (longest first to avoid ambiguity)
CATEGORY_PREFIXES = [
    "stock_fundamental",
    "stock_feature",
    "stock_stock",
    "stock_zh",
    "stock_hk",
    "stock_us",
    "stock_em",
    "fund_etf",
    "fund_feature",
    "interest",
    "stock",
    "fund",
    "bond",
    "futures",
    "option",
    "index",
    "forex",
    "fx",
    "macro",
    "economic",
    "news",
    "spot",
    "energy",
    "crypto",
    "reits",
    "bank",
    "rate",
    "currency",
    "hf",
    "nlp",
    "pro",
    "game",
    "air",
    "movie",
]

# Scene-based groupings for `ak list --scene`
SCENES = {
    "选股": {
        "desc": "A股选股相关：行情、基本面、龙虎榜、技术指标",
        "categories": ["stock", "stock_zh", "stock_feature", "stock_fundamental"],
    },
    "指数投资": {
        "desc": "指数行情、ETF、基金数据",
        "categories": ["index", "fund_etf", "fund"],
    },
    "宏观研究": {
        "desc": "宏观经济、利率、货币、银行",
        "categories": ["macro", "rate", "interest", "currency", "bank", "economic"],
    },
    "债券固收": {
        "desc": "债券行情、可转债、利率数据",
        "categories": ["bond", "rate", "interest"],
    },
    "期货衍生品": {
        "desc": "期货、期权行情",
        "categories": ["futures", "option", "spot", "energy"],
    },
    "海外市场": {
        "desc": "港股、美股、外汇",
        "categories": ["stock_hk", "stock_us", "forex", "fx", "hf"],
    },
}


def get_category(func_name: str) -> str:
    """Derive category from function name by matching longest prefix."""
    for prefix in CATEGORY_PREFIXES:
        if func_name.startswith(prefix + "_") or func_name == prefix:
            return prefix
    return "other"


def get_category_label(category: str) -> str:
    meta = CATEGORY_META.get(category)
    return meta[0] if meta else category


def get_category_tier(category: str) -> int:
    meta = CATEGORY_META.get(category)
    return meta[1] if meta else 5


def get_category_desc(category: str) -> str:
    meta = CATEGORY_META.get(category)
    return meta[2] if meta else ""


def get_max_tier(show_all: bool = False) -> int:
    """Default tier cutoff: show tier 1+2, with --all show everything."""
    return 5 if show_all else 2


def should_show_category(category: str, max_tier: int) -> bool:
    tier = get_category_tier(category)
    return tier <= max_tier
