import numpy as np

class SignalMarker(object):
	"""
	docstring for SignalMarker:

	Marking a days signal for different trading strategy, 
	but in general it will 


	"""
	def __init__(self, arg):
		super(SignalMarker, self).__init__()
		self.arg = arg
	
	@staticmethod
	def AlignInputsAndCreateOutput(input_1, input_2):

		if len(input_1) != len(input_2) or len(input_1) == 0 or len(input_2) == 0: 
			raise TypeError("Inputs Size doesn't Match, input1 %d, input2 %s \n"%(len(input_1),len(input_2)))
		return 	np.zeros(len(input_1))

	@staticmethod
	def MarkForLongSignal(open, long_price, rate = 0.0075):
		'''
		long_price : list, price high or close
		
		To mark the next day's log(long_price/open) > rate

		'''

		#checking two input have the same length

		output = SignalMarker.AlignInputsAndCreateOutput(open, long_price)
 		
		for i in range(0,len(long_price)-1):
			if  np.log( long_price[i+1] / open[i+1] ) > rate:
				output[i]  = 1

		output[-1] = np.nan
		return output


	@staticmethod
	def MarkForShortSignal(open, short_price, rate = 0.0075):
		'''
		short_price : list, price low or close
		'''
		output = SignalMarker.AlignInputsAndCreateOutput(open, short_price)

		for i in range(0,len(short_price)-1):
			if  np.log( open[i+1] / short_price[i+1] ) > rate:
				output[i]  = 1
				
		output[-1] = np.nan

		return output
