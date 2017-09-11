import os
import rospy
import rospkg
import sqlite3
import urllib2
import requests
import json
import re

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget
from PyQt4 import QtGui, QtCore
from itertools import chain

#Global Variables
prev_selected_recipe =[]

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#Retrive data from database

def get_prev_selected_recipes(self,conn):
	rcp_title = conn.execute("SELECT recipe_title from USER_RECOM_SELECTION_DATA")
	for row in rcp_title:
		row = ''.join(row)	#must do ''.join(row) cuz row is tuple object and need to be converted to string
		prev_selected_recipe.append(row)

	return prev_selected_recipe


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#Recipe Recommendation Algorithm

#1 ounce = 28 gram, 1 quart (fluid) = 32 ounce (fluid), 1 pound = 16 ounce, 1 quart(fluid) = 4 cups (fluid)

#Find recipe with largest amount of asked ingredient
def largest_amount_alg(ing,conn,unwanted,wanted):

	ingr_s = " " + ing + "s "
	ingr = " " + ing + " "
	chosen_recipe = ""
	largest_amount = 0.0

	rcp_ing = conn.execute("SELECT recipe_ingredient from RECIPE WHERE recipe_ingredient LIKE ? OR recipe_ingredient LIKE ?", ('%'+ingr+'%', '%'+ingr_s+'%'))

	for row in rcp_ing:
		row = ''.join(row)
		items = row.split(" + ")
		for item in items:
			item = item.lower()
			item = "  " + item + " "	#add spacing at end and beginning cuz convenience
			if ingr in item or ingr_s in item:
				#print(item)
				if any(x in item for x in unwanted):	#e.g. unwanted = ["noodles"], query = "egg": don't want egg noodles
					continue

				if any(x in item for x in wanted):		#e.g. wanted = ["cups"], query = "whole milk": want x cups whole milk

					if "pound" in item:
						info = amount_and_chosen_recipe(item,"pound",largest_amount,chosen_recipe,row,16)
						largest_amount = info[0]
						chosen_recipe = info[1]

					elif "lb" in item:
						info = amount_and_chosen_recipe(item,"lb",largest_amount,chosen_recipe,row,16)
						largest_amount = info[0]
						chosen_recipe = info[1]

					elif "ounce" in item:
						info = amount_and_chosen_recipe(item,"ounce",largest_amount,chosen_recipe,row,1)
						largest_amount = info[0]
						chosen_recipe = info[1]
					
					elif "quart" in item:
						info = amount_and_chosen_recipe(item,"quart",largest_amount,chosen_recipe,row,4)
						largest_amount = info[0]
						chosen_recipe = info[1]

					elif "cup" in item:
						info = amount_and_chosen_recipe(item,"cup",largest_amount,chosen_recipe,row,1)
						largest_amount = info[0]
						chosen_recipe = info[1]
					else:
						info = amount_and_chosen_recipe(item,item[(len(item)-5):],largest_amount,chosen_recipe,row,1)
						largest_amount = info[0]
						chosen_recipe = info[1]
					
	rcp_recom = conn.execute("SELECT recipe_id from RECIPE WHERE recipe_ingredient = ? limit 1", (chosen_recipe,))
	data = rcp_recom.fetchall()	#https://stackoverflow.com/questions/2440147/how-to-check-the-existence-of-a-row-in-sqlite-with-python
	if len(data)==0:	#if rcp_recom is an empty cursor
		return " "
	else:
		rcp_id = ''.join(map(str,zip(*data)[0])) #turn it into string type
		return rcp_id

#Return chosen recipe and amount for largest amount algorithm
def amount_and_chosen_recipe(item, unit,largest_amount,chosen_recipe,row,factor):
	amount = ""

	if item.count(unit) > 1:		#if more than one instance of unit occuring in string, index is very end of string
		index = len(item)	
	else:
		index = item.find(unit)
	while True:
		index = index - 1			#Go backwards from the index of where you found 'quart' to find the amount
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
			if item[index+1]=="/":
				amount = str(float(item[index]) / float(item[index+2])) + amount
			elif item[index+1]==".":
				amount = str(float(item[index]) + float(amount)/(10**len(amount)))
			elif item[index+2].isdigit():
				if item[index+3]=="/":
					amount = str(float(item[index]) + float(amount))
				elif item[index+1]==" ":
					amount = str(float(item[index]) * float(amount))
				elif item[index+1]=="-":
					amount = amount
				else:
					amount = item[index] + amount
			elif item[index+1].isdigit() and item[index+2]=="-" and item[index+3].isdigit():
				amount = amount
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
						if con in item:			#e.g. 2 cans (14 oz.) of ...    2 (14 oz) cans of ...
							if item[item.find(con)-2].isdigit():
								amount = str(float(amount)*float(item[item.find(con)-2]))
							elif item[item.find(con)-2] == ")":
								if item[index]=="(" and item[index-2].isdigit():
									amount = str(float(amount)*float(item[index-2]))
							elif "x" in item[:index] and any(char.isdigit() for char in item[:index]):
								multi = [s for s in item[:index] if s.isdigit()]
								multi = ''.join(multi)
								amount = str(float(amount)*float(multi))
					if float(amount)*factor > largest_amount:	#x4 factor converts to quart to cup scale (if unit is quart)
						largest_amount = float(amount)*factor
						chosen_recipe = row
					break
		if index <= 0:
			break

	return (largest_amount,chosen_recipe)


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def recom_alg(ing, conn, wanted, unwanted):

	ingr_s = " " + ing + "s "
	ingr = " " + ing + " "
	rcp_ing = conn.execute("SELECT recipe_ingredient from RECIPE WHERE recipe_ingredient LIKE ? OR recipe_ingredient LIKE ?", ('%'+ingr+'%', '%'+ingr_s+'%'))
	local_data = rcp_ing.fetchall()
	
	if len(local_data)==0:	#if rcp_ing is an empty cursor (the query does not exists in the ingredient lists)
		rcp_title = conn.execute("SELECT recipe_title from RECIPE WHERE recipe_title LIKE ?", ('%'+ing+'%',))
		local_data_2 = rcp_title.fetchall()
		
		if len(local_data_2)==0: #if rcp_title is an empty cursor (the query does not exists in the recipe title lists)
			
			recom_recipe = "omelet0"
			return recom_recipe

		else:

			recom_recipe = local_data_2[0][0] #Get the first recipe TITLE in which the ing is in recipe title
			recom_rcp_id = conn.execute("SELECT recipe_id from RECIPE WHERE recipe_title = ? limit 1",(recom_recipe,))
			recom_recipe = recom_rcp_id.fetchone()[0]
			return recom_recipe

	else:
		
		recom_recipe = largest_amount_alg(ing,conn,unwanted,wanted)
		
		if recom_recipe == " ":
			recom_recipe = "omelet0"
			return recom_recipe
		else:
			return recom_recipe