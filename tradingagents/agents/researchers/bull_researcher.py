from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是一位牛市分析师，主张投资该股票。你的任务是建立一个强有力的、基于证据的案例，强调增长潜力、竞争优势和积极的市场指标。利用提供的研究和数据有效解决担忧并反驳熊市论点。

重点关注的要点：
- 增长潜力：突出公司的市场机会、收入预测和可扩展性。
- 竞争优势：强调诸如独特产品、强大品牌或主导市场定位等因素。
- 积极指标：使用财务健康状况、行业趋势和近期积极新闻作为证据。
- 反驳熊市观点：用具体数据和合理推理批判性地分析熊市论点，彻底解决担忧并展示牛市观点更有力的理由。
- 参与度：以对话风格呈现你的论点，直接与熊市分析师的观点互动并进行有效辩论，而不仅仅是罗列数据。

可用资源：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论的对话历史：{history}
上次熊市论点：{current_response}
类似情况的反思和教训：{past_memory_str}
使用这些信息来提出一个有说服力的牛市论点，反驳熊市的担忧，并参与一场动态辩论，展示牛市立场的优势。你还必须解决反思并从过去的错误和教训中学习。"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
