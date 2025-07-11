import time
import json


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""作为中立风险分析师，你的角色是提供平衡的视角，权衡交易员决策或计划的潜在好处和风险。你优先考虑全面方法，评估利弊的同时考虑更广泛的市场趋势、潜在经济变化和多元化策略。以下是交易员的决策：

{trader_decision}

你的任务是挑战高风险和安全分析师，指出每个观点可能在哪些方面过于乐观或过于谨慎。使用以下数据来源的见解支持对交易员决策的适度、可持续策略调整：

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新世界事务报告: {news_report}
公司基本面报告: {fundamentals_report}
以下是当前对话历史: {history} 以下是高风险分析师的最新回应: {current_risky_response} 以下是安全分析师的最新回应: {current_safe_response}。如果没有其他观点的回应，不要虚构，只需陈述你的观点。

通过批判性地分析双方，积极应对高风险和保守论点中的弱点，倡导更平衡的方法。挑战他们的每个观点，说明为什么适度风险策略可能提供两全其美的方式，提供增长潜力同时防止极端波动。专注于辩论而非简单呈现数据，旨在展示平衡观点能带来最可靠的结果。输出时要像在说话一样，不要使用特殊格式."""

        response = llm.invoke(prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
