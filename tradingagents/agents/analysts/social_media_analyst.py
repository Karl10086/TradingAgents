from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_social_media_analyst(llm, toolkit):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news]
        else:
            tools = [
                toolkit.get_reddit_stock_info,
            ]

        system_message = (
            "你是一名社交媒体和公司特定新闻研究员/分析师，负责分析社交媒体帖子、近期公司新闻和公众情绪。你将获得一家公司的名称，你的目标是在查看社交媒体、分析人们每天对该公司的感受以及查看近期公司新闻后，撰写一份详细的长期报告，说明你的分析、见解和对交易者和投资者的影响。尝试查看所有可能的来源，从社交媒体到情绪再到新闻。不要简单地说趋势好坏参半，而要提供详细且细粒度的分析和见解，以帮助交易者做出决策。"
            + """ 确保在报告末尾附加一个Makrdown表格以组织报告中的关键点，使其结构清晰、易于阅读。""",
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
                    "作为参考，当前日期是{current_date}。当前我们要分析的公司是{ticker}",
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
            "sentiment_report": report,
        }

    return social_media_analyst_node
