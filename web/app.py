import streamlit as st
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime
import os

# 初始化会话状态
if 'analysis_in_progress' not in st.session_state:
    st.session_state.analysis_in_progress = False
if "state" not in st.session_state:
    st.session_state.state = {}
if "decision" not in st.session_state:
    st.session_state.decision = {}

# 设置页面配置
st.set_page_config(
    page_title="StockAgent",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# 初始化tradingagents（使用缓存避免重复初始化）
@st.cache_resource
def init_tradingagents(llm, level, analysts):
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

# 运行tradingagents（使用缓存避免重复初始化）
def run_tradingagents(llm, level, analysts, stock_code, trade_date):
    ta = init_tradingagents(
        llm=llm,
        level=level,
        analysts=analysts
    )
    ta.ticker = stock_code
    init_agent_state = ta.propagator.create_initial_state(
        stock_code, trade_date
    )
    args = ta.propagator.get_graph_args()
    trace = []
    with st.status("AI代理正在分析中，请稍候...", expanded=True) as status:
        team_display_names = {
            "Market Analyst": "市场分析师",
            "Social Analyst": "情绪分析师",
            "News Analyst": "新闻分析师",
            "Fundamentals Analyst": "基本面分析师",
            "Bull Researcher": "看涨研究员",
            "Bear Researcher": "看跌研究员",
            "Research Manager": "研究经理",
            "Trader": "交易员",
            "Risky Analyst": "风险分析师",
            "Neutral Analyst": "中性分析师",
            "Safe Analyst": "保守分析师",
            "Portfolio Manager": "投资组合经理"
        }
        teams_status_placeholders = {}
        for key, value in team_display_names.items():
            teams_status_placeholders[key] = st.empty()
            teams_status_placeholders[key].text(f"⚪ **{value}:** 待处理")
        teams_status_placeholders["Market Analyst"].text(f"🟢 **{team_display_names["Market Analyst"]}:** 进行中")
        for chunk in ta.graph.stream(init_agent_state, **args):
            if len(chunk["messages"]) > 0:
                # Analyst Team Reports
                if "market_report" in chunk and chunk["market_report"]:
                    teams_status_placeholders["Market Analyst"].text(f"✅ **{team_display_names['Market Analyst']}:** 已完成")
                    if "social" in analysts:
                        teams_status_placeholders["Social Analyst"].text(f"🟢 **{team_display_names['Social Analyst']}:** 进行中")
                if "sentiment_report" in chunk and chunk["sentiment_report"]:
                    teams_status_placeholders["Social Analyst"].text(f"✅ **{team_display_names['Social Analyst']}:** 已完成")
                    if "news" in analysts:
                        teams_status_placeholders["News Analyst"].text(f"🟢 **{team_display_names['News Analyst']}:** 进行中")
                if "news_report" in chunk and chunk["news_report"]:
                    teams_status_placeholders["News Analyst"].text(f"✅ **{team_display_names['News Analyst']}:** 已完成")
                    if "fundamentals" in analysts:
                        teams_status_placeholders["Fundamentals Analyst"].text(f"🟢 **{team_display_names['Fundamentals Analyst']}:** 进行中")
                if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                    teams_status_placeholders["Fundamentals Analyst"].text(f"✅ **{team_display_names['Fundamentals Analyst']}:** 已完成")
                    # Once fundamentals are done, research and trading teams start
                    for team_key in ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]:
                        teams_status_placeholders[team_key].text(f"🟢 **{team_display_names[team_key]}:** 进行中")

                # Research Team - Handle Investment Debate State
                if (
                    "investment_debate_state" in chunk
                    and chunk["investment_debate_state"]
                ):
                    debate_state = chunk["investment_debate_state"]
                    if (
                        "judge_decision" in debate_state
                        and debate_state["judge_decision"]
                    ):
                        for team_key in ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]:
                            teams_status_placeholders[team_key].text(f"✅ **{team_display_names[team_key]}:** 已完成")
                        teams_status_placeholders["Risky Analyst"].text(f"🟢 **{team_display_names['Risky Analyst']}:** 进行中")

                # Risk Management Team - Handle Risk Debate State
                if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                    risk_state = chunk["risk_debate_state"]
                    if (
                        "current_safe_response" in risk_state
                        and risk_state["current_safe_response"]
                    ):
                        teams_status_placeholders["Safe Analyst"].text(f"🟢 **{team_display_names['Safe Analyst']}:** 进行中")
                    if (
                        "current_neutral_response" in risk_state
                        and risk_state["current_neutral_response"]
                    ):
                        teams_status_placeholders["Neutral Analyst"].text(f"🟢 **{team_display_names['Neutral Analyst']}:** 进行中")
                    if "judge_decision" in risk_state and risk_state["judge_decision"]:
                        # All risk management and portfolio manager teams complete after judge decision
                        teams_status_placeholders["Risky Analyst"].text(f"✅ **{team_display_names['Risky Analyst']}:** 已完成")
                        teams_status_placeholders["Neutral Analyst"].text(f"✅ **{team_display_names['Neutral Analyst']}:** 已完成")
                        teams_status_placeholders["Safe Analyst"].text(f"✅ **{team_display_names['Safe Analyst']}:** 已完成")
                        teams_status_placeholders["Portfolio Manager"].text(f"✅ **{team_display_names['Portfolio Manager']}:** 已完成")
            trace.append(chunk)
        status.update(label="AI代理已完成分析", expanded=False)
    final_state = trace[-1]
    ta.curr_state = final_state
    return final_state, ta.process_signal(final_state["final_trade_decision"])

# 侧边栏配置
with st.sidebar:
    st.title("📊 StockAgent")
    st.divider()

    # 股票代码输入
    stock_code = st.text_input(
        "**输入股票代码:**", 
        value="601318.SS",
        disabled=st.session_state.analysis_in_progress
    )
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
        disabled=st.session_state.analysis_in_progress
    )
    selected_analysts = [analyst_mapping[cn] for cn in selected_analysts_cn]

    # 选择分析模型
    selected_llm = st.selectbox(
        "**选择AI分析模型:**", 
        options=["Qwen", "DeepSeek"], 
        index=0,
        disabled=st.session_state.analysis_in_progress
    )

    # 选择分析等级
    level_mapping = {
        "⚡ 浅层分析": 1,
        "🔍 中等分析": 3,
        "🧠 深度分析": 5
    }
    selected_level_cn = st.selectbox(
        "**选择分析等级:**", 
        options=list(level_mapping.keys()), 
        index=0,
        disabled=st.session_state.analysis_in_progress
    )
    selected_level = level_mapping[selected_level_cn]
    with st.expander("分析等级说明", expanded=False):
        st.markdown("""
        - **浅层分析**: 快速研究 (约1-2分钟)
        - **中等分析**: 折中方案 (约3-5分钟)
        - **深度分析**: 全面研究 (约5-8分钟)
        """)
    st.divider()
    
    # 运行分析
    def on_click():
        st.session_state.analysis_in_progress = True
    st.button(
        "🚀 运行分析",
        on_click=on_click,
        type="primary",
        use_container_width=True,
        disabled=st.session_state.analysis_in_progress
    )
    if st.session_state.analysis_in_progress:
        if not selected_analysts:
            st.error("请至少选择一种分析师类型！")
        else:
            st.session_state.state = {}
            st.session_state.decision = None
            
            try:
                state, decision = run_tradingagents(
                    llm=selected_llm, 
                    level=selected_level, 
                    analysts=selected_analysts,
                    stock_code=stock_code,
                    trade_date=datetime.now().strftime("%Y-%m-%d")
                )
                st.session_state.state = state
                st.session_state.decision = decision
                st.toast("分析完成！", icon="✅")
            except Exception as e:
                st.error(f"分析失败: {str(e)}")
        st.session_state.analysis_in_progress = False
        st.rerun()
        
# 主内容区域
st.title("📊 StockAgent - 智能股票分析系统")
st.caption("使用多代理AI系统进行全面的股票市场分析")

# 创建标签页
market_report_tab, sentiment_report_tab, news_report_tab, fundamentals_report_tab, final_trade_decision_tab = st.tabs([
    "📈 市场分析报告", 
    "💬 情绪分析报告", 
    "📰 新闻分析报告", 
    "💰 基本面分析报告", 
    "✅ 最终交易决定"
])

with market_report_tab:
    if "market_report" in st.session_state.state:
        st.markdown(st.session_state.state["market_report"])
    else:
        st.info("请运行分析以获取市场分析报告")
        
with sentiment_report_tab:
    if "sentiment_report" in st.session_state.state:
        st.markdown(st.session_state.state["sentiment_report"])
    else:
        st.info("请运行分析以获取情绪分析报告")
        
with news_report_tab:
    if "news_report" in st.session_state.state:
        st.markdown(st.session_state.state["news_report"])
    else:
        st.info("请运行分析以获取新闻分析报告")
        
with fundamentals_report_tab:
    if "fundamentals_report" in st.session_state.state:
        st.markdown(st.session_state.state["fundamentals_report"])
    else:
        st.info("请运行分析以获取基本面分析报告")
        
with final_trade_decision_tab:
    if "final_trade_decision" in st.session_state.state:
        st.markdown(st.session_state.state["final_trade_decision"])
    else:
        st.info("请运行分析以获取最终交易决定")

# 页脚
st.divider()
st.markdown('<p style="text-align:center; color:grey;">© 2025 StockAgent System v1.0 | Powered by DeepSeek</p>', unsafe_allow_html=True)
