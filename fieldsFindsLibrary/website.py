#!/usr/bin/env python3

#Import field and find library objects
from .geoObjects import Field, Find, MapArea
from .webObjects import AreaDropDown, FormList, Status
from .database import DbFieldsFinds

#Import Jinja2 to render website
from jinja2 import Environment, FileSystemLoader

#Class list in file
__all__ = ['WebsiteFieldsFinds']

class WebsiteFieldsFinds(object):
	"""The Fields and Finds Website
	
	The WebsiteFieldFinds class contains all information needed to:
	1) Load and submit data from database
	2) Perform any actions - filter or add data
	3) Generate the SVG
	4) Generate the webpage using a Jinja2 html template
	
	"""
	
	def __init__(self,params):
		"""Initialise object
		
		Keyword arguments:
		params -- a dictonary of parameters submitted from browser
		"""
		
		#Get Website Templates
		self._env = Environment(loader=FileSystemLoader('templates'))
		self._mainTemplate = self._env.get_template('maintemplate.html')
		
		#Style names to pass to SVG
		self._findStyle = 'find'
		self._fieldStyle = 'field'
		
		#Setup DB Connection
		self._db = DbFieldsFinds()
		
		#Map Objects
		self._mapArea = None	

		#Web Objects
		self._areaDropDown = None
		self._cropDropDown = None
		self._classDropDown = None
		self._ownerDropDown = None
		self._areaDelList = None
		self._findList = None
		self._fieldList = None
		
		#Status - default empty line
		self._status = '<br>'
		
		#Parameters
		self._params = params
			
		#Param interpretation
		if 'Action' in self._params:
			self._action = self._params['Action'].value
		else:
			self._action = None
		
		if 'MapArea' in self._params:
			self._mapAreaName = self._params['MapArea'].value
		else:
			self._mapAreaName = 'Default'
			
		if 'FilterClass' in self._params:
			self._filterClass = self._params['FilterClass'].value
			self._status = Status('Filter Applied','Class = ' + self._filterClass)
		else:
			self._filterClass = None
					

	
	def run(self):
		"""Run all actions requested and generate the website"""
	
		self._db.openConnection()
		self._performActions()
		fields = self._db.getFields(self._mapArea.areaId)
		finds = self._db.getFinds(self._mapArea.areaId,self._filterClass)
		self._mapArea.addFields(fields,self._fieldStyle)
		self._mapArea.addFinds(finds,self._findStyle)
		self._genWebObjects()
		self._db.closeConnection()
	
	def __str__(self):
		"""return rendered website as string object"""
		
		assert self._mapArea != None #Check map created
		assert self._areaDropDown != None
		svgMap = self._mapArea.renderMap('100%','100%')
		svgInfo = self._mapArea.renderInfo(300,500)
		return self._mainTemplate.render(
										svgMap = svgMap,
										svgInfo = svgInfo,
										currentMap = self._mapAreaName,
										mapAreas = self._areaDropDown,
										cropList = self._cropDropDown,
										classList = self._classDropDown,
										ownerList = self._ownerDropDown,
										jsMapAreaName = self._mapAreaName,
										status = self._status,
										maxX = self._mapArea.maxX,
										maxY = self._mapArea.maxY,
										maxXl1 = self._mapArea.maxX-1,
										maxYl1 = self._mapArea.maxY-1,
										delAreaList = self._areaDelList,
										findList = self._findList,
										fieldList = self._fieldList
										)
		
	def _genWebObjects(self):
		"""Generate webpage dropdowns and lists"""
		
		#Get list of maps
		areaList = self._db.getMapAreaList()
		self._areaDropDown = AreaDropDown(areaList)
		
		#Remove default and demo maps and create delete map list
		areaList.remove('Default')
		areaList.remove('Demo Kindrogan')
		areaList.remove('Demo Large')
		self._areaDelList = FormList(areaList)
		
		#Get crop, class, owner, find and field lists
		cropList = self._db.getCropList()
		self._cropDropDown = FormList(cropList)
		classList = self._db.getClassList()
		self._classDropDown = FormList(classList)
		ownerList = self._db.getOwnerList()
		self._ownerDropDown = FormList(ownerList)
		findList = self._db.getFindIdList(self._mapArea.areaId)
		self._findList = FormList(findList)
		fieldList = self._db.getFieldIdList(self._mapArea.areaId)
		self._fieldList = FormList(fieldList)
		
	def _performActions(self):
		"""Performs any database actions requested"""
		
		#If action is AddArea then do separately as has different error handling
		if self._action == 'AddArea':
			self._addArea()
			
		#Perform other actions
		if self._action != None and self._action != 'AddArea':
			#Catch success or error status and display to user
			try:
				message = ''
				if self._action == 'AddField':
					message = self._db.addField(
												self._mapAreaName,
												self._getParam('LowX'),
												self._getParam('HiX'),
												self._getParam('LowY'),
												self._getParam('HiY'),
												self._getParam('Owner'),
												self._getParam('Crop'))	
												
				elif self._action == 'AddFind':
					message = self._db.addFind(
												self._mapAreaName,
												self._getParam('X'),
												self._getParam('Y'),
												self._getParam('Type'),
												self._getParam('Depth'),
												self._allowBlank('Notes'),
												self._allowBlank('ImgPath'))
												
				elif self._action == 'DelFind':
					message = self._db.delFind(self._getParam('Id'))
					
				elif self._action == 'DelField':
					message = self._db.delField(self._getParam('Id'))
					
				elif self._action == 'DelArea':
					message = self._db.delArea(self._getParam('DelArea'))
					#If deleting map currently being viewed then change display to Default map
					if self._mapAreaName == self._getParam('DelArea'):
						self._mapAreaName = 'Default'
						
				elif self._action == 'AddFindClass':
					message = self._db.addFindClass(
												self._getParam('ClassName'),
												self._getParam('Period'),
												self._getParam('Use'),
												'#'+self._getParam('Colour'))
													
				elif self._action == 'AddCrop':
					message = self._db.addCrop(
												self._getParam('CropName'),
												self._getParam('Start'),
												self._getParam('End'),
												self._allowBlank('ImgPath'))
					
				elif self._action == 'AddOwner':
					message = self._db.addOwner(
												self._getParam('OwnerName'),
												self._allowBlank('ImgPath'))
												
				#Display success message	
				self._status = Status('Success',message)
				
			except Exception as e:
				#Display error message
				self._status = Status('Error',str(e))
					
		#Select Area to display
		self._mapArea = self._db.getMapArea(self._mapAreaName)
					
	def _addArea(self):
		"""Adds map to database"""
		
		#Catch success or error status and display to user
		try:					
			message = self._db.addNewArea(
											self._getParam('MapArea'),
											self._getParam('MaxX'),
											self._getParam('MaxY'),
											self._allowBlank('ImgPath'))
											
			#Display success message								
			self._status = Status('Success',message)
			
		except Exception as e:
			#Display error message and display old map area
			self._status = Status('Error',str(e))
			self._mapAreaName = self._params['OldArea'].value

	def _getParam(self,key):
		"""This checks if parameter exists and return and errors if doesn't exist"""
		
		if key not in self._params:
			raise Exception(key + ' cannot be blank')
		return self._params[key].value
			
	def _allowBlank(self,key):
		"""This checks if parameter exists and return blank if doesn't exists """
		
		val = '' #This allows the value to be blank
		if key in self._params:
			val = self._params[key].value
		return val
	

		

		
	