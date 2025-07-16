from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "deepseek"
config["deep_think_llm"] = "deepseek-chat"
config["quick_think_llm"] = "deepseek-reasoner"
config["backend_url"] = "https://api.deepseek.com/v1"

# Initialize with custom config
ta = TradingAgentsGraph(
    selected_analysts=["market", "social", "news", "fundamentals"],
    debug=True, 
    config=config
)

# forward propagate
_, decision = ta.propagate("601318.SS", datetime.now().strftime("%Y-%m-%d"))
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
