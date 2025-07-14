from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_global_news]
        else:
            tools = [
                toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
            ]

        system_message = (
            "你是一名新闻研究员，负责分析过去一周的相关新闻和趋势。请撰写一份关于当前世界状态的全面报告，这些信息对交易和宏观经济有参考价值。查看EODHD和finnhub的新闻以获得全面信息。不要简单地说趋势好坏参半，而要提供详细且细粒度的分析和见解，以帮助交易者做出决策。"
            + """ 确保在报告末尾附加一个Makrdown表格以组织报告中的关键点，使其结构清晰、易于阅读。"""
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
                    "作为参考，当前日期是{current_date}。我们正在研究公司{ticker}",
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
            "news_report": report,
        }

    return news_analyst_node
