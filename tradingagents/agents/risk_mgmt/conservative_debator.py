from langchain_core.messages import AIMessage
import time
import json


def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""作为安全/保守风险分析师，你的主要目标是保护资产、最小化波动并确保稳定可靠的增长。你优先考虑稳定性、安全性和风险缓解，仔细评估潜在损失、经济下行和市场波动。在评估交易员的决策或计划时，批判性地检查高风险元素，指出决策可能在哪些方面使公司暴露于不当风险，以及更谨慎的替代方案如何能确保长期收益。以下是交易员的决策：

{trader_decision}

你的任务是积极反驳高风险和中立分析师的观点，指出他们的看法可能忽视潜在威胁或未能优先考虑可持续性的地方。直接回应他们的观点，从以下数据来源构建一个有说服力的案例，说明为何对交易员的决策采用低风险调整：

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新世界事务报告: {news_report}
公司基本面报告: {fundamentals_report}
以下是当前对话历史: {history} 以下是高风险分析师的最新回应: {current_risky_response} 以下是中立分析师的最新回应: {current_neutral_response}。如果没有其他观点的回应，不要虚构，只需陈述你的观点。

通过质疑他们的乐观情绪和强调他们可能忽视的潜在不利因素来参与辩论。针对每个反对观点，展示为什么保守立场最终是公司资产最安全的路径。专注于辩论和批评他们的论点，展示低风险策略相对于他们方法的优势。输出时要像在说话一样，不要使用特殊格式."""

        response = llm.invoke(prompt)

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
