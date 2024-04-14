from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy
from pandas import DataFrame


import talib.abstract as ta
from functools import reduce
import freqtrade.vendor.qtpylib.indicators as qtpylib


class Diamond(IStrategy):
	INTERFACE_VERSION: int = 3

	# Buy hyperspace params:
	buy_params = {
		"buy_fast_key": "high",
		"buy_horizontal_push": 7,
		"buy_slow_key": "volume",
		"buy_vertical_push": 0.942,
	}

	# Sell hyperspace params:
	sell_params = {
		"sell_fast_key": "high",
		"sell_horizontal_push": 10,
		"sell_slow_key": "low",
		"sell_vertical_push": 1.184,
	}

	# ROI table:
	minimal_roi = {
		"0": 0.242,
		"13": 0.044,
		"51": 0.02,
		"170": 0
	}

	# Stoploss:
	stoploss = -0.271

	
	def get_name(self) -> str:
		return "dimond_strategy"


	# Trailing stop:
	trailing_stop = True
	trailing_stop_positive = 0.011
	trailing_stop_positive_offset = 0.054
	trailing_only_offset_is_reached = False
	# timeframe
	timeframe = '5m'
	# #################### END OF RESULT PLACE ####################

	buy_vertical_push = DecimalParameter(0.5, 1.5, decimals=3, default=1, space='buy')
	buy_horizontal_push = IntParameter(0, 10, default=0, space='buy')
	buy_fast_key = CategoricalParameter(['open', 'high', 'low', 'close', 'volume',
										 ], default='ma_fast', space='buy')
	buy_slow_key = CategoricalParameter(['open', 'high', 'low', 'close', 'volume',
										 #  'ma_fast', 'ma_slow', {...}
										 ], default='ma_slow', space='buy')

	sell_vertical_push = DecimalParameter(0.5, 1.5, decimals=3,  default=1, space='sell')
	sell_horizontal_push = IntParameter(0, 10, default=0, space='sell')
	sell_fast_key = CategoricalParameter(['open', 'high', 'low', 'close', 'volume',
										  #  'ma_fast', 'ma_slow', {...}
										  ], default='ma_fast', space='sell')
	sell_slow_key = CategoricalParameter(['open', 'high', 'low', 'close', 'volume',
										  #  'ma_fast', 'ma_slow', {...}
										  ], default='ma_slow', space='sell')

	def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		return dataframe

	def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		conditions = []
		conditions.append(
			qtpylib.crossed_above
			(
				dataframe[self.buy_fast_key.value].shift(self.buy_horizontal_push.value),
				dataframe[self.buy_slow_key.value] * self.buy_vertical_push.value
			)
		)

		if conditions:
			dataframe.loc[
				reduce(lambda x, y: x & y, conditions),
				'enter_long']=1

		return dataframe

	def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		conditions = []
		conditions.append(
			qtpylib.crossed_below
			(
				dataframe[self.sell_fast_key.value].shift(self.sell_horizontal_push.value),
				dataframe[self.sell_slow_key.value] * self.sell_vertical_push.value
			)
		)
		if conditions:
			dataframe.loc[
				reduce(lambda x, y: x & y, conditions),
				'exit_long']=1
		return dataframe