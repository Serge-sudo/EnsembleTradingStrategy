from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class MAStrategy(IStrategy):
    """
    This is a simple Moving Average Crossover strategy.

    It buys when the fast moving average crosses above the slow moving average and
    sells when the fast moving average crosses below the slow moving average.
    """

    # Define the two moving average windows
    fast_ma = 3
    slow_ma = 10

    # Minimal ROI designed for the strategy.
    minimal_roi = {
        "0": 0.01  # 1% ROI
    }

    # Optimal stop loss for the strategy
    stoploss = -0.10  # -10% stop loss

    # Trailing stop loss
    trailing_stop = True
    trailing_stop_positive = 0.01  # 1%
    trailing_stop_positive_offset = 0.02  # 2%
    trailing_only_offset_is_reached = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add your needed indicators here - this method prepares the DataFrame for the strategy.
        """
        # Calculate moving averages
        dataframe['fast_ma'] = ta.SMA(dataframe, timeperiod=self.fast_ma)
        dataframe['slow_ma'] = ta.SMA(dataframe, timeperiod=self.slow_ma)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on the indicators, define your buy strategy.
        """
        dataframe.loc[
            (
                (dataframe['fast_ma'] > dataframe['slow_ma'])  # Fast MA is above Slow MA
                & (dataframe['fast_ma'].shift(1) <= dataframe['slow_ma'].shift(1))  # And was below in the previous period
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on the indicators, define your sell strategy.
        """
        dataframe.loc[
            (
                (dataframe['fast_ma'] < dataframe['slow_ma'])  # Fast MA is below Slow MA
                & (dataframe['fast_ma'].shift(1) >= dataframe['slow_ma'].shift(1))  # And was above in the previous period
            ),
            'sell'] = 1
        return dataframe
