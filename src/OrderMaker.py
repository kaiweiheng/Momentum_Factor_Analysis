class OrderMaker(object):
	"""
	docstring for OrderMaker

	"""
	def __init__(self, precision, expected_gain):
		super(OrderMaker, self).__init__()
		self.precision = precision
		self.expected_gain = expected_gain + 1
		self.fraction = self.KellyBetPortion()

	def MakeDayTradeLongSignalOrder(self, prediction, open_price, balance, order_table):
		'''
		Make Order take prediction signal as input, to produce output of a table for difference types of order, price and quantity
		
		Market_Order_Open, Q_MOO , Limited_Order, Price, Q_LO, Market_Order_
		'''
		q = 0
		if prediction == 1:
			q = int(balance*self.fraction/open_price)
			order_table["OpenQ"] += q
			order_table["OpenP"] = open_price


			order_table["High"] = -q
			order_table["HighP"] = open_price*self.expected_gain
		return order_table

	def MakeDayTradeShortSignalOrder(self, prediction):
		'''
		Make Order take prediction signal as input, to produce output of a table for difference types of order, price and quantity
		
		Market_Order_Open, Q_MOO , Limited_Order, Price, Q_LO, Market_Order_
		'''

		return 0		

	def MakeDayTradeOrderTemplateForADay(self):

		return { "OpenQ" : 0, "HighQ" : 0, "LowQ" : 0 }

	def KellyBetPortion(self):
		'''
		Kelly's ratio to decide fraction of the assets to apply to the security

		portion =  p - ( (1-p)/(b)), p:probability of win, b: proportion of the bet gained with a win
		'''
		return  self.precision - ( (1 - self.precision) / (self.expected_gain)  )


	def KellyInvestedPortion(self):
		'''
		Kelly's ratio to decide fraction of the assets to apply to the security

		portion =  (p/a)/( (1-p)/b), p:probability of win, b: proportion of the bet gained with a win, a: proportion of the bet gained with a loss
		'''
		return 0 
