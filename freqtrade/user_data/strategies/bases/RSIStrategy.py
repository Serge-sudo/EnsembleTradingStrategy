from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
class RSIStrategy(IStrategy):
    # RSI parameters
    rsi_period = 14
    rsi_buy_threshold = 50
    rsi_sell_threshold = 40

    def get_name(self) -> str:
        return "rsi_strategy"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        import talib.abstract as ta
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                dataframe['rsi'] < self.rsi_buy_threshold  # RSI below buy threshold
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                dataframe['rsi'] > self.rsi_sell_threshold  # RSI above sell threshold
            ),
            'sell'] = 1
        return dataframe
