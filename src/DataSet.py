import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from openbb_terminal.sdk import widgets
from openbb_terminal.sdk import openbb
from openbb_terminal.helper_classes import TerminalStyle
from openbb_terminal.core.config.paths import REPOSITORY_DIRECTORY

from FactorConstrctor import FactorConstructor
from SignalMarker import SignalMarker

import os
import sys
import logging
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
import pickle

class DataSet(object):
	"""docstring for DataSet"""
	def __init__(self, describe, product_code):
		super(DataSet, self).__init__()
		self.describe, self.product_code = describe, product_code
		self.obj_path = './data/%s_%s.pkl'%(self.product_code,self.describe)
		#if existed obj 
		# if os.path.exists(self.obj_path)

		self.factor_mean, self.factor_std = dict(), dict()
		
		# read config file which contains all 
	
	def DumpDataSet(self):
		file = open(self.obj_path, 'wb')
		pickle.dump(self, file)
		file.close()		

		# return 0

	def MakeDataSet(self, num_of_testing_days = 255):
		#make the last consecutive year as the testing set
		hist_Z = self.hist_Z
		self.testing_set = hist_Z.iloc[-num_of_testing_days:]
		hist_Z = hist_Z.iloc[:-num_of_testing_days]
		

		#making sure binary signal are evenly distributed into two dataset
		positive_samples, nagtive_samples = hist_Z[ hist_Z['Mark'] == 1 ].copy(deep=True), hist_Z[ hist_Z['Mark'] == 0].copy(deep=True) 
		
		if len(positive_samples) < len(nagtive_samples):
			nagtive_samples = nagtive_samples.sample(n = len(positive_samples) , replace = False)
		elif len(positive_samples) > len(nagtive_samples):
			positive_samples = positive_samples.sample( n = len(nagtive_samples),  replace = False)

		#splite 80:20 as training and validation dataset 
		training_set_tmp  = positive_samples.sample(frac = 0.8, replace = False)
		self.training_set = training_set_tmp.copy(deep = True)
		self.validation_set = positive_samples[ [ i not in training_set_tmp.index.to_list() for i in positive_samples.index.to_list()]  ].copy(deep = True)

		training_set_tmp = nagtive_samples.sample(frac = 0.8, replace = False) 
		self.training_set = self.training_set.append( training_set_tmp.copy(deep = True) )
		self.validation_set = self.validation_set.append( nagtive_samples[ [ i not in training_set_tmp.index.to_list() for i in nagtive_samples.index.to_list()]  ].copy(deep = True)  ) 

		self.training_set = self.training_set.sample(frac = 1, replace = False)
		self.validation_set = self.validation_set.sample(frac = 1, replace = False)

		logging.info("\n Training Set length %d, %.2f positive \n"%(len(self.training_set), len(self.training_set[ self.training_set['Mark'] == 1 ])/len(self.training_set)  ))
		logging.info("\n validation Set Set length %d, %.2f positive \n"%(len(self.validation_set), len(self.validation_set[ self.validation_set['Mark'] == 1 ])/len(self.validation_set)  ))

		#update attributions and dump into disk
		self.DumpDataSet()

		return self.training_set, self.validation_set, self.testing_set

	def SelectFactsHis(self):

		self.hist_raw = openbb.stocks.load(
		        symbol = self.product_code,
		        start_date = '2000-01-01',
		        # end_date = '2022-01-01',
		        source = "AlphaVantage")
		

		self.hist_raw['YearTime'] = FactorConstructor.CalculateYearTime(self.hist_raw.index) 
		self.hist_raw['R_log'] = FactorConstructor.CalculateReturn(self.hist_raw['Close'])
		
		length_raw = len(self.hist_raw)

		#drop nan and return is 0
		self.hist_raw = self.hist_raw.dropna()
		length_dropped_nan = len(self.hist_raw)

		self.hist_raw = self.hist_raw[ self.hist_raw['R_log'] != 0]

		logging.info("\n %s Dropped nan %d, zero return %d, left %d \n"%(self.product_code, length_raw - length_dropped_nan, length_dropped_nan - len(self.hist_raw)  ,len(self.hist_raw)) )
		

		# self.hist_raw['MoM_Q'] = FactorConstructor.CalculateMomentum(self.hist_raw['R_log'], period = int(255/6) )
		# self.hist_raw['MoM_M'] = FactorConstructor.CalculateMomentum(self.hist_raw['R_log'], period = int(255/12) )
		# self.hist_raw['MoM_W'] = FactorConstructor.CalculateMomentum(self.hist_raw['R_log'], period = int(255/52) )

		self.hist_raw['MoM_Q'] = FactorConstructor.CalculateMomentum(self.hist_raw['Close'], period = int(255/6) )
		self.hist_raw['MoM_M'] = FactorConstructor.CalculateMomentum(self.hist_raw['Close'], period = int(255/12) )
		self.hist_raw['MoM_W'] = FactorConstructor.CalculateMomentum(self.hist_raw['Close'], period = int(255/52) )		

		self.hist_raw['Vol_Q'] = FactorConstructor.CalculateVolatility(self.hist_raw['R_log'], period = int(255/6) )
		self.hist_raw['Vol_M'] = FactorConstructor.CalculateVolatility(self.hist_raw['R_log'], period = int(255/12) )
		self.hist_raw['Vol_W'] = FactorConstructor.CalculateVolatility(self.hist_raw['R_log'], period = int(255/52) )

		self.hist_raw['Mark'] = SignalMarker.MarkForLongSignal(self.hist_raw['Open'], self.hist_raw['High'], 0.0065)
		# self.hist_raw['Short_Open_Low_Signal'] = SignalMarker.MarkForShortSignal(self.hist_raw['Open'], self.hist_raw['Low'])

		self.hist_raw = self.hist_raw.dropna()


		#Volume_Z can be defined as Z score in a certain window time, or ordering in a fixed certains days windows
		self.hist_Z = self.hist_raw[['Volume', 'YearTime', 'R_log','MoM_Q','MoM_M','MoM_W','Vol_Q','Vol_M','Vol_W']].copy(deep=True)

		for column in self.hist_Z:
			self.hist_Z[column], mean, std = FactorConstructor.MakeZScore(self.hist_Z[column])
			self.factor_mean[column] = mean
			self.factor_std[column] = std

		self.hist_Z['Mark'] = self.hist_raw['Mark'].copy(deep = True)
		
		# logging.info("\n %s Percentage of long signal %.5f, short signal %.5f\n"%(product_code, len(self.hist_raw[ self.hist_raw['Long_Open_High_Signal'] == 1 ])/len(self.hist_raw) , len(self.hist_raw[ self.hist_raw['Short_Open_Low_Signal'] == 1 ])/len(self.hist_raw)))
		# logging.info("\n %s \n"%(self.hist_Z.describe(include='all') ))

		return self.hist_Z

