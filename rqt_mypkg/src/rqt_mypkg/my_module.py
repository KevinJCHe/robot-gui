import os
import rospy
import rospkg
import sqlite3
import re
import urllib2
import requests
import recommendation_algorithm
import result_algorithm

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget
from PyQt4 import QtGui, QtCore
from itertools import chain
from datetime import datetime
from collections import Counter

#Global Variables
breadcrumb = []
unique_key = 0
header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

#Get database
database_path = '/home/turtlebot22/Summer2017/RecipeAPI/recipe.db'
conn = sqlite3.connect(database_path)

db_path = '/home/turtlebot22/Summer2017/src/rqt_mypkg/src/rqt_mypkg/User_Selected_Recipe.db'
conn_2 = sqlite3.connect(db_path)

#Page IDs for breadcrumb
Main_Page_ID = 1

Keyboard_Page_ID = 11
Voice_Page_ID = 12
Food_Recipe_Page_ID = 13
Textual_Page_ID = 14

Food_Page_ID = 21
Recipe_Page_ID = 22

Produce_Page_ID = 31
Meat_Page_ID = 32
Pantry_Page_ID = 33
Dairy_Page_ID = 34

Fruit_Page_ID = 41


class MyPlugin(Plugin):	#Why is it Plugin? cuz in plugin.xml, the base class is rqt_qui_py::Plugin.........yea can't find much on that

	def __init__(self, context):	#Why context? I have no freakin clue
		super(MyPlugin, self).__init__(context) #inherits the bound __init__ method from parent's class. MyPlugin is the child class in this case
	# Give QObjects reasonable names
		self.setObjectName('MyPlugin')
	# Process standalone plugin command-line arguments
		from argparse import ArgumentParser
		parser = ArgumentParser()
	# Add argument(s) to the parser.
		parser.add_argument("-q", "--quiet", action="store_true",
		              dest="quiet",
		              help="Put plugin in silent mode")
		args, unknowns = parser.parse_known_args(context.argv())
		if not args.quiet:
		    print 'arguments: ', args
		    print 'unknowns: ', unknowns

		self.main_page(context)

	#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	
	#Set Events and Functions

	def BackButtonClicked(self, context):						#Back button click evvent
		context.remove_widget(self._widget)
		prev_page_ID = breadcrumb[-2]
		breadcrumb.remove(breadcrumb[-1])
		breadcrumb.remove(breadcrumb[-1])	#Since you took away brc[-1], brc[-2] becomes brc[-1]
		if prev_page_ID == Main_Page_ID:
			self.main_page(context)
		elif prev_page_ID == Keyboard_Page_ID:
			self.keyboard_page(context)
		elif prev_page_ID == Food_Recipe_Page_ID:
			self.food_recipe_page(context)
		elif prev_page_ID == Food_Page_ID:
			self.food_page(context)
		elif prev_page_ID == Recipe_Page_ID:
			self.recipe_page(context)
		elif prev_page_ID == Produce_Page_ID:
			self.produce_page(context)
		elif prev_page_ID == Dairy_Page_ID:
			self.dairy_page(context)
		elif prev_page_ID == Meat_Page_ID:
			self.meat_page(context)
		elif prev_page_ID == Fruit_Page_ID:
			self.fruit_page(context)
		else:
			self.main_page(context)
		

	def VisualButtonClicked(self, context):						#Visual button click event
		context.remove_widget(self._widget)
		self.food_recipe_page(context)

	def VoiceButtonClicked(self, context):						#Voice button click event
		print("Voice button Clicked")

	def TextualButtonClicked(self, context):					#Textual button click event
		print("Textual button Clicked")

	def KeyboardButtonClicked(self, context):					#Keyboard button click event
		context.remove_widget(self._widget)
		self.keyboard_page(context)

	def FoodButtonClicked(self, context):						#Food button click event
		context.remove_widget(self._widget)
		self.food_page(context)

	def RecipeButtonClicked(self, context):						#Recipe button click event
		context.remove_widget(self._widget)
		self.recipe_page(context)

	def RecipeResultButtonClicked(self, context, recipe_id):	#Recipe Result button click event
		context.remove_widget(self._widget)
		self.recipe_result_page(context, recipe_id)

	def MeatButtonClicked(self, context):						#Meat button click event
		context.remove_widget(self._widget)
		self.meat_page(context)

	def DairyButtonClicked(self, context):						#Dairy button click event
		context.remove_widget(self._widget)
		self.dairy_page(context)

	def ProduceButtonClicked(self, context):					#Produce button click event
		context.remove_widget(self._widget)
		self.produce_page(context)

	def PantryButtonClicked(self, context):						#Pantry button click event
		print("Pantry button clicked")

	def VegetableButtonClicked(self, context):					#Vegetable button click event
		print("Vegetable button Clicked")

	def FruitButtonClicked(self, context):						#Fruit button click event
		context.remove_widget(self._widget)
		self.fruit_page(context)

	def RedButtonClicked(self, context, page,color):			#Red button click event
		context.remove_widget(self._widget)
		self.result_page(context,color,page,'visual')

	def YellowButtonClicked(self, context,page,color):			#Yellow button click event
		context.remove_widget(self._widget)
		self.result_page(context,color,page,'visual')

	def OrangeButtonClicked(self, context,page,color):			#Orange button click event
		context.remove_widget(self._widget)
		self.result_page(context,color,page,'visual')

	def GreenButtonClicked(self, context,page,color):			#Green button click event
		context.remove_widget(self._widget)
		self.result_page(context,color,page,'visual')

	def Purple_BlackButtonClicked(self, context,page,color):	#Purple_Black button click event
		context.remove_widget(self._widget)
		self.result_page(context,color,page,'visual')

	def Blue_PinkButtonClicked(self, context,page,color):		#Blue_Pink button click event
		context.remove_widget(self._widget)
		self.result_page(context,color,page,'visual')

	def EggButtonClicked(self, context, page, food):			#Egg button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def MilkButtonClicked(self, context,page,food):				#Milk button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def ButterButtonClicked(self, context,page,food):			#Butter button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def CheeseButtonClicked(self, context,page,food):			#Cheese button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def YogurtButtonClicked(self, context,page,food):			#Yogurt button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def BeefButtonClicked(self, context, page, food):			#Beef button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def PorkButtonClicked(self, context,page,food):				#Pork button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def FishButtonClicked(self, context,page,food):				#Fish button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def ChickenButtonClicked(self, context,page,food):			#Chicken button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def CrustaceanButtonClicked(self, context,page,food):		#Crustacean button click event
		context.remove_widget(self._widget)
		self.result_page(context,food,page,'visual')

	def KeyboardEntered(self,context):							#Keyboard Entered event
		text = self._widget.Keyboard.text()
		context.remove_widget(self._widget)
		self.result_page(context,text,'keyboard','keyboard')

	def KeywordEntered(self,context,food_category):				#Keyword Entered event
		text = self._widget.Keyword_Search.text()
		print(food_category + ":" + text)

	def Buy_RecipeButtonClicked(self,recipe_id):
	#SAVE DATA FOR MACHINE LEARNING ALGORITHM
		time_of_day = str(datetime.now())
		recipe_title = conn.execute("SELECT recipe_title from RECIPE WHERE recipe_id = ? limit 1",(recipe_id,)) 
		#YOU MUST PERFORM THE SQL COMMAND AGAIN, OR ELSE IT WONT WORK!!!! 
		conn_2.execute("INSERT INTO USER_RECOM_SELECTION_DATA (recipe_title, time_of_day) VALUES (?,?)", (recipe_title.fetchone()[0],time_of_day))
		conn_2.commit()

	#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


	#GET PAGES
	def new_page(self, context, ui_name, unique_num):
		global unique_key
		unique_key = unique_key + 1 #Cuz widget object name must be unique everytime widget is opened, this ensures that it will be
		self._widget = QWidget()
		ui_file = os.path.join(rospkg.RosPack().get_path('rqt_mypkg'), 'resource', ui_name)
		loadUi(ui_file, self._widget)
		self._widget.setObjectName('Ui'+ unique_num)
		if context.serial_number() > 1:
		    self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
		context.add_widget(self._widget)


	def main_page(self,context):
	#Get Main Page
		ui_name = 'MyPlugin.ui'
		unique_num = 'a' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Main_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 70px;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
				max-width: 400px;
			}
		""")
	#Connect Slots to Signals
		self._widget.Visual.clicked.connect(lambda: self.VisualButtonClicked(context)) #Visual button click event
		self._widget.Voice.clicked.connect(lambda: self.VoiceButtonClicked(context)) #Voice button click event
		self._widget.Textual.clicked.connect(lambda: self.TextualButtonClicked(context)) #Textual button click event
		self._widget.Keyboard.clicked.connect(lambda: self.KeyboardButtonClicked(context)) #Keyboard button click event


	def food_recipe_page(self, context):
	#Get Food / Recipe Page
		ui_name = 'Food_Recipe.ui'
		unique_num = 'b' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Food_Recipe_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 70px;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
				max-width: 400px;
			}
			QPushButton#Back{
				font-size: 60px;
				color: orange;
			}
		""")
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Food.clicked.connect(lambda: self.FoodButtonClicked(context)) #Food button click event
		self._widget.Recipe.clicked.connect(lambda: self.RecipeButtonClicked(context)) #Recipe button click event


	def food_page(self, context):
	#Get Food Page
		ui_name = 'Food.ui'
		unique_num = 'c' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Food_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 70px;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
				max-width: 400px;
			}
			QPushButton#Back{
				font-size: 60px;
				color: orange;
			}
		""")
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Meat.clicked.connect(lambda: self.MeatButtonClicked(context)) #Meat button click event
		self._widget.Dairy.clicked.connect(lambda: self.DairyButtonClicked(context)) #Dairy button click event
		self._widget.Produce.clicked.connect(lambda: self.ProduceButtonClicked(context)) #Produce button click event
		self._widget.Pantry.clicked.connect(lambda: self.PantryButtonClicked(context)) #Pantry button click event


	def recipe_page(self, context):
	#Get Recipe Page
		ui_name = 'Recipe.ui'
		unique_num = 'd' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Recipe_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				font-size: 35px;
				text-align: left;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
				max-width: 400px;
			}
			QPushButton#Back{
				font-size: 60px;
				color: orange;
				text-align: center;			
			}
			QLabel#Recommended, QLabel#Prev_Freq{
				font-size: 40px;
				font-weight: bold;
				letter-spacing: 2px;
				color: black;
				border: 3px solid black;
				max-height: 50px;
			}
		""")
	#Set Contents Margin
		self._widget.THE_ROW.setContentsMargins(15, 75, 15, 150)
	#Retrieve recipe data
		prev_selected_recipes = recommendation_algorithm.get_prev_selected_recipes(self, conn_2)
		
		#Prev Recipe
		prev_rcp_id = conn.execute("SELECT recipe_id from RECIPE WHERE recipe_title = ? limit 1",(prev_selected_recipes[-1],))
		prev_recipe = prev_rcp_id.fetchone()[0]
		
		#Freq Recipe
		most_common_recipe = [word for word, word_count in Counter(prev_selected_recipes).most_common(1)]
		frq_rcp_id = conn.execute("SELECT recipe_id from RECIPE WHERE recipe_title = ? limit 1",(most_common_recipe[0],))
		freq_recipe = frq_rcp_id.fetchone()[0]
		
		#Recom 1
		recom_1_rcp_id = conn.execute("SELECT recipe_id from RECIPE WHERE rowid = ? limit 1",(48,))
		recom_recipe_1 = recom_1_rcp_id.fetchone()[0]
		
		#Recom 2
		recom_2_rcp_id = conn.execute("SELECT recipe_id from RECIPE WHERE rowid = ? limit 1",(91,))
		recom_recipe_2 = recom_2_rcp_id.fetchone()[0]
		
		#Chosen Recipes
		chosen_recipes = [prev_recipe,freq_recipe,recom_recipe_1,recom_recipe_2]
	#Input Recipe Info
		layout_1 = self._widget.Recipe_Grid_1
		layout_2 = self._widget.Recipe_Grid_2
		widgets_1 = (layout_1.itemAt(i).widget() for i in range(layout_1.count())) 
		widgets_2 = (layout_2.itemAt(i).widget() for i in range(layout_2.count())) 
		widgets = chain(widgets_1, widgets_2)
		r = 0
		for widget in widgets:		#E.g. widget = self._widget.Recipe_Title_1
			name = widget.objectName()
			if "Recipe_Title_" in name:
			#Set Recipe Names
				rcp_name = conn.execute("SELECT recipe_title from RECIPE WHERE recipe_id = ? limit 1",(chosen_recipes[r],))
				recipe_name = rcp_name.fetchone()[0]
				widget.setText(recipe_name)	
			#MAKE SURE TEXT FITS INTO BUTTON
				text = widget.text()
				number_of_char = len(text)
				#APPROXIMATE!	 - 21 characters for "Western Omelet Breakfast Sandwich...", width: 400, font-size:35, font-family: Ubuntu
				if number_of_char > 20:
					indices =[]
					p = number_of_char / 20
					for s in range(1,p+1):
						indices.append(20*s)
					for s in indices:
						while text[s] != " ":	#If text[20] is not a space, go backwards until you do find it
							s = s - 1
						text = text[:s] + '\n' + text[s:].strip()	#insert '\n' at the space position
					widget.setText(text)
			elif "Recipe_Pic_" in name:
			#Place the Recipe Images
				recipe_image_url = conn.execute("SELECT recipe_image_url from RECIPE WHERE recipe_id = ? limit 1",(chosen_recipes[r],))
				rcp_img_url = recipe_image_url.fetchone()[0] #rcp_img_url is a tuple
				data = urllib2.urlopen(urllib2.Request(rcp_img_url,headers=header)).read()
				pixmap = QtGui.QPixmap()
				pixmap.loadFromData(data)
				pixmapScaled = pixmap.scaledToHeight(125)
				widget.setPixmap(pixmapScaled)
				widget.setAlignment(QtCore.Qt.AlignCenter)
				r = r + 1
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Recipe_Title_1.clicked.connect(lambda: self.RecipeResultButtonClicked(context,chosen_recipes[0])) #Recipe Result button click event
		self._widget.Recipe_Title_2.clicked.connect(lambda: self.RecipeResultButtonClicked(context,chosen_recipes[1])) #Recipe Result button click event
		self._widget.Recipe_Title_3.clicked.connect(lambda: self.RecipeResultButtonClicked(context,chosen_recipes[2])) #Recipe Result button click event
		self._widget.Recipe_Title_4.clicked.connect(lambda: self.RecipeResultButtonClicked(context,chosen_recipes[3])) #Recipe Result button click event


	def recipe_result_page(self, context, recipe_id):
	#Get Produce Page
		ui_name = 'Recipe_Result.ui'
		unique_num = 'p' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(90)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-weight: bold;
				letter-spacing: 2px;
			}
			QPushButton#Back{
				color: orange;
				max-width: 400px;
				font-size: 60px;
			}
			QPushButton#Buy_Recipe{
				color: red;
				width: 100%;
				font-size: 40px;
			}
			QLabel#Recipe_Title{
				font-size: 40px;
				font-weight: bold;
				letter-spacing: 2px;
				color: black;
				text-align: center;
			}
			QLabel#Recipe_Ingredient{
				font-size: 25px;
				font-weight: bold;
				letter-spacing: 2px;
				background-color: white;
				color: blue;
			}
		""")
	#Set Contents Margin/Alignment
		self._widget.Recipe_Result_Column.setContentsMargins(50, 100, 50, 100)
		self._widget.Recipe_Result_Column.setAlignment(QtCore.Qt.AlignCenter)
	#Input The Recipe Info
		#Recipe Pic
		recipe_image_url = conn.execute("SELECT recipe_image_url from RECIPE WHERE recipe_id = ? limit 1",(recipe_id,))
		rcp_img_url = recipe_image_url.fetchone()[0] #rcp_img_url is a tuple
		data = urllib2.urlopen(urllib2.Request(rcp_img_url,headers=header)).read()
		pixmap = QtGui.QPixmap()
		pixmap.loadFromData(data)
		pixmapScaled = pixmap.scaledToHeight(300)
		self._widget.Recipe_Picture.setPixmap(pixmapScaled)
		self._widget.Recipe_Picture.setAlignment(QtCore.Qt.AlignCenter)
		#Recipe Title
		recipe_title = conn.execute("SELECT recipe_title from RECIPE WHERE recipe_id = ? limit 1",(recipe_id,))
		rcp_title = recipe_title.fetchone()[0]
		s = 60
		if len(rcp_title) > 60:	#Make sure Recipe Title fits within Widget width
			while rcp_title[s] != " ":
				s = s - 1
			rcp_title = rcp_title[:s] + '\n' + rcp_title[s:].strip()
		self._widget.Recipe_Title.setText(rcp_title)
		self._widget.Recipe_Title.setAlignment(QtCore.Qt.AlignCenter)
		#Recipe Ingredient
		recipe_ingredient = conn.execute("SELECT recipe_ingredient from RECIPE WHERE recipe_id = ? limit 1",(recipe_id,))
		rcp_ingr = recipe_ingredient.fetchone()[0]
		rcp_ingr = rcp_ingr.replace(" + ", "\n")
		self._widget.Recipe_Ingredient.setText(rcp_ingr)
		self._widget.Recipe_Ingredient.setAlignment(QtCore.Qt.AlignLeft)
	#MAKE SURE TEXT FITS INSIDE THE Recipe Ingredient LABEL
		ing_list = rcp_ingr.split("\n")
		i = 0
		s = 60
		fits = True
		for item in ing_list:
			number_of_char = len(item)
			#APPROXIMATE!	 - 63 characters for "Spicy Pumpkin Soup -- 5 cups of.......", width: 750, font-size:25, font-family: Ubuntu
			if number_of_char > 60:
				fits = False
				while ing_list[i][s] != " ":
					s = s - 1
				ing_list[i] = ing_list[i][:s] + '\n' + ing_list[i][s:].strip()
			i = i + 1
		if fits == False:
			rcp_ingr = '\n'.join(ing_list)
			self._widget.Recipe_Ingredient.setText(rcp_ingr)
	#Make Recipe Ingredient scrollable if too long
		scroll = QtGui.QScrollArea()	#In PyQt4 It's QtGui instead of QtWidgets
		scroll.setWidgetResizable(True)
		scroll.setFixedHeight(300)
		scroll.setWidget(self._widget.Recipe_Ingredient)
		self._widget.Recipe_Result_Row.addWidget(scroll)
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Buy_Recipe.clicked.connect(lambda: self.Buy_RecipeButtonClicked(recipe_id)) #Buy_Recipe button click event


	def produce_page(self, context):
	#Get Produce Page
		ui_name = 'Produce.ui'
		unique_num = 'e' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Produce_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 70px;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
				max-width: 400px;
			}
			QPushButton#Back{
				font-size: 60px;
				color: orange;
			}
		""")
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Vegetable.clicked.connect(lambda: self.VegetableButtonClicked(context)) #Vegetable button click event
		self._widget.Fruit.clicked.connect(lambda: self.FruitButtonClicked(context)) #Fruit button click event


	def fruit_page(self, context):
		page = "fruit"
	#Get Produce Page
		ui_name = 'Fruit.ui'
		unique_num = 'm' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Fruit_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				border: 3px solid black;
				text-align: center;
				font-size: 70px;
				font-weight: bold;
				letter-spacing: 2px;
				color: white;
				max-width: 400px;
				height: 200px;
			}
			QPushButton#Back{
				font-size: 60px;
				color: orange;
				background-color: white;
				height: 75px;
				width: 250px;
			}
			QPushButton#Red{
				background-color: red;
			}
			QPushButton#Green{
				background-color: green;
			}
			QPushButton#Blue_Pink{
				background-color: pink;
				color: blue;
			}
			QPushButton#Orange{
				background-color: orange;
			}
			QPushButton#Yellow{
				background-color: yellow;
			}
			QPushButton#Purple_Black{
				background-color: purple;
				color: black;
				font-size: 50px;
			}
			QLabel{
				font-size: 60px;
				font-weight: bold;
				letter-spacing: 2px;
				color: black;
				max-height: 50px;
			}
			QLineEdit#Keyword_Search{
				background-color: white;
				border: 3px solid black;
				font-size: 40px;
				font-weight: bold;
				letter-spacing: 2px;
				color: black;
				height: 50px;
			}
		""")
	#Set Content Alignment and Margins
		self._widget.Keyword_Search.setContentsMargins(600, 0, 0, 0)
	#Put placeholder text
		self._widget.Keyword_Search.setPlaceholderText("Keyword Type Here") 
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Keyword_Search.editingFinished.connect(lambda: self.KeywordEntered(context, 'fruit')) #Keyword Enter event
		self._widget.Red.clicked.connect(lambda: self.RedButtonClicked(context,page,'red')) #red bupage,tton click event
		self._widget.Purple_Black.clicked.connect(lambda: self.Purple_BlackButtonClicked(context,page,'purple_black')) #purple_black button click event
		self._widget.Green.clicked.connect(lambda: self.GreenButtonClicked(context,page,'green')) #green button click event
		self._widget.Yellow.clicked.connect(lambda: self.YellowButtonClicked(context,page,'yellow')) #yellow button click event
		self._widget.Orange.clicked.connect(lambda: self.OrangeButtonClicked(context,page,'orange')) #Orange button click event
		self._widget.Blue_Pink.clicked.connect(lambda: self.Blue_PinkButtonClicked(context,page,'blue_pink')) #Blue_Pink button click event
		


	def dairy_page(self, context):
		page = "dairy"
	#Get Dairy Page
		ui_name = 'Dairy.ui'
		unique_num = 'f' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Dairy_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 70px;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
				max-width: 400px;
			}
			QPushButton#Back{
				font-size: 60px;
				color: orange;
			}
		""")
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Egg.clicked.connect(lambda: self.EggButtonClicked(context,page,'egg')) #Egg button click event
		self._widget.Milk.clicked.connect(lambda: self.MilkButtonClicked(context,page,'milk')) #Milk button click event
		self._widget.Butter.clicked.connect(lambda: self.ButterButtonClicked(context,page,'butter')) #Butter button click event
		self._widget.Cheese.clicked.connect(lambda: self.CheeseButtonClicked(context,page,'cheese')) #Cheese button click event
		self._widget.Yogurt.clicked.connect(lambda: self.YogurtButtonClicked(context,page,'yogurt')) #Yogurt button click event


	def meat_page(self, context):
		page = "meat"
	#Get Dairy Page
		ui_name = 'Meat.ui'
		unique_num = 'l' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Meat_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 70px;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
				max-width: 400px;
			}
			QPushButton#Back{
				font-size: 60px;
				color: orange;
			}
		""")
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Beef.clicked.connect(lambda: self.BeefButtonClicked(context,page,'beef')) #Beef button click event
		self._widget.Pork.clicked.connect(lambda: self.PorkButtonClicked(context,page,'pork')) #Pork button click event
		self._widget.Fish.clicked.connect(lambda: self.FishButtonClicked(context,page,'fish')) #Fish button click event
		self._widget.Chicken.clicked.connect(lambda: self.ChickenButtonClicked(context,page,'chicken')) #Chicken button click event
		self._widget.Crustacean.clicked.connect(lambda: self.CrustaceanButtonClicked(context,page,'crustacean')) #Crustacean button click event


	def keyboard_page(self,context):
	#Get Keyboards Page
		ui_name = 'Keyboard.ui'
		unique_num = 'g' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(Keyboard_Page_ID)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QLineEdit{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 40px;
				font-weight: bold;
				letter-spacing: 2px;
				color: red;
			}
			QPushButton#Back{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-size: 60px;
				font-weight: bold;
				letter-spacing: 2px;
				color: orange;
			}
		""")
	#Put placeholder text
		self._widget.Keyboard.setPlaceholderText("Type Here") 
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event
		self._widget.Keyboard.editingFinished.connect(lambda: self.KeyboardEntered(context)) #Keyboard Enter event


	def result_page(self, context, query, page, source_of_query):
	#Get Produce Page
		ui_name = 'Result.ui'
		unique_num = 'i' + str(unique_key)
		self.new_page(context, ui_name, unique_num)
	#Add to breadcrumb
		breadcrumb.append(100)
	#Set Style Sheet
		self._widget.setStyleSheet("""
			QWidget{
				background-color: rgb(10,50,90);
			}
			QPushButton#Back{
				background-color: white;
				border: 3px solid black;
				text-align: center;
				font-weight: bold;
				letter-spacing: 2px;
				max-width: 400px;
				font-size: 60px;
				color: orange;
			}
			QPushButton#Pic_Result_1, QPushButton#Pic_Result_2, QPushButton#Pic_Result_3{
				width: 400px;
				height: 250px;
			} 
			QLabel{
				font-size: 40px;
				font-weight: bold;
				letter-spacing: 2px;
				color: black;
				text-align:center;
			}
			QLabel#Result{
				font-size: 70px;
			}
			QLabel#Result_1_Label, QLabel#Result_2_Label, QLabel#Result_3_Label{
				text-transform: uppercase;
			}
		""")
	#Set Content Alignment
		self._widget.Vertical_Column.setAlignment(QtCore.Qt.AlignCenter)
		self._widget.Result.setAlignment(QtCore.Qt.AlignCenter)
		self._widget.Recommended_Recipe.setAlignment(QtCore.Qt.AlignCenter)
		self._widget.Result_1_Label.setAlignment(QtCore.Qt.AlignCenter)
		self._widget.Result_2_Label.setAlignment(QtCore.Qt.AlignCenter)
		self._widget.Result_3_Label.setAlignment(QtCore.Qt.AlignCenter)
	#Result Algorithm
		result_algorithm.result_alg(self, context, conn, query, page, source_of_query)
	#Connect Slots to Signals
		self._widget.Back.clicked.connect(lambda: self.BackButtonClicked(context)) #Back button click event


	#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


	def shutdown_plugin(self):
		# TODO unregister all publishers here
		conn.close()
		conn_2.close()

	def save_settings(self, plugin_settings, instance_settings):
		# TODO save intrinsic configuration, usually using:
		# instance_settings.set_value(k, v)
		pass

	def restore_settings(self, plugin_settings, instance_settings):
		# TODO restore intrinsic configuration, usually using:
		# v = instance_settings.value(k)
		pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog