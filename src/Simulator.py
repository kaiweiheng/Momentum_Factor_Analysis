from Assessment import Assessment
from OrderMaker import OrderMaker
from Experiment import Experiment

from prettytable import PrettyTable
from FactorConstrctor import FactorConstructor
import datetime
import logging
class Simulator(object):
	"""docstring for Simulator"""
	def __init__(self, startbalace, expected_gain, product_list):
		super(Simulator, self).__init__()
		self.balance, self.expected_gain, self.product_list  = startbalace, expected_gain, product_list
		self.testing_prediction_list, self.testing_set_list, self.order_maker_list = dict(), dict(),dict()
		
		for p in product_list:
			validation_preci, testing_prediction, testing_set =  self.PrepareModelAndTestingSet(p)
			self.testing_prediction_list[p] = testing_prediction
			self.testing_set_list[p] = testing_set
			self.order_maker_list[p] = OrderMaker(validation_preci, expected_gain)

			# self.testing_prediction_list.append(testing_prediction)
			# self.testing_set_list.append(testing_set)
			# self.order_maker_list.append(OrderMaker(validation_preci, expected_gain))


	def PrepareModelAndTestingSet(self, product, signal_type = "LongSig"):
		exp = Experiment(signal_type, product) 
		testing_prediction = exp.MakePredictionExperiment()
		validation_preci = exp.validation_preci 
		last_year = exp.data_set.hist_raw.iloc[-255:] #2021-12-15 to 2022-12-19		
		return validation_preci, testing_prediction, last_year

	def Simulate(self):

		length =  -1
		#checking the length of simulation data are the same
		for p in self.product_list:
			l = self.testing_set_list[p]
			if length == -1:
				length = len(l)
			elif length != len(l):
				#throw out error
				raise Exception("%s has days of testing_set %d, others has %s"%(p, len(l), length))

		testing_dates = self.testing_set_list[ self.product_list[0] ].index.to_list()
		balace_records, PnL_records = [], []
		# #for each day
		for acc in range(0, length - 1):
			#for each product propose deals
			order_tables_for_a_day = dict()

			for p in self.product_list:
				prediction_for_a_testing_date = self.testing_prediction_list[p][acc]
				open_price = self.testing_set_list[p].iloc[acc+1]["Open"]

				order_table = self.order_maker_list[p].MakeDayTradeOrderTemplateForADay()
				order_table = self.order_maker_list[p].MakeDayTradeLongSignalOrder(prediction_for_a_testing_date, open_price, self.balance, order_table)
				
				order_tables_for_a_day[p] = order_table


			#select product to do simulation
			# a = 0 
			# for key in order_tables_for_a_day.keys():
			# 	if order_tables_for_a_day[key]["OpenQ"] > 0:
			# 		a += order_tables_for_a_day[key]["OpenQ"] * order_tables_for_a_day[key]["OpenP"]

			# print("%s  %.2f \n"%(testing_dates[acc], a/self.balance))


			#do simulation, calculate PnL
			PnL_table = {}
			for p in self.product_list:
				order_table = order_tables_for_a_day[p]
				PnL_table[p] = self.CalculatePnL(order_table, self.testing_set_list[p].iloc[acc+1], testing_dates[acc+1])

			self.balance += sum(PnL_table.values())
			
			PnL_records.append(sum(PnL_table.values()))
			balace_records.append(self.balance)

		#making assessment
		# for p in self.product_list:

		unified_balance_records = Assessment.UnifyReturn(balace_records)	
		bench_mark = Assessment.UnifyReturn(self.testing_set_list[ self.product_list[0] ]["Close"].to_list()[1:])

		Assessment.AssessTradingStrategy(bench_mark, unified_balance_records, self.product_list[0] )

		Assessment.AssessReturns(testing_dates, bench_mark, unified_balance_records)

		# return_table = PrettyTable(  Assessment.GetMonthlyReturnDates(testing_dates[1:]) )
		# return_table.add_row(Assessment.CalculateMonthlyReturn(unified_balance_records, "Product" ))
		# return_table.add_row(Assessment.CalculateMonthlyReturn(bench_mark, self.product_list[0]   ))
		# print(return_table)




		return balace_records, PnL_records

	def CalculatePnL(self, order_table, testing_set_for_a_day, testing_date):
		Open, High, Low, Close = testing_set_for_a_day["Open"],testing_set_for_a_day["High"], testing_set_for_a_day["Low"], testing_set_for_a_day["Close"]

		cumulated_Q, position, profit, comission = 0, 0, 0, []

		if order_table["OpenQ"] != 0:
			position -= order_table["OpenQ"] * order_table["OpenP"]
			cumulated_Q += order_table["OpenQ"]
			comission.append(self.CalculateFutuUSCommision(order_table["OpenP"],  order_table["OpenQ"])) 
			# logging.info("%s Open %d, Price %.2f  cumulated_Q %d\n"%(testing_date,order_table["OpenQ"], order_table["OpenP"],cumulated_Q))			

		if order_table["HighQ"] != 0 and High >= order_table["HighP"]:
			position -= order_table["HighQ"] * order_table["HighP"]
			cumulated_Q += order_table["HighQ"]
			comission.append(self.CalculateFutuUSCommision(order_table["HighP"],  order_table["HighQ"])) 
			# logging.info("%s HighMeet %d, Price %.2f  cumulated_Q %d\n"%(testing_date,order_table["HighQ"], order_table["HighP"],cumulated_Q))			

		if order_table["LowQ"] != 0 and Low <= order_table["LowP"]:
			position -= order_table["LowQ"] * order_table["LowP"]
			cumulated_Q += order_table["LowQ"]
			comission.append(self.CalculateFutuUSCommision(order_table["LowP"],  order_table["LowQ"])) 
			# logging.info("%s LowMeet %d, Price %.2f  cumulated_Q %d\n"%(testing_date,order_table["LowQ"], order_table["LowP"],cumulated_Q))			

		if cumulated_Q != 0:
		#cob clear position
			position -= -cumulated_Q * Close
			# cumulated_Q += q
			comission += self.CalculateFutuUSCommision(Close, -cumulated_Q)

		profit = position - sum(comission)		

		return profit

	@staticmethod
	def CalculateFutuUSCommision(P, Q):
		'''
		https://www.futuhk.com/commissionnew?lang=zh-hk
		'''
		comission = max(0.99, 0.0049*abs(Q))
		platform_fee = max(1, 0.005*abs(Q))
		deal_fee = 0.003*abs(Q) 
		SCE_fee, activity_fee = 0,0

		if Q < 0:
			SCE_fee = max(0.000029*P*abs(Q),0.01)
			activity_fee = min(  max(0.00013*abs(Q), 0.01)  ,6.49)

		return comission + platform_fee + deal_fee + SCE_fee + activity_fee