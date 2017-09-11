# -*- coding: utf-8 -*-

import sqlite3
import re
from string import digits
from string import maketrans
from datetime import datetime

#CALCULATE NUTRIENT AMOUNT DATA
#Retrieve database
conn_nutr = sqlite3.connect('/home/kevin/Summer2017/RecipeAPI/nutrient.db')
conn_recp = sqlite3.connect('/home/kevin/Summer2017/RecipeAPI/recipe.db')
cursor_rcp_ing = conn_recp.execute("SELECT recipe_ingredient from RECIPE")
cursor_only_ing = conn_recp.execute("SELECT only_ingredient from RECIPE")


#Input the ingredient words (without any amount/description/other unnecessary words) into a list
def get_just_ing_list():
	just_ing_items = []
	for row in cursor_only_ing:
		ing_items = str(row).replace("(u'", "").replace("',)", "").replace('(u"', '').replace('",)', '')
		just_ing_items.append(ing_items)
	return just_ing_items


def get_amount(item,ser_amt,just_ingr):

	actual_amt = "0"

	ser_amt = str(ser_amt).lower().split(" = ")	#e.g. 30g = 2 tablespoons
	gram_amnt = ser_amt[0].replace("g", "")		#e.g. 30
	other_unit_amnt = ser_amt[1]				#e.g. 2 tablespoons

	#CONVERT EVERYTHING TO GRAMS
	
	#Specifically for when units are wacky in other_unit_amnt e.g. 150g = 1.0 lobster, 17g = 1.0 large, etc
	unit = other_unit_amnt.translate(None, digits).replace(".", "")	
	if unit in item:
		amnt = find_number(item,unit)
		other_unit_amnt = find_number_simple_ver(unit,other_unit_amnt)
		actual_amt = str(float(gram_amnt) / float(other_unit_amnt) * float(amnt)) + "g"

	#For SPECIAL CASES
	elif "g " in item and item[item.find("g ") - 1].isdigit():
		amnt = find_number(item, "g ")
		actual_amt = amnt + "g"
	elif "g)" in item and (item[item.find("g)") - 1].isdigit() or item[item.find("g)") - 2].isdigit()):
		amnt = find_number(item, "g)")
		actual_amt = amnt + "g"
	elif "g/" in item and (item[item.find("g/") - 1].isdigit() or item[item.find("g/") - 2].isdigit()):
		amnt = find_number(item, "g/")
		actual_amt = amnt + "g"
	
	#For normal units
	else:
		units = ["gram"," g ","pound"," lb","lb ","ounce"," oz"," oz","teaspoon","tsp","tablespoon","tbsp","cup","pinch","dash","milliliter"," ml","ml ","liter","quart"," qt","handful","clove","slice"]
		for unit in units:
			if unit in item:
				amnt = find_number(item,unit)
		
				if unit in other_unit_amnt:
					other_unit_amnt = find_number_simple_ver(unit,other_unit_amnt)
					actual_amt = str(float(gram_amnt) / float(other_unit_amnt) * float(amnt)) + "g"
				
				elif unit == "gram" or unit == " g ":
					actual_amt = amnt + "g"

				elif unit == "pound" or unit == " lb" or unit == "lb ":
					actual_amt = str(float(amnt) * 453.6)  + "g"
				
				elif unit == "ounce" or unit == " oz" or unit == "oz ":
					actual_amt = str(float(amnt) * 28.35)  + "g"

				elif unit == "teaspoon":
					if "tsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tsp",other_unit_amnt)
						actual_amt = str(float(gram_amnt) / float(other_unit_amnt) * float(amnt)) + "g"
					elif "cup" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("cup",other_unit_amnt)
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/48)) + "g"	#US customary 48 teaspoon = 1 cup
					elif "tbsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tbsp",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/3)) + "g"	#US customary 1 teaspoon = 3 tablespoon
					elif "tablespoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tablespoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/3)) + "g"
					elif "fl oz" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("fl oz",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/6)) + "g"	#US customary 1 teaspoon = 1/6 fl oz
				
				elif unit == "tsp":
					if "teaspoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("teaspoon",other_unit_amnt)
						actual_amt = str(float(gram_amnt) / float(other_unit_amnt) * float(amnt)) + "g"
					elif "cup" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("cup",other_unit_amnt)
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/48)) + "g"
					elif "tbsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tbsp",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/3)) + "g"
					elif "tablespoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tablespoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/3)) + "g"
					elif "fl oz" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("fl oz",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/6)) + "g"	
				
				elif unit == "tbsp":
					if "tablespoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tablespoon",other_unit_amnt)
						actual_amt = str(float(gram_amnt) / float(other_unit_amnt) * float(amnt)) + "g"
					elif "cup" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("cup",other_unit_amnt)
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/16)) + "g"	#US customary 16 tablespoon = 1 cup
					elif "tsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tsp",other_unit_amnt)				
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*3)) + "g"
					elif "teaspoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("teaspoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*3)) + "g"
					elif "fl oz" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("fl oz",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/2)) + "g"	#US customary 1 tablespoon = 1/2 fl oz

					#SPECIAL
					elif "butter" in just_ingr:
						actual_amt = str(float(amnt)*14.18) + "g" 	# 1 tbsp of butter = 14.18g
					elif "cilantro" in just_ingr:
						actual_amt = amnt + "g" 					# 1 tablespoon of cilantro = 1g
					elif "cheese" in item:
						actual_amt = str(float(amnt)*6) + "g"		# 1 tablespoon of cheese = 6g
				
				elif unit == "tablespoon":
					if "tbsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tbsp",other_unit_amnt)
						actual_amt = str(float(gram_amnt) / float(other_unit_amnt) * float(amnt)) + "g"
					elif "cup" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("cup",other_unit_amnt)
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/16)) + "g"
					elif "tsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tsp",other_unit_amnt)				
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*3)) + "g"
					elif "teaspoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("teaspoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*3)) + "g"
					elif "fl oz" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("fl oz",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/2)) + "g"

					#SPECIAL
					elif "butter" in just_ingr:
						actual_amt = str(float(amnt)*14.18) + "g" 	# 1 tablespoon of butter = 14.18g
					elif "cilantro" in just_ingr:
						actual_amt = amnt + "g" 					# 1 tablespoon of cilantro = 1g
					elif "cheese" in item:
						actual_amt = str(float(amnt)*6) + "g"		# 1 tablespoon of cheese = 6g
				
				elif unit == "cup":
					if "tbsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tbsp",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*16)) + "g"
					elif "tablespoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tablespoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*16)) + "g"
					elif "tsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tsp",other_unit_amnt)				
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*48)) + "g"
					elif "teaspoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("teaspoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*48)) + "g"
					elif "fl oz" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("fl oz",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*8)) + "g"		#US customary 1 cup = 8 fl oz
					elif "milliliter" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("milliliter",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*236.6)) + "g"	#US customary 1 cup = 236.6 milliliter
					elif " ml" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver(" ml",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*236.6)) + "g"

					#SPECIAL
					elif "ham" in just_ingr:
						actual_amt = str(float(amnt)*140) + "g"		# 1 cup of diced ham ~ 140g
					elif "butter" in just_ingr:
						actual_amt = str(float(amnt)*227) + "g" 	# 1 cup of butter ~ 227g
					elif "cheese" in just_ingr:
						actual_amt = str(float(amnt)*115) + "g" 	# 1 cup of cheese ~ 4 ounce ~ 115g

				elif unit == "pinch":
					if "tbsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tbsp",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/48)) + "g"
					elif "tablespoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tablespoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/48)) + "g"
					elif "tsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tsp",other_unit_amnt)				
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/16)) + "g"
					elif "teaspoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("teaspoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/16)) + "g"

				elif unit == "dash":
					if "tbsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tbsp",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/24)) + "g"
					elif "tablespoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tablespoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/24)) + "g"
					elif "tsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tsp",other_unit_amnt)				
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/8)) + "g"
					elif "teaspoon" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("teaspoon",other_unit_amnt)	
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)/8)) + "g"

				elif unit == " ml" or unit == "ml ":
					if "tbsp" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("tbsp",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*0.0676)) + "g"	#US customary 1 ml = 0.067 tbsp
					elif "fl oz" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("fl oz",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*0.0338)) + "g"	#US customary 1 ml = 0.0338 fl oz

				elif unit == "liter":
					if "fl oz" in other_unit_amnt:
						other_unit_amnt = find_number_simple_ver("fl oz",other_unit_amnt)			
						actual_amt = str((float(gram_amnt) / float(other_unit_amnt)) * (float(amnt)*33.8)) + "g"
				
				elif unit == "clove" and "garlic" in just_ingr:
					actual_amt = str(float(amnt) * (11)) + "g"		# 1 garlic clove ~ 11g
				elif unit == "slice":
					if "bacon" in just_ingr:
						actual_amt = str(float(amnt) * (26)) + "g"		# 1 slice bacon ~ 26g
					elif "ham" in just_ingr:
						actual_amt = str(float(amnt) * (56)) + "g"		# 1 slice ham ~ 56g
					elif "pepperoni" in just_ingr:
						actual_amt = str(float(amnt) * (4)) + "g"		# 1 slice pepperoni ~ 4g

				break
	
	if actual_amt == "0":	#no units were provided
		
		if "bay" in just_ingr:
			amnt = find_number(item, "bay lea")
			actual_amt = str(float(amnt) * (0.2)) + "g"		# 1 bay leaf ~ 0.2g
		elif "jalapeno" in item or "chili pepper" in item or "chilli pepper" in item:
			amnt = find_number(item, "jalapeno")
			if amnt == 0.1:
				amnt = find_number(item, "chili pepper")
				if amnt == 0.1:
					amnt = find_number(item, "chilli pepper")
			actual_amt = str(float(amnt) * (15)) + "g"		# 1 jalapeno pepper ~ 15g
		elif "egg" in just_ingr or "hamburger bun" in just_ingr:
			amnt = find_number(item, "egg")
			if amnt == "0.1":
				amnt = find_number(item, "hamburger bun")
			actual_amt = str(float(amnt) * (42)) + "g"		# 1 medium egg ~ 1.5 ounces ~ 42g ~ 1 hamburger bun
		elif "tortilla" in just_ingr:
			amnt = find_number(item, "tortilla")
			actual_amt = str(float(amnt) * (48)) + "g"		# 1 tortilla ~ 48g
		elif "carrot" in just_ingr or "lemon" in just_ingr:
			amnt = find_number(item, "carrot")
			if amnt == "0.1":
				amnt = find_number(item, "carrot")
			actual_amt = str(float(amnt) * (61)) + "g"		# 1 medium carrot/lemon ~ 61g
		elif "onion" in just_ingr:
			amnt = find_number(item, "onion")
			actual_amt = str(float(amnt) * (90)) + "g"		# 1 medium onion ~ 90g
		elif "bell pepper" in item:
			amnt = find_number(item, "bell pepper")
			actual_amt = str(float(amnt) * (140)) + "g"		# 1 medium bell pepper ~ 140g
		elif "avocado" in just_ingr:
			amnt = find_number(item, "avocado")
			actual_amt = str(float(amnt) * (90)) + "g"		# 1 medium avocado ~ 150g
		elif "whole chicken" in item:
			amnt = find_number(item, "whole chicken")
			actual_amt = str(float(amnt) * (960)) + "g"		# 1 whole chicken ~ 960g
		elif "chicken breast" in just_ingr:
			amnt = find_number(item, "chicken breast")
			actual_amt = str(float(amnt) * (213)) + "g"		# 1 chicken breast ~ 213g
		else:
			amnt = find_number(item, item[(len(item)-5):])
			if amnt == "0.1":
				actual_amt = amnt + "g"
			else:
				actual_amt = amnt + " unknown"

	return actual_amt


#Super complex version
def find_number(item,unit):
	if item.count(unit) > 1:		#if more than one instance of unit occuring in string, index is very end of string
		index = len(item)	
	else:
		index = item.find(unit)
	amount =""
	while True:
		index = index - 1			#Go backwards from the index of where you found unit to find the amount
		if item[index].isdigit():
			if "inch" in item[index:index+6] or "piece" in item[index:index+8]:
				while True:
					index = index - 1
					if item[index]==" " and any(char.isdigit() for char in item[index:index+3]):
						break
					if index <= 0:
						break
				continue
			elif " to " in item[index:index+5]:
				if amount == "":	#e.g. 2 to 3 inches
					index = index - 2
					continue
			if item[index+1]=="/":			#e.g. 1/4
				amount = str(float(item[index]) / float(item[index+2])) + amount
			elif item[index+1]==".":		#e.g. 1.5
				amount = str(float(item[index]) + float(amount)/(10**len(amount)))
			elif item[index+2].isdigit():
				if item[index+3]=="/":		#e.g. 1 1/4
					amount = str(float(item[index]) + float(amount))
				elif item[index+1]==" ":	#e.g. 2 8-pound meat
					amount = str(float(item[index]) * float(amount))
				elif item[index+1]=="-":	#e.g. 2-8 pound meat
					amount = amount
				else:						#e.g. 28 pound meat
					amount = item[index] + amount
			elif item[index+1].isdigit() and item[index+2]=="-" and item[index+3].isdigit():
				amount = amount 			#e.g. 28-30 pound meat
			else:							
				amount = item[index] + amount
		if amount != "":
			if not item[index].isdigit():		#Once there's no more digits , leave the while loop
				if item[index]=="/":
					continue
				elif item[index-1].isdigit():	#e.g. 1 1/4 cups of ... check if index before is a number
					continue
				else:
					container = ["can", "package","bag","bottle","jar"]
					for con in container:
						if con in item:			#e.g. 2 cans (14 oz.) of ...    2 (14 oz) cans of ... 3 x 100oz cans of ...
							if item[item.find(con)-2].isdigit():
								amount = str(float(amount)*float(item[item.find(con)-2]))
							elif item[item.find(con)-2] == ")":
								if item[index]=="(" and item[index-2].isdigit():
									amount = str(float(amount)*float(item[index-2]))
							elif "x" in item[:index] and any(char.isdigit() for char in item[:index]):
								multi = [s for s in item[:index] if s.isdigit()]
								multi = ''.join(multi)
								amount = str(float(amount)*float(multi))
					break
		if index <= 0:
			amount = "0.1"
			break

	return amount


#Simple version
def find_number_simple_ver(unit,other_unit_amnt):
	number = ""
	other_unit_amnt = " " + other_unit_amnt
	unit_idx = other_unit_amnt.find(unit)
	index = 1
	while True:								#go backwards from the index of where unit is
		if other_unit_amnt[unit_idx - index] == "/":
			index = index + 1
			continue
		elif other_unit_amnt[unit_idx - index].isdigit() or other_unit_amnt[unit_idx - index] == ".":
			if other_unit_amnt[unit_idx - index + 1] == "/":
				number = str(float(other_unit_amnt[unit_idx - index]) / float(number))
			else:
				number = other_unit_amnt[unit_idx - index] + number
		elif other_unit_amnt[unit_idx - index] == " " and number != "":
			break
		index = index + 1
	return number


if __name__ == "__main__":
	
	just_ing_items = get_just_ing_list()

	x = 0
	for ingr_list in cursor_rcp_ing:
		
		ing_list = str(ingr_list).replace("(u'", "").replace("',)", "").replace('(u"', '').replace('",)', '').split(' + ')	#row is tuple, need to convert to string
		just_ing = just_ing_items[x].split(" + ")

		c = 0
		for ing in ing_list:

			ing = " " + ing.lower() + " "	#add spacing at end and beginning cuz convenience
			
			if just_ing[c] in ing:			#make sure the corresponding ingredient word (without amount/desc words) is actually in ingredient string (with the amount/desc words)

				serving_amount = conn_nutr.execute("SELECT Serving_Amount from NUTRIENT WHERE Ingredient_Name = ? limit 1", (just_ing[c],))
				ser_amt = serving_amount.fetchall()	#YOU CAN ONLY CALL FETCHALL() / FETCHONE() FUCNTION ONLY ONCE!!!!!!!!

				if len(ser_amt) == 0:		#if data does not exist in nutrient database
					continue
				
				else:
					ser_amt = ser_amt[0][0]	#e.g. of ser_amt : 30g = 2 tablespoons (for salt), 	29g = 1.0 slice (for white bread), etc	
					amt = get_amount(ing,ser_amt,just_ing[c])	
					
					if "unknown" in amt:
						print ser_amt
						print just_ing[c]
						print amt
						print ing 
						print

				serving_amount.close()	#need to close this equiv cursor cuz Sqlite3 Error

			if c == len(just_ing)-1:	#if you reach end of the just_ing list
				break

			c = c + 1 #index counter for just_ing list
			
		x = x + 1 #index counter for just_ing_items list

	conn_recp.close()
	conn_nutr.close()
			


















'''
#MACHINE LEARNING DATA
conn = sqlite3.connect('/home/kevin/Summer2017/src/rqt_mypkg/src/rqt_mypkg/User_Selected_Recipe.db')
conn.execute("CREATE TABLE USER_RECOM_SELECTION_DATA (recipe_title text)")
conn.execute("ALTER TABLE USER_RECOM_SELECTION_DATA ADD COLUMN time_of_day text");

time_of_day = str(datetime.now())
print time_of_day
'''


'''
#TensorFlow Practice
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
import tensorflow as tf
# NumPy is often used to load, manipulate and preprocess data.
import numpy as np

# Declare list of features. We only have one real-valued feature. There are many
# other types of columns that are more complicated and useful.
features = [tf.contrib.layers.real_valued_column("x", dimension=1)]

# An estimator is the front end to invoke training (fitting) and evaluation
# (inference). There are many predefined types like linear regression,
# logistic regression, linear classification, logistic classification, and
# many neural network classifiers and regressors. The following code
# provides an estimator that does linear regression.
estimator = tf.contrib.learn.LinearRegressor(feature_columns=features)

# TensorFlow provides many helper methods to read and set up data sets.
# Here we use two data sets: one for training and one for evaluation
# We have to tell the function how many batches
# of data (num_epochs) we want and how big each batch should be.
x_train = np.array([1., 2., 3., 4.])
y_train = np.array([0., -1., -2., -3.])
x_eval = np.array([2., 5., 8., 1.])
y_eval = np.array([-1.01, -4.1, -7, 0.])
input_fn = tf.contrib.learn.io.numpy_input_fn({"x":x_train}, y_train,
                                              batch_size=4,
                                              num_epochs=1000)
eval_input_fn = tf.contrib.learn.io.numpy_input_fn(
    {"x":x_eval}, y_eval, batch_size=4, num_epochs=1000)

# We can invoke 1000 training steps by invoking the  method and passing the
# training data set.
estimator.fit(input_fn=input_fn, steps=1000)

# Here we evaluate how well our model did.
train_loss = estimator.evaluate(input_fn=input_fn)
eval_loss = estimator.evaluate(input_fn=eval_input_fn)
print("train loss: %r"% train_loss)
print("eval loss: %r"% eval_loss)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
'''