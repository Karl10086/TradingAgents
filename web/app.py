import streamlit as st
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime
import os
import time

# 初始化会话状态
if "state" not in st.session_state:
    st.session_state.state = {}
if "decision" not in st.session_state:
    st.session_state.decision = None

# 设置页面配置
st.set_page_config(
    page_title="StockAgent",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
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
    st.title("📊 StockAgent")
    st.divider()

    # 股票代码输入
    stock_code = st.text_input("**输入股票代码:**", "601318.SS")
    with st.expander("股票代码说明", expanded=False):
        st.markdown("""
        - **深交所**: .SZ (如: 000001.SZ)
        - **上交所**: .SS (如: 601318.SS)
        - **港交所**: .HK (如: 00700.HK)
        - **美股**: 直接输入代码 (如: AAPL)
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
        "**选择分析师类型:**",
        options=analyst_options,
        default=analyst_options,
        placeholder="请选择至少一个分析师"
    )
    selected_analysts = [analyst_mapping[cn] for cn in selected_analysts_cn]

    # 选择分析模型
    selected_llm = st.selectbox("**选择AI分析模型:**", options=["Qwen", "DeepSeek"], index=1)

    # 选择分析等级
    level_mapping = {
        "⚡ 浅层分析": 1,
        "🔍 中等分析": 2,
        "🧠 深度分析": 3
    }
    selected_level_cn = st.selectbox("**选择分析等级:**", options=list(level_mapping.keys()), index=1)
    selected_level = level_mapping[selected_level_cn]

    with st.expander("分析等级说明", expanded=False):
        st.markdown("""
        - **浅层分析**: 快速研究 (约1-2分钟)
        - **中等分析**: 折中方案 (约3-5分钟)
        - **深度分析**: 全面研究 (约5-8分钟)
        """)
    
    st.divider()
    
    # 运行分析
    if st.button("🚀 运行分析", type="primary", use_container_width=True):
        if not selected_analysts:
            st.error("请至少选择一种分析师类型！")
        else:
            st.session_state.state = {}
            st.session_state.decision = None
            
            with st.spinner("AI代理正在分析中，请稍候..."):
                try:
                    ta = initialize_trading_agents(
                        llm=selected_llm, 
                        level=selected_level, 
                        analysts=selected_analysts
                    )
                    state, decision = ta.propagate(stock_code, datetime.now().strftime("%Y-%m-%d"))
                    st.session_state.state = state
                    st.session_state.decision = decision
                    st.toast("分析完成！", icon="✅")
                except Exception as e:
                    st.error(f"分析失败: {str(e)}")

# 主内容区域
st.title("📊 StockAgent - 智能股票分析系统")
st.caption("使用多代理AI系统进行全面的股票市场分析")

# 创建标签页
market_report_tab, sentiment_report_tab, news_report_tab, fundamentals_report_tab, investment_plan_tab, final_trade_decision_tab = st.tabs([
    "📈 市场分析报告", 
    "💬 情绪分析报告", 
    "📰 新闻分析报告", 
    "💰 基本面分析报告", 
    "📝 投资计划", 
    "✅ 最终交易决定"
])

with market_report_tab:
    if "market_report" in st.session_state.state:
        st.subheader("市场趋势分析")
        st.markdown(st.session_state.state["market_report"])
    else:
        st.info("请运行分析以获取市场分析报告")
        
with sentiment_report_tab:
    if "sentiment_report" in st.session_state.state:
        st.subheader("市场情绪分析")
        st.markdown(st.session_state.state["sentiment_report"])
        
        # 添加情绪可视化
        if "sentiment_score" in st.session_state.state:
            score = st.session_state.state["sentiment_score"]
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("情绪综合评分", f"{score}/10", delta=f"{score - 5}" if score > 5 else None)
            with col2:
                st.progress(score/10, text="市场情绪指数")
    else:
        st.info("请运行分析以获取情绪分析报告")
        
with news_report_tab:
    if "news_report" in st.session_state.state:
        st.subheader("近期新闻分析")
        st.markdown(st.session_state.state["news_report"])
        
        # 添加新闻摘要
        if "key_news" in st.session_state.state:
            st.subheader("重要新闻摘要")
            for i, news in enumerate(st.session_state.state["key_news"][:5], 1):
                with st.container(border=True):
                    st.markdown(f"**{i}. {news['title']}**")
                    st.caption(f"来源: {news['source']} | 时间: {news['date']}")
                    st.write(news["summary"])
    else:
        st.info("请运行分析以获取新闻分析报告")
        
with fundamentals_report_tab:
    if "fundamentals_report" in st.session_state.state:
        st.subheader("基本面分析")
        st.markdown(st.session_state.state["fundamentals_report"])
        
        # 添加财务指标
        if "financial_metrics" in st.session_state.state:
            metrics = st.session_state.state["financial_metrics"]
            st.subheader("关键财务指标")
            cols = st.columns(4)
            cols[0].metric("市盈率(PE)", metrics.get("pe_ratio", "N/A"))
            cols[1].metric("市净率(PB)", metrics.get("pb_ratio", "N/A"))
            cols[2].metric("股息率", f"{metrics.get('dividend_yield', 'N/A')}%")
            cols[3].metric("ROE", f"{metrics.get('roe', 'N/A')}%")
    else:
        st.info("请运行分析以获取基本面分析报告")
        
with investment_plan_tab:
    if "investment_plan" in st.session_state.state:
        st.subheader("投资策略建议")
        st.markdown(st.session_state.state["investment_plan"])
        
        # 添加风险分析
        if "risk_analysis" in st.session_state.state:
            with st.expander("风险分析", expanded=True):
                st.markdown(st.session_state.state["risk_analysis"])
                
        # 添加时间规划
        if "time_horizon" in st.session_state.state:
            horizon = st.session_state.state["time_horizon"]
            st.metric("建议投资周期", horizon)
    else:
        st.info("请运行分析以获取投资计划")
        
with final_trade_decision_tab:
    if "final_trade_decision" in st.session_state.state:
        decision = st.session_state.state["final_trade_decision"]
        
        # 根据决策类型显示不同的UI
        col1, col2 = st.columns([1, 3])
        with col1:
            if "买入" in decision or "强烈推荐" in decision:
                st.success("### 🟢 买入建议")
                st.image("https://cdn-icons-png.flaticon.com/512/3524/3524380.png", width=100)
            elif "卖出" in decision or "减持" in decision:
                st.error("### 🔴 卖出建议")
                st.image("https://cdn-icons-png.flaticon.com/512/3524/3524425.png", width=100)
            elif "持有" in decision or "观望" in decision:
                st.warning("### 🟡 持有建议")
                st.image("https://cdn-icons-png.flaticon.com/512/3524/3524338.png", width=100)
            else:
                st.info("### 交易决策")
        
        with col2:
            st.markdown(decision)
            
            # 添加置信度指示器
            if "confidence_level" in st.session_state.state:
                confidence = st.session_state.state["confidence_level"]
                st.metric("决策置信度", f"{confidence}%")
                st.progress(confidence/100, text="分析置信度")
        
        # 添加决策摘要
        if "decision_summary" in st.session_state.state:
            with st.expander("决策依据摘要", expanded=True):
                st.markdown(st.session_state.state["decision_summary"])
    else:
        st.info("请运行分析以获取最终交易决定")

# 页脚
st.divider()
st.markdown('<p style="text-align:center; color:grey;">© 2025 StockAgent System v1.0 | Powered by DeepSeek</p>', unsafe_allow_html=True)
