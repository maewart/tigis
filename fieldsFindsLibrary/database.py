#!/usr/bin/env python3
import cx_Oracle
from .geoObjects import Field, Find, MapArea
__all__ = ['DbFieldsFinds']

class DbFieldsFinds(object):
	"""This object controls all interactions with the fields and finds database
	
	This class contains all functionality to:
	1) Control the connection to the database
	2) Load maps, fields and finds
	3) Add new maps, fields and finds
	4) Perform consistency checks on data including field intersection calculations
	5) Delete maps, fields and finds
	6) Add new find classes, crops and owners
	7) Get lists of data from database
	"""

	def __init__(self):
		"""Initialise and set connection to None"""
	
		self._conn = None
			
	def openConnection(self):
		"""Open Connection"""
	
		pwdPath = "../../../oracle/mainpwd"
		with open(pwdPath,'r') as pwdRaw:
			pwd = pwdRaw.read().strip()
		self._conn = cx_Oracle.connect(dsn="geosgen",user="s1783947",password=pwd)
		pwd = None #Keep Pwd in memory for a short as possible	
		
	def closeConnection(self):
		"""Close Connection"""
	
		assert self._conn != None #Check connection open
		self._conn.close
		self._conn = None
	
	def getMapArea(self,areaName):
		"""Get Map Area
		
		Keyword arguments:
		areaName -- Name of Map
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		sql = "Select * from s1783947.FF_AREA where AREA_NAME=:Area"
		cursor.execute(sql,Area=areaName)
		for row in cursor:
			area = MapArea(row[0],row[1],row[2],row[3],row[4])

		if cursor.rowcount == 0:
			raise Exception("Cannot Find Requested Map Area")
		if cursor.rowcount > 1:
			raise Exception("Duplicate Map Areas Returned")
			
		return area
	
	def getFields(self,areaId):
		"""Get Fields in Area
		
		Keyword arguments:
		areaId -- Id of MapArea
		"""	
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		
		sql = "Select FIELD_ID, LOW_X, HI_X, LOW_Y, HI_Y, FIELD_AREA, CROP_NAME, CROP_START, CROP_END, OWNER, AREA_ID, OWNER_IMAGE, CROP_IMAGE from s1783947.VIEW_FIELDS_COMB where AREA_ID=:AreaId"
		cursor.execute(sql,AreaId=areaId)
		
		fieldList = []
		for row in cursor:
			field = Field(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])
			fieldList.append(field)
		cursor = None
		
		return fieldList
	
	def getFinds(self,areaId,filterClass=None):
		"""Get Finds in Area
		
		Keyword arguments:
		areaId -- Id of MapArea
		"""	
		
		assert self._conn != None #Check connection open
			
		cursor = self._conn.cursor()
		sql = "Select OBJECT_ID, X, Y, DEPTH, FIELD_NOTES, TYPE, PERIOD, USE, AREA_ID, COLOUR, FIND_IMAGE from s1783947.VIEW_FINDS_COMB where AREA_ID=:AreaId"
		
		#Apply Filter
		if filterClass == None:
			cursor.execute(sql,AreaId=areaId)
		else:
			sql = sql + " and Type=:FilterClass"
			cursor.execute(sql,AreaId=areaId,FilterClass=filterClass)
		
		findList = []
		for row in cursor:
			find = Find(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10])
			findList.append(find)
		cursor = None
		
		return findList
	
	
	def getMapAreaList(self):
		"""Get list of Map Areas"""
	
		sql = "Select Distinct AREA_NAME from s1783947.FF_AREA Order By AREA_NAME"
		return self._getList(sql)
		
	def getCropList(self):
		"""Get list of Crops"""
	
		sql = "Select Distinct NAME from s1783947.VIEW_CROP_COMB Order By NAME"
		return self._getList(sql)
	
	def getClassList(self):
		"""Get list of Classes"""
	
		sql = "Select Distinct NAME from s1783947.VIEW_CLASS_COMB Order By NAME"
		return self._getList(sql)
		
	def getOwnerList(self):
		"""Get list of Owners"""
	
		sql = "Select Distinct FARMER_NAME from s1783947.FF_FARMERS Order By FARMER_NAME"
		return self._getList(sql)
		
	def getFieldIdList(self,areaId):
		"""Get list of Field Ids within area"""
		
		sql = "Select Distinct FIELD_ID from s1783947.FF_FIELDS_NEW where AREA_ID=:AreaId Order By FIELD_ID"
		return self._getListForArea(sql,areaId)
	
	def getFindIdList(self,areaId):
		"""Get list of Find Ids within area"""
	
		sql = "Select Distinct FIND_ID from s1783947.FF_FINDS_NEW where AREA_ID=:AreaId Order By FIND_ID"
		return self._getListForArea(sql,areaId)
	
	def _getList(self,sql):
		"""private list retriever
		
		Keyword arguments:
		sql -- sql query
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		cursor.execute(sql)
		areaList = []
		for row in cursor:
			areaList.append(row[0])
		return areaList
		
	def _getListForArea(self,sql,areaId):
		"""private list retriever for specific area Id
		
		Keyword arguments:
		sql -- sql query
		areaId -- Area Id
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		cursor.execute(sql,AreaId=areaId)
		areaList = []
		for row in cursor:
			areaList.append(row[0])
		return areaList
	
	def addNewArea(self,areaName,maxX,maxY,imgPath):
		"""Add new area
		
		Keyword arguments
		areaName -- Name
		maxX -- Max X value
		maxY -- Max Y value
		imgPath -- Path to background image
		
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		
		#Check Name doesn't already exist
		sql = "Select * from s1783947.FF_AREA where AREA_NAME=:Area"
		cursor.execute(sql,Area=areaName)
		if len(cursor.fetchall()) > 0:
			raise Exception("Map Area Name already exists: " + areaName)
			
		#Check are numbers not strings
		try:
			fx = float(maxX)
			fy = float(maxY)
		except:
			raise Exception('Coordinates must be integer >= 0')
				
		#Check coordinates are integers
		if abs(fx- round(fx)) > 0.0001 or abs(fy - round(fy)) > 0.0001: raise Exception('Coordinates must be an integer >= 10')
		
		#Value checks
		if fx <10: raise Exception('X size must be integer greater than 10')
		if fy <10: raise Exception('Y size must be integer greater than 10')
		if fx > 50: raise Exception('X size cannot be greater than 50')
		if fy > 50: raise Exception('Y size cannot be greater than 50')
		
		#Get new Area Id
		sql = "Select Max(AREA_ID) from s1783947.FF_AREA"
		cursor.execute(sql)
		newId = 0
		for row in cursor:
			newId = row[0]+1
		
		#Insert New Area
		sql = "Insert Into s1783947.FF_Area (AREA_ID,AREA_NAME,MAX_X,MAX_Y,IMAGE_PATH) Values (:AreaId,:Name,:MaxX,:MaxY,:ImgPath)"
		cursor.execute(sql,AreaId=newId,Name=areaName,MaxX=maxX,MaxY=maxY,ImgPath=imgPath)
		self._conn.commit()
		
		#Return success message
		return areaName + ' area created'

	def addField(self,areaName,lowX,hiX,lowY,hiY,owner,cropName):
		"""Add new field
		
		Keyword arguments
		areaName,lowX,hiX,lowY,hiY,owner,cropName
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		
		#Load area to enable checks
		mapArea = self.getMapArea(areaName)
		
		#Check are numbers not strings
		try:
			fLowX = float(lowX)
			fLowY = float(lowY)
			fHiX = float(hiX)
			fHiY = float(hiY)
		except:
			raise Exception('Coordinates must be integer greater than 0')
		
		#Check coordinates are integers
		if abs(fLowX - round(fLowX)) > 0.0001 or abs(fLowY - round(fLowY)) > 0.0001 or abs(fHiX - round(fHiX)) > 0.0001 or abs(fHiY - round(fHiY)) > 0.0001: raise Exception('Coordinates must be an integer >= 0')

		#Derive Area
		fArea = (fHiX-fLowX) * (fHiY-fLowY)
		
		#Value checks
		if fLowX <0: raise Exception('X Coordinates must be integer >= 0')
		if fLowY <0: raise Exception('Y Coordinates must be integer >= 0')
		if fHiX <=0: raise Exception('X Coordinates must be integer > 0')
		if fHiY <=0: raise Exception('Y Coordinates must be integer > 0')
		if fHiX <= fLowX: raise Exception('High X must be greater than Low X')
		if fHiY <= fLowY: raise Exception('High Y must be greater than Low Y')
		if fHiX > mapArea.maxX: raise Exception('X coordinate must be within area bounds')
		if fHiY > mapArea.maxY: raise Exception('X coordinate must be within area bounds')
		if fArea <=0: raise Exception('Area must be greater than 0')
		
		#Intersect Check
		self._checkIntersect(mapArea.areaId,fLowX,fLowY,fHiX,fHiY)
		
		#Get Crop Id
		sql = "Select CROP from s1783947.VIEW_CROP_COMB where NAME=:Name"
		cursor.execute(sql,Name=cropName)
		i=0
		for row in cursor:
			cropId = row[0]
			i=i+1
		if i == 0:
			raise Exception("Crop does not exist: " + cropName)
		elif i > 1:
			raise Exception("Duplicate crop in database: " + cropName)
					
		#Get new Field Id
		sql = "Select Max(FIELD_ID) from s1783947.VIEW_FIELDS_COMB"
		cursor.execute(sql)
		newId = 0
		for row in cursor:
			newId = row[0]+1
		
		#Insert Field
		sql = "Insert Into s1783947.FF_FIELDS_NEW (FIELD_ID,LOWX,HIX,LOWY,HIY,AREA,OWNER,CROP,AREA_ID) Values (:FieldId,:LowX,:HiX,:LowY,:HiY,:Area,:Owner,:CropId,:AreaId)"
		cursor.execute(sql,FieldId=newId,LowX=lowX,HiX=hiX,LowY=lowY,HiY=hiY,Area=fArea,Owner=owner,CropId=cropId,AreaId=mapArea.areaId)
		self._conn.commit()
		
		#Return success message
		return 'Field ' + str(newId) + ' added'
		
	def _checkIntersect(self,areaId,lowX,lowY,hiX,hiY):
		""" Private method to check if field intersects with existing fields
		
		Keyword arguments:
		areaId,lowX,lowY,hiX,hiY
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		sql = "select FIELD_ID from VIEW_FIELDS_COMB where AREA_ID=:AreaId and ((:LowX > LOW_X and :LowX < HI_X and :LowY > LOW_Y and :LowY < HI_Y) or (:HiX > LOW_X and :HiX < HI_X and :LowY > LOW_Y and :LowY < HI_Y) or (:LowX > LOW_X and :LowX < HI_X and :HiY > LOW_Y and :HiY < HI_Y) or (:HiX > LOW_X and :HiX < HI_X and :HiY > LOW_Y and :HiY < HI_Y))"
		cursor.execute(sql,AreaId=areaId,LowX=lowX+0.1,LowY=lowY+0.1,HiX=hiX-0.1,HiY=hiY-0.1)
		result = ''
		count = 0
		for row in cursor:
			if len(result)>0:
				result = result +', '+ str(row[0])
			else:
				result = result +' '+ str(row[0])
			count = count +  1
		
		#Raise exception if intersects
		if count > 0:
			raise Exception('Cannot intersect with other fields. This field would intersect with' + result)
		
	def addFind(self,areaName,x,y,typeName,depth,notes,imgPath):
		"""Add new find
		
		Keyword arguments
		areaName,x,y,typeName,depth,notes,imgPath
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
			
		#Load area to enable checks
		mapArea = self.getMapArea(areaName)
		
		#Check are numbers not strings
		try:
			fx = float(x)
			fy = float(y)
		except:
			raise Exception('Coordinates must be integer >= 0')
		
		try:
			fDepth = float(depth)
		except:
			raise Exception('Depth must be number greater than 0')
		
		#Check coordinates are integers
		if abs(fx- round(fx)) > 0.0001 or abs(fy - round(fy)) > 0.0001: raise Exception('Coordinates must be an integer >= 0')
		
		#Value checks
		if fx <0: raise Exception('X Coordinates must be integer greater than 0')
		if fy <0: raise Exception('Y Coordinates must be integer greater than 0')
		if fx > mapArea.maxX: raise Exception('X coordinate must be within area bounds')
		if fy > mapArea.maxY: raise Exception('Y coordinate must be within area bounds')
		if fDepth <0: raise Exception('Depth must be >= 0')
		if fDepth >20: raise Exception('Depth must be < 20m')
		
		#Existing Find Check
		self._checkFindCoord(mapArea.areaId,x,y)
		
		#Get Type Id
		sql = "Select TYPE from s1783947.VIEW_CLASS_COMB where NAME=:Name"
		cursor.execute(sql,Name=typeName)
		i=0
		for row in cursor:
			typeId = row[0]
			i=i+1
		if i == 0:
			raise Exception("Type does not exist: " + typeName)
		elif i > 1:
			raise Exception("Duplicate Type in database: " + typeName)
					
		#Get new Find Id
		sql = "Select Max(OBJECT_ID) from s1783947.VIEW_FINDS_COMB"
		cursor.execute(sql)
		newId = 0
		for row in cursor:
			newId = row[0]+1	
		
		#Insert Find
		sql = "Insert Into s1783947.FF_FINDS_NEW (FIND_ID,XCOORD,YCOORD,TYPE,DEPTH,FIELD_NOTES,AREA_ID,IMAGE_PATH) Values (:FindId,:X,:Y,:TypeId,:Depth,:Notes,:AreaId,:ImgPath)"
		cursor.execute(sql,FindId=newId,X=x,Y=y,TypeId=typeId,Depth=depth,Notes=notes,AreaId=mapArea.areaId,ImgPath=imgPath)
		self._conn.commit()
		
		#Return success message
		return 'Find ' + str(newId) + ' added'
			
	def _checkFindCoord(self,areaId,x,y):
		"""Private method to check if find already exists in location
		
		Keyword arguments:
		areaId -- Id of area
		x -- X coordinate
		y -- Y coordinate
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		sql = "select OBJECT_ID from VIEW_FINDS_COMB where AREA_ID=:AreaId and X=:X and Y=:Y"
		cursor.execute(sql,AreaId=areaId,X=x,Y=y)
		result = ''
		count = 0
		for row in cursor:
			if len(result)>0:
				result = result +', '+ str(row[0])
			else:
				result = result +' '+ str(row[0])
			count = count +  1
			
		#Raise exception if find already exists
		if count > 0:
			raise Exception('Cannot have same coordinate as existing find. This find has the same as' + result)
	
	def delFind(self,id):
		"""Delete find
		
		Keyword arguments:
		id -- Id to delete
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
			
		#Delete Find
		sql = "Delete from s1783947.FF_FINDS_NEW where FIND_ID=:Id"
		cursor.execute(sql,Id=id)
		self._conn.commit()
		
		return 'Find ' + str(id) + ' deleted'
	
	def delField(self,id):
		"""Delete field
		
		Keyword arguments:
		id -- Id to delete
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		#Delete Field
		sql = "Delete from s1783947.FF_FIELDS_NEW where FIELD_ID=:Id"
		cursor.execute(sql,Id=id)
		self._conn.commit()
		
		return 'Field ' + str(id) + ' deleted'
		
	def delArea(self,areaName):
		"""Delete Map Area
		
		Keyword arguments:
		areaName -- Area Name to delete
		"""
	
		#Check not default or demo area
		defaultList=['Default','Demo Kindrogan','Demo Large']
		if areaName in defaultList:
			raise Exception("Cannot delete default or demo maps. If you create your own map, you'll be able to delete it.")
				
		#Load Area to get Id and ensure it exists
		mapArea = self.getMapArea(areaName)
		
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
		#Delete Area
		sql = "Delete from s1783947.FF_AREA where AREA_ID=:Id"
		try:
			cursor.execute(sql,Id=mapArea.areaId)
			self._conn.commit()
		except:
			raise Exception('You must remove Fields and Finds within map first due to the database foreign key requirement. This will be improved in next version')
		
		return areaName + ' map deleted'
		
	def addFindClass(self,className,period,use,colour):
		"""Add new Class
		
		Keyword arguments:
		className,period,use,colour
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
				
		#Existing Class Check
		sql = "Select NAME from s1783947.FF_CLASS_NEW where NAME=:Name"
		cursor.execute(sql,Name=className)
		i=0
		for row in cursor:
			typeId = row[0]
			i=i+1
		if i > 0:
			raise Exception("Class Name already exists: " + className)
					
		#Get new Type Id
		sql = "Select Max(TYPE) from s1783947.VIEW_CLASS_COMB"
		cursor.execute(sql)
		newId = 0
		for row in cursor:
			newId = row[0]+1
		
		#Insert Class
		sql = "Insert Into s1783947.FF_CLASS_NEW (TYPE,NAME,PERIOD,USE,COLOUR) Values (:Type,:Name,:Period,:Use,:Colour)"
		cursor.execute(sql,Type=newId,Name=className,Period=period,Use=use,Colour=colour)
		self._conn.commit()
		
		return className + ' class added'
		
	def addCrop(self,cropName,start,end,imgPath):
		"""Add new Crop
		
		Keyword arguments:
		cropName,start,end,imgPath
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
				
		#Existing Crop Check
		sql = "Select NAME from s1783947.FF_CROPS_NEW where NAME=:Name"
		cursor.execute(sql,Name=cropName)
		i=0
		for row in cursor:
			typeId = row[0]
			i=i+1
		if i > 0:
			raise Exception("Crop Name already exists: " + cropName)
					
		#Get new Crop Id
		sql = "Select Max(CROP) from s1783947.VIEW_CROP_COMB"
		cursor.execute(sql)
		newId = 0
		for row in cursor:
			newId = row[0]+1

		#Insert Crop
		sql = "Insert Into s1783947.FF_CROPS_NEW (CROP,NAME,START_OF_SEASON,END_OF_SEASON,IMAGE_PATH) Values (:Crop,:Name,TO_DATE(:StartDate,'yyyy-mm-dd'),TO_DATE(:EndDate,'yyyy-mm-dd'),:ImgPath)"
		cursor.execute(sql,Crop=newId,Name=cropName,StartDate=start,EndDate=end,ImgPath=imgPath)
		self._conn.commit()
		
		return cropName + ' crop added'
		
	def addOwner(self,ownerName,imgPath):
		"""Add new owner
		
		Keyword arguments
		ownerName,imgPath
		"""
	
		assert self._conn != None #Check connection open
		cursor = self._conn.cursor()
				
		#Existing Crop Check
		sql = "Select FARMER_NAME from s1783947.FF_FARMERS where FARMER_NAME=:Name"
		cursor.execute(sql,Name=ownerName)
		i=0
		for row in cursor:
			typeId = row[0]
			i=i+1
		if i > 0:
			raise Exception("Owner Name already exists: " + ownerName)
					
		#Insert Owner
		sql = "Insert Into s1783947.FF_FARMERS (FARMER_NAME,IMAGE_PATH) Values (:Name,:ImgPath)"
		cursor.execute(sql,Name=ownerName,ImgPath=imgPath)
		self._conn.commit()
		
		return ownerName + ' added'
