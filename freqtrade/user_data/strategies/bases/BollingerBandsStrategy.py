from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
class BollingerBandsStrategy(IStrategy):
    # Bollinger Bands parameters
    bb_period = 20
    bb_deviation = 2.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        import talib.abstract as ta
        upperband, middleband, lowerband = ta.BBANDS(dataframe['close'], timeperiod=self.bb_period, nbdevup=self.bb_deviation, nbdevdn=self.bb_deviation, matype=0)
        dataframe['upperband'] = upperband
        dataframe['middleband'] = middleband
        dataframe['lowerband'] = lowerband
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                dataframe['close'] < dataframe['lowerband']  # Close price is below the lower BB
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                dataframe['close'] > dataframe['upperband']  # Close price is above the upper BB
            ),
            'sell'] = 1
        return dataframe
