import streamlit as st
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime
import os

# 设置页面配置
st.set_page_config(
    page_title="StockAgent",
    layout="wide",
    initial_sidebar_state="auto"
)

# 初始化交易代理图（使用缓存避免重复初始化）
@st.cache_resource
def initialize_trading_agents(analysts):
    config = DEFAULT_CONFIG.copy()
    if selected_llm == "Qwen":
        config["llm_provider"] = "dashscope"
        config["deep_think_llm"] = "qwen-turbo"
        config["quick_think_llm"] = "qwen-plus"
        config["backend_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        os.environ["OPENAI_API_KEY"] = "sk-3442e0f2f83d4e91a7cce778c50f170c"
    elif selected_llm == "DeepSeek":
        config["llm_provider"] = "deepseek"
        config["deep_think_llm"] = "deepseek-chat"
        config["quick_think_llm"] = "deepseek-reasoner"
        config["backend_url"] = "https://api.deepseek.com/v1"
        os.environ["OPENAI_API_KEY"] = "sk-dd4681022dfe44fa8683fd716a11c961"
    if selected_level == "浅层":
        config['max_debate_rounds'] = 1
    elif selected_level == "中层":
        config['max_debate_rounds'] = 3
    elif selected_level == "深层":
        config['max_debate_rounds'] = 5
    return TradingAgentsGraph(
        selected_analysts=analysts,
        config=config
    )

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置参数")

    # 股票代码输入
    stock_code = st.text_input("输入股票代码:", "601318.SS")
    with st.expander("股票代码说明"):
        st.markdown("""
        - 深交所后缀 .SZ (如: 000001.SZ)
        - 上交所后缀 .SS (如: 601318.SS)
        - 港交所后缀 .HK (如: 00700.HK)
        """)
    
    # 选择分析师类型
    analyst_options = ["📈市场分析师", "💬情绪分析师", "📰新闻分析师", "💰基本面分析师"]
    selected_analysts = st.multiselect(
        "选择分析师类型:",
        options=analyst_options,
        default=analyst_options
    )

    # 选择分析模型
    selected_llm = st.selectbox("选择AI分析模型:", options=["Qwen", "DeepSeek"])

    # 选择分析等级
    selected_level = st.selectbox("选择分析等级:", options=["浅层", "中等", "深层"])
    with st.expander("分析等级说明"):
        st.markdown("""
        - 浅层 (快速研究，少量辩论和策略讨论轮次)
        - 中等 (折中方案，适度的辩论轮次和策略讨论)
        - 深层 (全面研究，深入的辩论和策略讨论)
        """)

    # 运行分析
    if st.button("运行分析", type="primary", use_container_width=True):
        with st.spinner("AI代理正在分析中，请稍候..."):
            try:
                ta = initialize_trading_agents(selected_analysts)
                _, decision = ta.propagate(stock_code, datetime.now().strftime("%Y-%m-%d"))
                st.write(decision)

                st.session_state.decision = decision
            except Exception as e:
                st.error(f"分析过程中出错: {str(e)}")
