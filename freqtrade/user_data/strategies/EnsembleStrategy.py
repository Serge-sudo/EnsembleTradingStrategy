from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
from bases.MAStrategy import MAStrategy
from bases.RSIStrategy import RSIStrategy
from bases.SMAOffset import SMAOffset
from bases.BollingerBandsStrategy import BollingerBandsStrategy
from bases.SMAOffsetProtectOptV0 import SMAOffsetProtectOptV0
from bases.CombinedBinHAndClucV8 import CombinedBinHAndClucV8
from catboost import CatBoostClassifier, Pool, sum_models

class EnsembleStrategy(IStrategy):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.base_strategies = [
			SMAOffset(*args, **kwargs),
			# MAStrategy(*args, **kwargs),
			# RSIStrategy(*args, **kwargs),
			# BollingerBandsStrategy(*args, **kwargs),
			SMAOffsetProtectOptV0(*args, **kwargs),
			# CombinedBinHAndClucV8(*args, **kwargs)
		]

	def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		for strategy in self.base_strategies:
			dataframe = strategy.populate_indicators(dataframe, metadata)
		return dataframe

	def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		dataframe.loc[:,'buy'] = 0
		populated_dataframe = dataframe
		populated_dataframe["pair"] = metadata.get("pair")
		for strategy in self.base_strategies:
			strategy_name = strategy.get_name()
			strategy_indicators = strategy.populate_indicators(dataframe, metadata)
			dataframe[f"strat_buy_signal_{strategy_name}"] = strategy.populate_buy_trend(
				strategy_indicators, metadata
			)["buy"]
			y = dataframe[f"strat_buy_signal_{strategy_name}"]
			x = populated_dataframe[[col for col in populated_dataframe.columns if "date" not in col ]].fillna(-1)
			# remove duplicated columns
			x = x.loc[:, ~x.columns.duplicated()]
			cat_features = [i for i in x.columns if x.dtypes[i] == "object"]

			dataset = Pool(data=x, label=y, cat_features=cat_features)
			baseline_model = CatBoostClassifier(iterations=15)
			try:
				baseline_model = baseline_model.load_model("/home/Serge/workspace/assemblyTradingStrategy/freqtrade/user_data/buy_model")
			except:
				# first run
				pass

			model = CatBoostClassifier(iterations=15)
			try:
				model.fit(dataset, use_best_model=True, eval_set=dataset)
			except:
				#  target contains only one value
				pass
			final_model = sum_models(
				[baseline_model, model], weights=None, ctr_merge_policy="IntersectingCountersAverage"
			)
			final_model.save_model("/home/Serge/workspace/assemblyTradingStrategy/freqtrade/user_data/buy_model")

		preds = final_model.predict(dataset, prediction_type="Probability")
		dataframe["buy_proba"] = preds[:, 1]

		dataframe["buy"] = dataframe['buy_proba'].apply(lambda x: 1 if x > 0.7 else 0)

		return dataframe

	def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		dataframe.loc[:,'sell'] = 0
		populated_dataframe = dataframe
		populated_dataframe["pair"] = metadata.get("pair")
		for strategy in self.base_strategies:
			strategy_name = strategy.get_name()
			strategy_indicators = strategy.populate_indicators(dataframe, metadata)
			dataframe[f"strat_sell_signal_{strategy_name}"] = strategy.populate_sell_trend(
				strategy_indicators, metadata
			)["sell"]
			y = dataframe[f"strat_sell_signal_{strategy_name}"]
			x = populated_dataframe[[col for col in populated_dataframe.columns if "date" not in col]].fillna(-1)
			# remove duplicated columns
			x = x.loc[:, ~x.columns.duplicated()]
			cat_features = [i for i in x.columns if x.dtypes[i] == "object"]
			dataset = Pool(data=x, label=y, cat_features=cat_features)
			baseline_model = CatBoostClassifier(iterations=15)
			try:
				baseline_model = baseline_model.load_model("/home/Serge/workspace/assemblyTradingStrategy/freqtrade/user_data/sell_model")
			except:
				# first run
				pass

			model = CatBoostClassifier(iterations=15)
			try:
				model.fit(dataset, use_best_model=True, eval_set=dataset)
			except:
				#  target contains only one value
				pass
			final_model = sum_models(
				[baseline_model, model], weights=None, ctr_merge_policy="IntersectingCountersAverage"
			)
			final_model.save_model("/home/Serge/workspace/assemblyTradingStrategy/freqtrade/user_data/sell_model")

		preds = final_model.predict(dataset, prediction_type="Probability")
		dataframe["sell_proba"] = preds[:, 1]

		dataframe["sell"] = dataframe['sell_proba'].apply(lambda x: 1 if x > 0.7 else 0)

		return dataframe
