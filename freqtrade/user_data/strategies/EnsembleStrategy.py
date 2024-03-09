from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
from bases.MAStrategy import MAStrategy 
from bases.RSIStrategy import RSIStrategy
from bases.BollingerBandsStrategy import BollingerBandsStrategy


class EnsembleStrategy(IStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_strategies = [
            MAStrategy(*args, **kwargs),
            RSIStrategy(*args, **kwargs),
            BollingerBandsStrategy(*args, **kwargs),
        ]
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for strategy in self.base_strategies:
            dataframe = strategy.populate_indicators(dataframe, metadata)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[:,'buy'] = 0
        votes = sum(strategy.populate_buy_trend(dataframe.copy(), metadata)['buy'] for strategy in self.base_strategies)
        majority_vote = votes > (len(self.base_strategies) / 2)
        dataframe.loc[majority_vote, 'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[:,'sell'] = 0
        votes = sum(strategy.populate_sell_trend(dataframe.copy(), metadata)['sell'] for strategy in self.base_strategies)
        majority_vote = votes > (len(self.base_strategies) / 2)
        dataframe.loc[majority_vote, 'sell'] = 1
        return dataframe

