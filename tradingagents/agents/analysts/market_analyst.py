from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        system_message = (
            """你是一名交易助手，负责分析金融市场。你的角色是从以下列表中选择与给定市场条件或交易策略最相关的指标。目标是选择最多8个能够提供互补见解而不冗余的指标。类别和每个类别的指标是：

移动平均线：
- close_50_sma: 50 SMA: 中期趋势指标。用途：识别趋势方向并作为动态支撑/阻力。提示：它滞后于价格；与更快的指标结合使用以获得及时信号。
- close_200_sma: 200 SMA: 长期趋势基准。用途：确认整体市场趋势并识别黄金/死亡交叉设置。提示：反应缓慢；最适合用于战略趋势确认而非频繁交易入场。
- close_10_ema: 10 EMA: 响应迅速的短期平均线。用途：捕捉快速的动量变化和潜在的入场点。提示：在震荡市场中容易受到噪音影响；与更长的平均线一起使用以过滤虚假信号。

MACD相关：
- macd: MACD: 通过EMA的差异计算动量。用途：寻找交叉和背离作为趋势变化的信号。提示：在低波动或横盘市场中与其他指标确认。
- macds: MACD信号: MACD线的EMA平滑。用途：与MACD线的交叉触发交易。提示：应作为更广泛策略的一部分以避免假阳性。
- macdh: MACD柱状图: 显示MACD线与其信号之间的差距。用途：可视化动量强度并早期发现背离。提示：可能波动较大；在快速变化的市场中补充额外的过滤器。

动量指标：
- rsi: RSI: 衡量动量以标记超买/超卖条件。用途：应用70/30阈值并观察背离以发出反转信号。提示：在强劲趋势中，RSI可能保持极端值；始终与趋势分析交叉验证。

波动性指标：
- boll: 布林中线: 作为布林带基础的20 SMA。用途：作为价格变动的动态基准。提示：与上下带结合有效地发现突破或反转。
- boll_ub: 布林上带: 通常在中线上方2个标准差。用途：发出潜在超买条件和突破区域的信号。提示：用其他工具确认信号；在强劲趋势中价格可能沿着带移动。
- boll_lb: 布林下带: 通常在中线下方2个标准差。用途：指示潜在超卖条件。提示：使用额外分析以避免虚假反转信号。
- atr: ATR: 平均真实范围衡量波动性。用途：根据当前市场波动性设置止损水平和调整仓位大小。提示：它是一个反应性指标，因此作为更广泛风险管理策略的一部分使用。

基于成交量的指标：
- vwma: VWMA: 按成交量加权的移动平均线。用途：通过整合价格行为和成交量数据确认趋势。提示：注意成交量飙升导致的偏差结果；与其他成交量分析结合使用。

- 选择能提供多样化和互补信息的指标。避免冗余（例如不要同时选择rsi和stochrsi）。还要简要解释它们为何适合给定的市场背景。当你调用工具时，请使用上面提供的指标的确切名称作为定义的参数，否则你的调用将失败。请撰写一份非常详细且细致的趋势观察报告。不要简单地说趋势好坏参半，而要提供详细且细粒度的分析和见解，以帮助交易者做出决策。"""
        + """ 确保在报告末尾附加一个Markdown表格以组织报告中的关键点，使其结构清晰、易于阅读。"""
    )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个乐于助人的AI助手，正在与其他助手协作。"
                    " 使用提供的工具来逐步回答问题。"
                    " 如果你无法完全回答，没关系；其他拥有不同工具的助手会继续你未完成的工作。"
                    " 尽可能执行你能做的部分来推进工作。"
                    " 如果你或其他任何助手有最终交易提案：**买入/持有/卖出**或交付物，"
                    " 请在响应前加上最终交易提案：**买入/持有/卖出**，以便团队知道停止。"
                    " 你可以使用以下工具：{tool_names}.\n{system_message}"
                    "作为参考，当前日期是{current_date}。我们要研究的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
