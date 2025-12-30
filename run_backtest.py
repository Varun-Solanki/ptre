from src.backtesting.backtest_engine import Backtester
from src.backtesting.performance import pretty_print

bt = Backtester("AAPL", start="2020-01-01")

bt.load_data()
bt.generate_signals()
bt.run_backtest()

results = bt.results()
pretty_print(results)
