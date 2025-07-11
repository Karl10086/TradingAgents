import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"基于分析师团队的全面分析，这里是为{company_name}量身定制的投资计划。该计划整合了当前技术市场趋势、宏观经济指标和社交媒体情绪的分析结果。请将此计划作为评估您下一个交易决策的基础。\n\n建议投资计划: {investment_plan}\n\n利用这些洞察做出明智的战略决策。",
        }

        messages = [
            {
                "role": "system",
                "content": f"""你是一名交易代理，正在分析市场数据以做出投资决策。根据你的分析，提供具体的买入、卖出或持有建议。用'最终交易提案：**买入/持有/卖出**'结束你的响应以确认你的建议。不要忘记利用过去决策的教训来从错误中学习。以下是你在类似交易情况中的一些反思和学到的教训：{past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
