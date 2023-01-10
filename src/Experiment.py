import os
import sys
import logging
import pickle
from prettytable import PrettyTable

from DataSet import DataSet
from Assessment import Assessment
from sklearn import linear_model

class Experiment(object):
	"""docstring for Experiment"""
	def __init__(self, describe, product_code):
		super(Experiment, self).__init__()
		self.describe, self.product_code = describe, product_code
		self.data_path = './data/%s_%s.pkl'%(self.product_code,self.describe)

		#if existed obj 
		if os.path.exists(self.data_path):
			logging.info("Loading existed dataset from %s \n"%(self.data_path))
			objectRep = open(self.data_path, "rb")
			self.data_set =  pickle.load(objectRep)

		else:
		#select from obb	
			logging.info("Buld from obb, saved at %s \n"%(self.data_path))
			self.data_set = DataSet(describe, product_code)
			self.data_set.SelectFactsHis()
			_, _, _ = self.data_set.MakeDataSet(255)
	
		# _, _, _ = self.data_set.MakeDataSet()
	def MakePredictionExperiment(self):
		training_set, validation_set, testing_set = self.data_set.training_set, self.data_set.validation_set, self.data_set.testing_set

		regr = linear_model.LinearRegression()
		regr.fit( training_set[["Volume", "YearTime", "R_log", "MoM_Q", "MoM_M","MoM_W","Vol_Q","Vol_M","Vol_W"]].to_numpy(),
				 training_set[["Mark"]].to_numpy())

		training_Prediction = regr.predict(training_set[["Volume", "YearTime", "R_log", "MoM_Q", "MoM_M","MoM_W","Vol_Q","Vol_M","Vol_W"]].to_numpy())
		Validation_Prediction = regr.predict(validation_set[["Volume", "YearTime", "R_log", "MoM_Q", "MoM_M","MoM_W","Vol_Q","Vol_M","Vol_W"]].to_numpy())
		Testing_Prediction = regr.predict(testing_set[["Volume", "YearTime", "R_log", "MoM_Q", "MoM_M","MoM_W","Vol_Q","Vol_M","Vol_W"]].to_numpy())

		#try to assess regression model acc and over fitting
		training_acc, training_preci, training_recall= Assessment.AssessBinaryTrainingAndValidation(training_Prediction, training_set[['Mark']].to_numpy(), 0.6, "%s_training"%(self.product_code))    
		validation_acc, validation_preci, validation_recall = Assessment.AssessBinaryTrainingAndValidation(Validation_Prediction, validation_set[['Mark']].to_numpy(), 0.6, "%s_validation"%(self.product_code))
		testing_acc, testing_preci, testing_recall = Assessment.AssessBinaryTrainingAndValidation(Testing_Prediction, testing_set[['Mark']].to_numpy(), 0.6, "%s_testing"%(self.product_code))


		t = PrettyTable(["%s_%s"%(self.product_code, self.describe), "Acc", "Precision","Recall"])
		t.add_row(["Training", "%.4f"%(training_acc), "%.4f"%(training_preci), "%.4f"%(training_recall) ])
		t.add_row(["Validation", "%.4f"%(validation_acc), "%.4f"%(validation_preci), "%.4f"%(training_recall) ])
		t.add_row(["Testing", "%.4f"%(testing_acc), "%.4f"%(testing_preci), "%.4f"%(training_recall) ])

		self.validation_acc, self.validation_preci = validation_acc, validation_preci
		# logging.info(t)
		print(t)
		return Testing_Prediction