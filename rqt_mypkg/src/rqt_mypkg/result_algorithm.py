import os
import rospy
import rospkg
import sqlite3
import urllib2
import requests
import json
import re
import recommendation_algorithm

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget
from PyQt4 import QtGui, QtCore

header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

def result_alg(self, context, conn, query, page, source_of_query):
	if source_of_query == "visual":

		if page == "dairy":

			if query == 'egg':

				#Set up variables
				result_item = ["white "+query,'roe','quail '+query]
				wanted=[" "]
				unwanted =["noodle"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'milk':

				#Set up variables
				result_item = ["whole "+query,"chocolate "+query,'soy '+query]
				wanted=["cup","quart"]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'butter':

				#Set up variables
				result_item = ["peanut "+query,"unsalted "+query,'margarine']
				wanted=["cup"]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'cheese':

				#Set up variables
				result_item = ["cheddar "+query,"parmesan "+query,"swiss "+query]
				wanted=["ounce","lb"]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'yogurt':

				#Set up variables
				result_item = [query,"greek "+query,"frozen "+query]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

		elif page == "fruit":

			if query == 'red':

				#Set up variables
				result_item = ["apple","strawberry","watermelon"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'purple_black':

				#Set up variables
				result_item = ["grape","plum","cherry"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'green':

				#Set up variables
				result_item = ["kiwi","lime","avocado"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'yellow':

				#Set up variables
				result_item = ["mango","banana","lemon"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'orange':

				#Set up variables
				result_item = ["orange","clementine","cantaloupe"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'blue_pink':

				#Set up variables
				result_item = ["blueberry","peach","grapefruit"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

		elif page == "meat":

			if query == 'beef':

				#Set up variables
				result_item = ["beef rib","ground beef","steak"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'pork':

				#Set up variables
				result_item = ["pork loin","bacon","ham"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'fish':

				#Set up variables
				result_item = ["salmon","tuna","halibut"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'chicken':

				#Set up variables
				result_item = ["chicken breast","drumstick","chicken wing"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)

			elif query == 'crustacean':

				#Set up variables
				result_item = ["shrimp","crab","lobster"]
				wanted=[" "]
				unwanted =["zzzzzz"]
				set_result_recom(self,context,conn,wanted,unwanted,result_item)


	elif source_of_query == "keyboard":
		#Set up variables
		result_item = [query,query,query]
		wanted=[" "]
		unwanted =["zzzzzz"]
		set_result_recom(self,context,conn,wanted,unwanted,result_item)

	elif source_of_query == "textual":
		print("textual")
	elif source_of_query == "voice":
		print("voice")

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#Input Recipe Recommendation Pic and Click Event
def set_result_recom(self,context,conn,wanted,unwanted,result_item):

	#RESULT SET TEXT
	self._widget.Result_1_Label.setText(result_item[0])
	self._widget.Result_2_Label.setText(result_item[1])
	self._widget.Result_3_Label.setText(result_item[2])

	#RECIPE RECOMMENDATION ALGORITHM
	rcp_id_1 = recommendation_algorithm.recom_alg(result_item[0], conn, wanted, unwanted)
	rcp_id_2 = recommendation_algorithm.recom_alg(result_item[1], conn, wanted, unwanted)
	rcp_id_3 = recommendation_algorithm.recom_alg(result_item[2], conn, wanted, unwanted)
	rcp_id = [rcp_id_1, rcp_id_2, rcp_id_3]

	#Recipe Recommendation
	layout = self._widget.Recipe_Row
	widgets = (layout.itemAt(i).widget() for i in range(layout.count())) 
	r = 0
	for widget in widgets:		#E.g. widget = self._widget.Recipe_Title_1
		
		#GET IMAGES DIRECTLY FROM IMAGE URL
		recipe_image_url = conn.execute("SELECT recipe_image_url from RECIPE WHERE recipe_id = ? limit 1",(rcp_id[r],))
		rcp_img_url = recipe_image_url.fetchone()[0] #rcp_img_url is a tuple
		data = urllib2.urlopen(urllib2.Request(rcp_img_url,headers=header)).read()
		icon = QtGui.QIcon()
		pixmap = QtGui.QPixmap()
		pixmap.loadFromData(data)
		icon.addPixmap(pixmap)
		widget.setIcon(icon)
		widget.setIconSize(QtCore.QSize(200,150))

		r = r + 1

	#Connect Slots to Signals
	self._widget.Recommended_Recipe_Pic_1.clicked.connect(lambda: self.RecipeResultButtonClicked(context,rcp_id[0])) #Recipe Result button click event
	self._widget.Recommended_Recipe_Pic_2.clicked.connect(lambda: self.RecipeResultButtonClicked(context,rcp_id[1])) 
	self._widget.Recommended_Recipe_Pic_3.clicked.connect(lambda: self.RecipeResultButtonClicked(context,rcp_id[2])) 