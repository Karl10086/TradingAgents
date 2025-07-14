from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_fundamentals]
        else:
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
            ]

        system_message = (
            "你是一名研究员，负责分析公司过去一周的基本面信息。请撰写一份关于公司基本面信息的全面报告，包括财务文件、公司简介、基本公司财务、公司财务历史、内部人情绪和内部人交易，以全面了解公司的基本面信息，为交易者提供信息。确保包含尽可能多的细节。不要简单地说趋势好坏参半，而要提供详细且细粒度的分析和见解，以帮助交易者做出决策。"
            + " 确保在报告末尾附加一个Markdown表格以组织报告中的关键点，使其结构清晰、易于阅读。",
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
