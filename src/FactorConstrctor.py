import numpy as np
import pandas as pd
from tqdm import tqdm
import datetime

class FactorConstructor(object):
	"""
	This object construct factor socre according to FTSE Factor index methodology 
	details refers to https://research.ftserussell.com/products/downloads/ftse_global_factor_index_series_ground_rules.pdf
	"""
	def __init__(self, arg):
		super(FactorConstrctor, self).__init__()
		self.arg = arg
	

	@staticmethod
	def CalculateMomentum(data, strictly_follow = False, period = 255):
		"""
		Momentum is defined as the cumulative total local return, calculated over the period that starts twelve
		months prior to the effective date, and ends the Monday following the third Friday of the previous
		month. A full history is required to calculate Momentum.
		"""

		if strictly_follow: #strictly follow FTSE method, twelve months perior to Monday following the theird friday of pervious month
			print("not applicable TBD \n")
		else: #simply start twelve months perior till today
			output = np.ones(len(data)) * np.nan
			data = data.to_list()
			for i in range(period, len(data)):
				# output[i] = (data[i] / data[i-period]) -1
				output[i] = np.log(data[i]/data[i-period])
		return output

	@staticmethod
	def CalculateVolatility(data, strictly_follow = False, period = 255):
		'''
		Volatility is defined as the standard deviation of five years of weekly (Wednesday to Wednesday) total
		local returns prior to the rebalance month. A minimum of 52 weekly return observations are required
		to calculate volatility		

		data : list, price return
		period : int, period to define vol, such as 255 is Year Vol
		'''
		if strictly_follow: #strictly follow FTSE method, standard deviation of fivee years of weekly total local returns 
			print("not applicable TBD \n")
		else: #simply calculate vol of prior 52 weeks daily vol
			output = np.ones(len(data)) * np.nan
			data = data.to_list()
			for i in range(period, len(data)):
				output[i] = np.std(data[i-period:i])
		return output


	@staticmethod
	def CalculateReturn(data, is_log = True):
		'''
		data : list, price return
		'''
		output = np.ones(len(data)) * np.nan
		data = data.to_list()

		for i in range(1,len(data)):
			if is_log:
				output[i] = np.log(data[i]/data[i-1])
			else:
				output[i] = (data[i]/data[i-1]) - 1
		return output


	@staticmethod
	def CalculateYearTime(dates, period = 'Y'):
		'''
		static method to calculate how much a year have pasted till such date

		date : list, pandas.datetime

		do Week or month or quartly time refer to
		https://stackoverflow.com/questions/31996872/getting-the-date-of-the-last-day-of-this-week-month-quarter-year
		'''
		output = np.ones(len(dates)) * np.nan
		dates = dates.to_list()

		acc = 0
		for d in dates:
			if period == 'Y':
				# find first and last date of that year
				last_day_last_the_year = datetime.date(year=d.year, month=12, day=31)
				first_day_last_the_year = datetime.date(year=d.year, month=1, day=1)

				output[acc] = (d.date() - first_day_last_the_year)/(last_day_last_the_year - first_day_last_the_year) 

			elif period == 'Q':
				print("TBD")
			elif period == 'M':
				print("TBD")
			elif period == 'W':
				print("TBD")
			else:
				print("Period Term Error")								

			acc = acc + 1

		return output

	@staticmethod
	def MakeZScore(data):
		mean = np.mean(data.to_list())
		std = np.std(data.to_list())
		z_score = (data - mean)/std
		return z_score, mean, std