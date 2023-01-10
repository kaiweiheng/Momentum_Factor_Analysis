import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from prettytable import PrettyTable
figure(figsize=(10, 10), dpi=100)

class Assessment(object):
	"""docstring for SignalAssessment"""
	def __init__(self, arg):
		super(SignalAssessment, self).__init__()
		self.arg = arg
	
	@staticmethod
	def AssessBinaryTrainingAndValidation(prediction, target, threshold = 0.5, describe = " "):
		'''
		prediction : numpy array
		target : numpy array
		'''
		accuracy, precision = -1, -1
		prediction = Assessment.ConvertPredictionToBinary(prediction, threshold)
		# accuracy =  1 - (sum(abs(prediction-target))/len(prediction))
		tp, fp, tn, fn = 0, 0, 0, 0
		for i in range(0, len(prediction)):
			if prediction[i] == 1 and target[i] == 1:
				tp += 1
			elif prediction[i] == 1 and target[i] == 0:
				fp += 1
			elif prediction[i] == 0 and target[i] == 1:
				fn += 1
			elif prediction[i] == 0 and target[i] == 0:
				tn += 1

		accuracy = (tp + tn)/ max(1, tp + tn + fp + fn)
		precision = tp / max(1,tp+fp)
		recall = tp / max(1, tp+fn)

		logging.info("%s total %d, tp %d, fp %d, tn %d, fn %d\n"%(describe, len(prediction), tp, fp, tn, fn))

		return accuracy, precision, recall

	@staticmethod
	def ConvertPredictionToBinary(prediction, threshold = 0.5):
		'''
		ConvertPredictionToBinary : convert pobability to 1 or 0


		prediction ： numpy array
		'''
		prediction[ prediction > threshold ] = 1
		prediction[ prediction <= threshold ] = 0

		return prediction

	@staticmethod
	def UnifyReturn(balances):
		return [ 100*b / balances[0] for b in balances]

	@staticmethod
	def AssessTradingStrategy(bench_mark, balance_record, product_name):
		fig, ax = plt.subplots(figsize=(15,10))

		ax.plot( np.arange(0, len(bench_mark), 1), bench_mark)

		ax.plot( np.arange(0, len(balance_record), 1), balance_record)	

		ax.set(xlabel='time ', ylabel='TR (Total Return)',
		       title='%s Momentum Strategy'%(product_name) )
		ax.grid()
		ax.legend( ('%s'%(product_name), 'Product'), loc='upper right', shadow=True)

		fig.savefig("./simulation_result/%s_Simulation_Result.png"%(product_name))
		plt.show()

		return 0

	# annual turnover
	@staticmethod
	def AssessReturns(testing_dates, bench_mark_record, product_record):
		'''
		bench_mark_record : array like, bench_mark_product NAV
		product_record : array like, product_record NAV
		'''
		
		bench_mark_return, product_return = Assessment.CalculateReturn(bench_mark_record), Assessment.CalculateReturn(product_record)

		#no of trades, average per trade PnL, median daily return
		# trades_day_table = PrettyTable(["/","No. of Trades","Avg PnL PreTrade","Median Daily Return"])
		# trades_day_table.add_row(["Product","/","/","/"])
		# trades_day_table.add_row(["Benchmark","/","/","/"])
		# print(trades_day_table)

		#No of win day, win rate, max consecutive win day,average consecutive win day, 
		product_win_rate, product_max_consec_win_days, product_avg_consecutive_win_days = Assessment.CalculateWinRatio(product_return)
		benchmark_win_rate, benchmark_max_consec_win_days, benchmark_avg_consecutive_win_days = Assessment.CalculateWinRatio(bench_mark_return)
		win_table = PrettyTable(["/","Win Rate","Max Consecutive Win days","Avg Consecutive Win days"])
		win_table.add_row(["Product","%.3f"%product_win_rate,"%.3f"%product_max_consec_win_days,"%.3f"%product_avg_consecutive_win_days])
		win_table.add_row(["Benchmark","%.3f"%benchmark_win_rate,"%.3f"%product_max_consec_win_days,"%.3f"%benchmark_avg_consecutive_win_days])
		print(win_table)

		############################################################################################
		#mean daily return, daily return std, daily downside std, daily sharp ratio, daily sortino ratio, Annual sharpe ratio, Annual Sortino Ratio
		beta = Assessment.CalculateBeta(bench_mark_return, product_return)

		product_downside, benchmark_downside = Assessment.CalculateDownsideStd(product_return), Assessment.CalculateDownsideStd(bench_mark_return)

		product_sharpe, benchmark_sharp = Assessment.CalculateSharpe(product_return), Assessment.CalculateSharpe(bench_mark_return)
		product_sharpe_ann, benchmark_sharp_ann = Assessment.CalculateSharpe(product_return, is_ann = True), Assessment.CalculateSharpe(bench_mark_return, is_ann = True)

		product_sortino, benchmark_sortino = Assessment.CalculateSortino(product_return), Assessment.CalculateSortino(bench_mark_return)
		product_sortino_ann, benchmark_sortino_ann = Assessment.CalculateSortino(product_return, is_ann = True), Assessment.CalculateSortino(bench_mark_return, is_ann = True)

		ratio_table = PrettyTable(["/*Dailys*/","Mean Re bps.","Std Re", "Downside Std (2% ann)", "Sharpe", "Beta", "Sortino", "Ann Sharpe", "Ann Sortino"])
		
		ratio_table.add_row(["Product","%.1f"%(10000*np.mean(product_return)),"%.4f"%np.std(product_return),"%.4f"%product_downside,
			"%.4f"%product_sharpe,"%.2f"%beta,"%.4f"%product_sortino,"%.4f"%product_sharpe_ann,"%.4f"%product_sortino_ann])
		
		ratio_table.add_row(["Benchmark","%.1f"%(10000*np.mean(bench_mark_return)),"%.4f"%np.std(bench_mark_return),"%.4f"%benchmark_downside,
			"%.4f"%benchmark_sharp,"/","%.4f"%benchmark_sortino,"%.4f"%benchmark_sharp_ann,"%.4f"%benchmark_sortino_ann])		
		print(ratio_table)


		############################################################################################
		#average drawdown duration, AvgDrawback, max drawdown duration, max dawrdown, 
		product_drawback_record, product_duration_record = Assessment.CalculateDrawbackAndDur(product_record)
		benchmark_drawback_record, benchmark_duration_record = Assessment.CalculateDrawbackAndDur(bench_mark_record)
		
		product_max_draw, product_maxd_duration = Assessment.CalculateMaxDrawback(product_record) 
		benchmark_max_draw, benchmark_maxd_duration = Assessment.CalculateMaxDrawback(bench_mark_record)

		jensenAlpha = Assessment.CalculateJensenAlpha(bench_mark_return, product_return)
		product_calmar, bench_mark_calmar = Assessment.CalculateCalmarRatio(product_return, product_record), Assessment.CalculateCalmarRatio(bench_mark_return, bench_mark_record)
		omega = Assessment.CalculateOmegaRatio(bench_mark_return, product_return)

		# total return, jensen alpha, calmar ratio, omega ratio, average drawdown duration
		total_return_table = PrettyTable(["%d TradeDs"%len(bench_mark_return),"Total_Return", "AvgDraw Dur" ,"AvgDrawback",
			"MaxDraw Dur", "MaxDrawback","calmar_ratio","jensen_alpha Ann","omega_ratio"])

		total_return_table.add_row(["Product","%.4f"%sum(product_return),"%.4f"%np.mean(product_duration_record),"%.4f"%np.mean(product_drawback_record),
			"%d"%product_maxd_duration, "%.4f"%product_max_draw, "%.4f"%product_calmar, "%.4f"%jensenAlpha, "%.4f"%omega])
		
		total_return_table.add_row(["Benchmark","%.4f"%sum(bench_mark_return),"%.4f"%np.mean(benchmark_duration_record),"%.4f"%np.mean(benchmark_drawback_record),
			"%d"%benchmark_maxd_duration,"%.4f"%benchmark_max_draw, "%.4f"%bench_mark_calmar, "/",  "/"])
		print(total_return_table)
		############################################################################################


		monthly_return_table = PrettyTable(  Assessment.GetMonthlyReturnDates(testing_dates[1:]) )
		monthly_return_table.add_row(Assessment.CalculateMonthlyReturn(product_record, "Product" ))
		monthly_return_table.add_row(Assessment.CalculateMonthlyReturn(bench_mark_record, "Benchmark"  ))
		print(monthly_return_table)

	@staticmethod
	def CalculateSharpe(price_returns, is_ann = False, ann_rf = 0):
		price_returns = [ r - (ann_rf/255) for r in price_returns]
		if is_ann:
			sharpe = np.mean(price_returns) / np.std(price_returns)
		else:
			sharpe = (255 * np.mean(price_returns) ) / (np.sqrt(255) * np.std(price_returns))
		return sharpe

	@staticmethod
	def CalculateSortino(price_returns, requiered_ann_return = 0.02, is_ann = False, ann_rf = 0):
		downside_std = Assessment.CalculateDownsideStd(price_returns, requiered_ann_return)

		price_returns = [r - (ann_rf/255) for  r in price_returns]
		if is_ann:
			sortino = (255 * np.mean(price_returns)) / (downside_std * np.sqrt(255))
		else:
			sortino = np.mean(price_returns) / downside_std
		# print("%s , %.4f"%(str(is_ann), sortino))
		return  sortino
	@staticmethod
	def CalculateJensenAlpha(bench_mark_return, product_return, rf_ann = 0):
		'''
		bench_mark_return : array like, log return of benchmark length to be equal with product_return
		product_return : array like
		'''
		beta = Assessment.CalculateBeta(bench_mark_return, product_return)
		# return  np.mean(product_return)/ (beta *  np.mean(bench_mark_return))

		# return 255*np.mean(np.array(product_return) - np.array(bench_mark_return))

		return  (255 * np.mean(product_return)) - rf_ann - (beta * 255 * np.mean(bench_mark_return))
 

	@staticmethod
	def CalculateCalmarRatio(price_returns, balance_records):
		avg_anuual_return = 255*np.mean(price_returns)
		max_draw_back, _ = Assessment.CalculateMaxDrawback(balance_records)
		return avg_anuual_return / max_draw_back


	@staticmethod
	def CalculateExcessReturns(bench_mark_return, product_return):
		output = []
		for i in range(0, len(bench_mark_return)):
			output.append(product_return[i]  - bench_mark_return[i])
		return output

	@staticmethod
	def CalculateOmegaRatio(bench_mark_return, product_return):
		excess_returns = Assessment.CalculateExcessReturns(bench_mark_return, product_return)

		return sum([ e for e in excess_returns if e > 0]) / abs(sum([ e for e in excess_returns if e < 0]))

	@staticmethod
	def CalculateReturn(data, is_log = True):
		'''
		data : list, price return
		'''
		output = np.ones(len(data)) * np.nan
		# data = data.to_list()

		for i in range(1,len(data)):
			if is_log:
				output[i] = np.log(data[i]/data[i-1])
			else:
				output[i] = (data[i]/data[i-1]) - 1
		return output[1:]


	@staticmethod
	def CalculateDownsideStd(price_returns, requiered_ann_return = 0.02):
		downside_std = sum([  (r - (requiered_ann_return/255))**2 for r in price_returns if ( r - (requiered_ann_return/255) ) < 0 ]) / len(price_returns)
		
		return np.sqrt(downside_std)

	@staticmethod
	def CalculateBeta(bench_mark_return, product_return):
		return np.cov(bench_mark_return, product_return)[0][1]/np.var(bench_mark_return)

	@staticmethod
	def CalculateMaxDrawback(balance_records):
		'''
		data : list, balance record
		'''
		max_record, min_record, drawback_record, duration_record = 0, 0, 0, 0

		for i in range(0,len(balance_records)):
			if i == 0 or balance_records[i] >= max_record:
				max_record = balance_records[i]
				min_record = balance_records[i]
				duration_record = 0
			
			elif balance_records[i] < min_record:
				min_record = balance_records[i]

				if drawback_record < abs(np.log(min_record/max_record)):
					drawback_record = abs(np.log(min_record/max_record))
			duration_record += 1

		return  drawback_record, duration_record

	@staticmethod
	def CalculateDrawbackAndDur(balance_records):
		'''
		balance_records : list, balance record
		'''
		drawback_record, duration_record = [], []
		max_record, min_record, drawback_tmp, duration_tmp = 0, 0, 0, 0

		for i in range(0, len(balance_records)):
			if i == 0 or balance_records[i] > min_record:
				if duration_tmp != 0:
					drawback_record.append(drawback_tmp)
					duration_record.append(duration_tmp)

				max_record = balance_records[i]
				min_record = balance_records[i]
				drawback_tmp, duration_tmp = 0, 0

			elif balance_records[i] <= min_record:
				min_record = balance_records[i]

				if drawback_tmp < abs(np.log(min_record/max_record)):
					drawback_tmp = abs(np.log(min_record/max_record))
			duration_tmp += 1


		if duration_tmp != 0:
			drawback_record.append(drawback_tmp)
			duration_record.append(duration_tmp)			

		return drawback_record, duration_record

	@staticmethod
	def CalculateMonthlyReturn(balance_records, product_code, return_type = "str"):
		# monthly return (every 25 trading dates)
		daily_return = Assessment.CalculateReturn(balance_records)
		if return_type == "str":
			output = [product_code]

			for i in range(0, len(daily_return), 25):
				tmp = sum(daily_return[i: min(i+25, len(daily_return))])
				output.append("%.4f"%(tmp))

			return output

		return [  sum(daily_return[i : min(i+25, len(daily_return)) ])   for i in range(0, len(daily_return), 25) ]


	@staticmethod
	def GetMonthlyReturnDates(dates):
		output = ["/"]
		for i in range(0, len(dates), 25):
			output.append( "%s"%(dates[i].strftime('%Y%m%d') ))

		# output.append( "Whole_Period_to%s"%(dates[-1].strftime('%Y%m%d') ))
		return output

	@staticmethod
	def CalculateWinRatio(price_returns):
		win_ratio = len([r for r in price_returns if r > 0])/len(price_returns)

		win_day_record, tmp = [], 0
		for r in price_returns:
			if r > 0:
				tmp += 1
			else:
				win_day_record.append(tmp)
				tmp = 0

		return win_ratio, max(win_day_record), np.mean(win_day_record)
