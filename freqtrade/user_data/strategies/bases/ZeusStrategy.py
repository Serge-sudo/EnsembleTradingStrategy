import logging
from freqtrade.strategy import CategoricalParameter, DecimalParameter

from numpy.lib import math
from freqtrade.strategy import IStrategy
from pandas import DataFrame
# --------------------------------

import pandas as pd
import ta
from ta.utils import dropna
import freqtrade.vendor.qtpylib.indicators as qtpylib
from functools import reduce
import numpy as np


class Zeus(IStrategy):

	INTERFACE_VERSION: int = 3
	# Buy hyperspace params:
	buy_params = {
		"buy_cat": "<R",
		"buy_real": 0.0128,
	}

	# Sell hyperspace params:
	sell_params = {
		"sell_cat": "=R",
		"sell_real": 0.9455,
	}

	
	def get_name(self) -> str:
		return "zeus_strategy"


	# ROI table:
	minimal_roi = {
		"0": 0.564,
		"567": 0.273,
		"2814": 0.12,
		"7675": 0
	}

	# Stoploss:
	stoploss = -0.256

	buy_real = DecimalParameter(
		0.001, 0.999, decimals=4, default=0.11908, space='buy')
	buy_cat = CategoricalParameter(
		[">R", "=R", "<R"], default='<R', space='buy')
	sell_real = DecimalParameter(
		0.001, 0.999, decimals=4, default=0.59608, space='sell')
	sell_cat = CategoricalParameter(
		[">R", "=R", "<R"], default='>R', space='sell')

	# Buy hypers
	timeframe = '4h'

	def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		# Add all ta features

		dataframe['trend_ichimoku_base'] = ta.trend.ichimoku_base_line(
			dataframe['high'],
			dataframe['low'],
			window1=9,
			window2=26,
			visual=False,
			fillna=False
		)
		KST = ta.trend.KSTIndicator(
			close=dataframe['close'],
			roc1=10,
			roc2=15,
			roc3=20,
			roc4=30,
			window1=10,
			window2=10,
			window3=10,
			window4=15,
			nsig=9,
			fillna=False
		)

		dataframe['trend_kst_diff'] = KST.kst_diff()

		# Normalization
		tib = dataframe['trend_ichimoku_base']
		dataframe['trend_ichimoku_base'] = (
			tib-tib.min())/(tib.max()-tib.min())
		tkd = dataframe['trend_kst_diff']
		dataframe['trend_kst_diff'] = (tkd-tkd.min())/(tkd.max()-tkd.min())
		return dataframe

	def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		conditions = []
		IND = 'trend_ichimoku_base'
		REAL = self.buy_real.value
		OPR = self.buy_cat.value
		DFIND = dataframe[IND]
		# print(DFIND.mean())
		if OPR == ">R":
			conditions.append(DFIND > REAL)
		elif OPR == "=R":
			conditions.append(np.isclose(DFIND, REAL))
		elif OPR == "<R":
			conditions.append(DFIND < REAL)

		if conditions:
			dataframe.loc[
				reduce(lambda x, y: x & y, conditions),
				'enter_long'] = 1

		return dataframe

	def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
		conditions = []
		IND = 'trend_kst_diff'
		REAL = self.sell_real.value
		OPR = self.sell_cat.value
		DFIND = dataframe[IND]
		# print(DFIND.mean())

		if OPR == ">R":
			conditions.append(DFIND > REAL)
		elif OPR == "=R":
			conditions.append(np.isclose(DFIND, REAL))
		elif OPR == "<R":
			conditions.append(DFIND < REAL)

		if conditions:
			dataframe.loc[
				reduce(lambda x, y: x & y, conditions),
				'exit_long'] = 1

		return dataframe