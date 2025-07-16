import streamlit as st
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime
import os

# 初始化会话状态
if "state" not in st.session_state:
    st.session_state.state = {}
if "decision" not in st.session_state:
    st.session_state.decision = None

# 设置页面配置
st.set_page_config(
    page_title="StockAgent",
    layout="wide",
    initial_sidebar_state="auto"
)

# 初始化交易代理图（使用缓存避免重复初始化）
@st.cache_resource
def initialize_trading_agents(llm, level, analysts):
    config = DEFAULT_CONFIG.copy()
    if llm == "Qwen":
        config["llm_provider"] = "dashscope"
        config["deep_think_llm"] = "qwen-turbo"
        config["quick_think_llm"] = "qwen-plus"
        config["backend_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        os.environ["OPENAI_API_KEY"] = "sk-3442e0f2f83d4e91a7cce778c50f170c"
    elif llm == "DeepSeek":
        config["llm_provider"] = "deepseek"
        config["deep_think_llm"] = "deepseek-chat"
        config["quick_think_llm"] = "deepseek-reasoner"
        config["backend_url"] = "https://api.deepseek.com/v1"
        os.environ["OPENAI_API_KEY"] = "sk-dd4681022dfe44fa8683fd716a11c961"
    config['max_debate_rounds'] = level
    return TradingAgentsGraph(
        selected_analysts=analysts,
        config=config
    )

# 侧边栏配置
with st.sidebar:
    st.title("StockAgent")
    st.divider()

    # 股票代码输入
    stock_code = st.text_input("输入股票代码:", "601318.SS")
    with st.expander("股票代码说明"):
        st.markdown("""
        - 深交所后缀 .SZ (如: 000001.SZ)
        - 上交所后缀 .SS (如: 601318.SS)
        - 港交所后缀 .HK (如: 00700.HK)
        """)
    
    # 选择分析师类型
    analyst_mapping = {
        "📈 市场分析师": "market",
        "💬 情绪分析师": "social",
        "📰 新闻分析师": "news",
        "💰 基本面分析师": "fundamentals"
    }
    analyst_options = list(analyst_mapping.keys())
    selected_analysts_cn = st.multiselect(
        "选择分析师类型:",
        options=analyst_options,
        default=analyst_options
    )
    selected_analysts = [analyst_mapping[cn] for cn in selected_analysts_cn]

    # 选择分析模型
    selected_llm = st.selectbox("选择AI分析模型:", options=["Qwen", "DeepSeek"])

    # 选择分析等级
    level_mapping = {
        "浅层": 1,
        "中等": 2,
        "深层": 3
    }
    selected_level_cn = st.selectbox("选择分析等级:", options=list(level_mapping.keys()))
    selected_level = level_mapping[selected_level_cn]

    with st.expander("分析等级说明"):
        st.markdown("""
        - 浅层 (快速研究，少量辩论和策略讨论轮次)
        - 中等 (折中方案，适度的辩论轮次和策略讨论)
        - 深层 (全面研究，深入的辩论和策略讨论)
        """)

    # 运行分析
    if st.button("运行分析", type="primary", use_container_width=True):
        with st.spinner("AI代理正在分析中, 请稍候..."):
            try:
                ta = initialize_trading_agents(
                    llm=selected_llm, 
                    level=selected_level, 
                    analysts=selected_analysts
                )
                state, decision = ta.propagate(stock_code, datetime.now().strftime("%Y-%m-%d"))
                st.session_state.state = state
                st.session_state.decision = decision
            except Exception as e:
                st.error(e)

# 内容配置
market_report_tab, sentiment_report_tab, news_report_tab, fundamentals_report_tab, investment_plan_tab, final_trade_decision_tab = st.tabs(["📈 市场分析报告", "💬 情绪分析报告", "📰 新闻分析报告", "💰 基本面分析报告", "💰 投资计划", "💰 最终交易决定"])

with market_report_tab:
    st.write(st.session_state.state.get("market_report", ""))

with sentiment_report_tab:
    st.write(st.session_state.state.get("sentiment_report", ""))

with news_report_tab:
    st.write(st.session_state.state.get("news_report", ""))

with fundamentals_report_tab:
    st.write(st.session_state.state.get("fundamentals_report", ""))

with investment_plan_tab:
    st.write(st.session_state.state.get("investment_plan", ""))

with final_trade_decision_tab:
    st.write(st.session_state.state.get("final_trade_decision", ""))

# 页脚
st.divider()
st.caption("StockAgent System v1.0 | Powered by StockAgent team")