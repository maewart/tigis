#!/usr/bin/env python3
import numpy as np
from .htmlHelper import genHTMLElement, genTextElement, genTableElements, genImageElements
from datetime import datetime
__all__ = ['Field','Find','MapArea']

class Field(object):
	"""The Field object
	
	The Field class contains all information needed to render the geographic display and the textual information
	
	"""

	def __init__(self,fieldId,lowX,hiX,lowY,hiY,area,crop,cropStart,cropEnd,owner,areaId,imgOwner,imgCrop):
		"""Initialise object
		
		Keyword arguments:
		fieldId,lowX,hiX,lowY,hiY,area,crop,cropStart,cropEnd,owner,areaId,imgOwner,imgCrop
		"""
		
		self._fieldId = str(fieldId)
		self._lowX = int(lowX)
		self._hiX = int(hiX)
		self._lowY = int(lowY)
		self._hiY = int(hiY)
		self._area = round(float(area),2)
		self._crop = str(crop)
		self._cropStart = cropStart.strftime('%d %b')
		self._cropEnd = cropEnd.strftime('%d %b')
		self._owner = str(owner)
		self._areaId = str(areaId)
		self._imgOwner = str(imgOwner)
		self._imgCrop = str(imgCrop)
		self._htmlId = 'Field' + self._fieldId
		self._prettyId = 'Field ' + self._fieldId
		
	def renderGeo(self,style,maxY):
		"""Return the geographic svg elements
		
		Keyword arguments:
		style -- The css style
		maxY -- The maximum value of Y for the area map
		
		"""
		
		#Create popup text
		titleElement = genHTMLElement('title',[],[],self._prettyId)
		
		#Build rectangle element
		rectElement = genHTMLElement('rect',
									['class','id','x','y','width','height','fill','fill-opacity','stroke','stroke-width'],
									[style,self._htmlId,self._lowX,maxY-self._hiY,self._hiX-self._lowX,self._hiY-self._lowY,'lightgreen',0.5,'black',0.02],
									titleElement)
										
		#Smaller font size needed if field is only 1 width or high
		fontSize = '1.7px'
		yAdjust = 0.65
		if (self._hiX-self._lowX)<1.1 or (self._hiY-self._lowY)<1.1:
			fontSize = '0.7px'
			yAdjust = 0.25

		#Generate the field number to be displayed 
		fieldNumber = genHTMLElement('text',
									['x','y','font-size','font-family','font-color','font-weight','fill-opacity','text-anchor'],
									[self._lowX+(self._hiX-self._lowX)/2,maxY-self._hiY+(self._hiY-self._lowY)/2+yAdjust,fontSize,'Arial','white','bold',0.5,'middle'],
									self._fieldId)
		
		#return combined field number and rectangle
		return fieldNumber + rectElement
	
	def renderInfo(self):
		"""Return the information svg elements"""
		
		#Define ViewBox
		viewBox='0 0 300 500'
		
		#Background
		bgElement = genHTMLElement('rect',['x','y','width','height','fill'],
										[0,0,300,500,'white'])
		
		#Text Elements
		textElement = self._renderText()
		
		#Image Elements
		imageCrop = genImageElements(self._imgCrop,'none',140,140,150,175)
		imageOwner = genImageElements(self._imgOwner,'meet',140,155,150,335)
		imageElements = imageCrop + imageOwner
		
		#Stroke Elements
		stroke1 = genHTMLElement('path',['stroke','d'],['grey','M5 35 l290 0'])
		stroke2 = genHTMLElement('path',['stroke','d'],['grey','M5 165 l290 0'])
		stroke3 = genHTMLElement('path',['stroke','d'],['grey','M5 325 l290 0'])
		strokeElements = stroke1+stroke2+stroke3
		
		#Visibility Elements								
		visElement = genHTMLElement('set',
									['attributeName','from','to','begin','end'],
									['visibility','hidden','visible',self._htmlId + '.mouseover', self._htmlId + '.mouseout'])
										
		#SVG group of all Elements
		combineAll = bgElement + textElement + imageElements +strokeElements + visElement
		groupElement = genHTMLElement('svg',
										['width','height','viewbox','visibility'],
										['100%','100%',viewBox,'hidden'],
										combineAll)
		
		#Return all elements grouped
		return groupElement

	def _renderText(self):
		"""Private method for generating the text information"""
		
		#Settings
		xSpaceHeader=5
		xSpaceValue=55
		ySpace=25
		yBuffer = 5
		fontSize='14px'
		fontFamily='Arial'
		fontColourMain='grey'
		fontColourHeader='#428bca'
		
		#Generate Text Elements
		title = genTextElement(xSpaceHeader,ySpace,'bold',fontColourHeader,self._prettyId)
	
		dataTable = genTableElements(['X Low','Y Low','X High','Y High','Area'],
									[self._lowX,self._lowY,self._hiX,self._hiY,self._area],
									xSpaceHeader,xSpaceValue,2*ySpace+yBuffer,ySpace,fontColourHeader,fontColourMain)
		
		cropTable = genTableElements(['Crop','Start','End'],
									[self._crop,self._cropStart,self._cropEnd],
									xSpaceHeader,xSpaceValue,205,ySpace,fontColourHeader,fontColourMain)

		ownerHeader = genTextElement(xSpaceHeader,365,'normal',fontColourHeader,'Owner')
		ownerName = genTextElement(xSpaceHeader,390,'normal',fontColourMain,self._owner)
		
		#Combine all elements
		combined = title + dataTable + cropTable + ownerHeader + ownerName
		textElement = genHTMLElement('text',['font-size','font-family','font-weight'],
										[fontSize,fontFamily,'normal'],combined)
		
		#Return combined data
		return textElement

		
class Find(object):
	"""The Find object
	
	The Find class contains all information needed to render the geographic display and the textual information
	
	"""

	def __init__(self,findId,x,y,depth,notes,type,period,use,areaId,colour,imgFind):
		"""Initialise object
		
		Keyword arguments:
		findId,x,y,depth,notes,type,period,use,areaId,colour,imgFind
		"""
	
		self._findId = str(findId)
		self._x = int(x)
		self._y = int(y)
		self._depth = float(depth)
		self._notes = str(notes)
		self._type = str(type)
		self._period = str(period)
		self._use = str(use)
		self._areaId = str(areaId)
		self._colour = str(colour)
		self._imgFind = str(imgFind)
		self._htmlId = 'Find' + self._findId
		self._prettyId = 'Find ' + self._findId
		
	def renderGeo(self,style,maxY):
		"""Return the geographic svg elements
		
		Keyword arguments:
		style -- The css style
		maxY -- The maximum value of Y for the area map
		
		"""
		
		#Create popup text
		titleElement = genHTMLElement('title',[],[],self._prettyId)
		
		#Adjust radius and font for larger fields
		radius = 0.25
		fontSize = '0.4px'
		if maxY > 35:
			radius = 0.5
			fontSize = '0.6px'
		
		#Generate circle element
		circleElement = genHTMLElement('circle',
										['class','id','cx','cy','r','fill','stroke','stroke-width'],
										[style,self._htmlId,self._x,maxY-self._y,radius,self._colour,'black','0.02'],
										titleElement)
										
		#Generate number element
		circleNumber = genHTMLElement('text',
										['x','y','font-size','font-family','font-weight','text-anchor','alignment-baseline'],
										[self._x + 0.18,maxY-self._y-0.18,fontSize,'Arial','normal','start','bottom'],
										self._findId)
							
		#Return combined elements
		return circleNumber + circleElement
		
	def renderInfo(self):
		"""Return the information svg elements"""
	
		#Define ViewBox
		viewBox='0 0 300 500'
		
		#Background
		bgElement = genHTMLElement('rect',['x','y','width','height','fill'],
										[0,0,300,500,'white'])
		
		#Text Elements
		textElement = self._renderText()

		#Image Elements
		imageElement = genImageElements(self._imgFind,'none',200,200,90,290)
		
		#Stroke Elements
		stroke1 = genHTMLElement('path',['stroke','d'],['grey','M5 35 l290 0'])
		stroke2 = genHTMLElement('path',['stroke','d'],['grey','M5 190 l290 0'])
		stroke3 = genHTMLElement('path',['stroke','d'],['grey','M5 260 l290 0'])
		strokeElements = stroke1+stroke2+stroke3
		
		#Visibility Elements								
		visElement = genHTMLElement('set',['attributeName','from','to','begin','end'],
										['visibility','hidden','visible',self._htmlId + '.mouseover', self._htmlId + '.mouseout'])
										
		#SVG group of all Elements
		combineAll = bgElement + textElement + imageElement +strokeElements + visElement
		groupElement = genHTMLElement('svg',['width','height','viewbox','visibility'],['100%','100%',viewBox,'hidden'],combineAll)
		
		return groupElement

	def _renderText(self):
		"""Private method for generating the text information"""
		
		#Settings
		xSpaceHeader=5
		xSpaceValue=100
		ySpace=25
		yBuffer = 5
		fontSize='14px'
		fontFamily='Arial'
		fontColourMain='grey'
		fontColourHeader='#428bca'
		
		#Generate Text Elements
		title = genTextElement(xSpaceHeader,ySpace,'bold',fontColourHeader,self._prettyId)
	
		dataTable = genTableElements(['X Coordinate','Y Coordinate','Depth','Type','Period','Use'],
									[self._x,self._y,self._depth,self._type,self._period,self._use],
									xSpaceHeader,xSpaceValue,2*ySpace+yBuffer,ySpace,fontColourHeader,fontColourMain)
		
		notesHeader = genTextElement(xSpaceHeader,215,'normal',fontColourHeader,'Notes')
		notesValue = genTextElement(xSpaceHeader,240,'normal',fontColourMain,str(self._notes))
		imageHeader1 = genTextElement(20,305,'normal',fontColourHeader,'Object')
		imageHeader2 = genTextElement(20,325,'normal',fontColourHeader,'Image')
		
		#Combine text elements
		combined = title + dataTable + notesHeader + notesValue	+ imageHeader1 + imageHeader2
		textElement = genHTMLElement('text',
									['font-size','font-family','font-weight'],
									[fontSize,fontFamily,'normal'],
									combined)
									
		return textElement
		


class MapArea(object):
	"""The full map area
	
	The MapArea class contains all information needed to render the background, all fields and all finds
	
	"""

	def __init__(self,areaId,areaName,maxX,maxY,imgPath):
		"""Initialise object
		
		Keyword arguments:
		areaId,areaName,maxX,maxY,imgPath
		"""
		
		self._areaId = str(areaId)
		self._areaName = str(areaName)
		self._maxX = int(maxX)
		self._maxY = int(maxY)
		self._imgPath = str(imgPath)
		self._xInterval = max(int(np.ceil(float(self._maxX)/8)),1)
		self._yInterval = max(int(np.ceil(float(self._maxY)/8)),1)
		self._htmlId = 'MapArea'
		self._fieldList = []
		self._findList = []
		self._fieldStyle = ''
		self._findStyle = ''
		
		#Define view boxes
		self._viewBoxMapOuter = '0 0 ' + str(self._maxX + 2) + ' ' + str(self._maxY + 2)
		self._viewBoxMapInner = '0 0 ' + str(self._maxX) + ' ' + str(self._maxY)
		self._viewBoxInfo = '0 0 300 500'
	
	def addFields(self,objList,style):
		"""Attach fields to area
		
		Keyword arguments:
		objList -- list of fields
		style -- css style
		"""
		self._fieldList = objList
		self._fieldStyle = style
	
	def addFinds(self,objList,style):
		"""Attach finds to area
		
		Keyword arguments:
		objList -- list of finds
		style -- css style
		"""
		
		self._findList = objList
		self._findStyle = style
	
	def renderMap(self,width,height):
		"""Renders the svg map and returns the svg element for display
		
		Keyword arguments:
		width -- the svg width - can be percent or absolute
		height -- the svg height - can be percent or absolute
		"""
		
		#Render all and combine
		viewBox = self._viewBoxMapOuter
		background = self._renderBackground()
		fields = self._renderObjects(self._fieldList,self._fieldStyle)
		finds = self._renderObjects(self._findList,self._findStyle)
		combined = background + fields + finds
		svgRoot = genHTMLElement('svg',
								['width','height','viewBox'],
								[width,height,viewBox],
								combined)
		
		#Return the root svg element for display
		return svgRoot
	
	def renderInfo(self,width,height):
		"""Renders the svg information and returns the svg element for display
		
		Keyword arguments:
		width -- the svg width - can be percent or absolute
		height -- the svg height - can be percent or absolute
		"""
		
		#Render all and combine
		instructions = self._renderInstructions()
		fieldInfo = self._renderObjectInfo(self._fieldList)
		findInfo = self._renderObjectInfo(self._findList)
		combined = instructions + fieldInfo + findInfo
		svgRoot = genHTMLElement('svg',
								['width','height'],
								[width,height],
								combined)
		
		#Return the root svg element for display
		return svgRoot
	
	def _renderBackground(self):
		"""Private method for rendering map background"""
	
		fontFamily='Arial'
		viewBox = self._viewBoxMapOuter
		
		#Scale axes fonts depending on area size
		fontScale = min(0.75,round(max(self._maxX,self._maxY) / 20 * 0.50,2))
		fontSize = str(fontScale)+'px'
		xFontBuffer = 1.2+max(self._maxX,self._maxY)/8*0.1
		
		#Create x Axis
		xAxis = ''
		for x in np.arange(0,self._maxX + 1,self._xInterval):
			xStr = str(x)
			xAxis = xAxis + genHTMLElement('text',
											['x','y','font-size','font-family','font-weight','text-anchor'],
											[x + 1,self._maxY + xFontBuffer,fontSize,fontFamily,'normal','middle'],
											xStr)
							
		#Create y Axis
		yAxis = ''
		yRange = np.arange(0,self._maxY + 1,self._yInterval)
		for y in yRange:
			yStr = str(y)
			yAxis = yAxis + genHTMLElement('text',
											['x','y','font-size','font-family','font-weight','text-anchor','alignment-baseline'],
											[0.9,self._maxY - y + 1,fontSize,fontFamily,'normal','end','middle'],
											yStr)
		
		#Create Axis titles
		xTitle = genHTMLElement('text',
								['x','y','font-size','font-family','font-weight','text-anchor'],
								[self._maxX/2 + 1,self._maxY + 1.9,fontSize,fontFamily,'bold','middle'],
								'x')
		
		yTitle = genHTMLElement('text',
								['x','y','font-size','font-family','font-weight','text-anchor','alignment-baseline'],
								[0.4,yRange[4],fontSize,fontFamily,'bold','end','middle'],
								'y')
		
		#Generate translated image
		image = self._renderImage()
		translateImage = genHTMLElement('g',['transform'],['translate(1,1)'],image)
		
		#Combine elements
		combine = translateImage + xAxis + yAxis + xTitle + yTitle
		
		#Create SVG collection and return
		svgElement = genHTMLElement('svg',
									['id','width','height','viewBox'],
									[self._htmlId,'100%','100%',viewBox],
									combine)
									
		return svgElement		

	def _renderImage(self):
		"""Private method for rendering map background image"""
		
		viewBox = self._viewBoxMapInner
		imageElement = genHTMLElement('image',['href','width','height','x','y','preserveAspectRatio'],[self._imgPath,'100%','100%',0,0,'none'])
		svgElement = genHTMLElement('svg',['width','height','viewBox'],[str(self._maxX),str(self._maxY),viewBox],imageElement)
		outline = genHTMLElement('rect',['x','y','width','height','fill','stroke','stroke-width'],[0,0,self._maxX,self._maxY,'none','black',0.04])
		
		return outline + svgElement
	
	def _renderInstructions(self):
		"""Private method for rendering instructions"""
		
		fontFamily='Arial'
	
		#Define ViewBox
		viewBox= self._viewBoxInfo
		
		#Generate Text Elements
		title = genTextElement(10,80,'bold','#428bca',self._areaName + ' Map Area')
		line1 = genTextElement(10,140,'normal','grey','Hover over fields or finds',False)
		line2 = genTextElement(10,165,'normal','grey','to display information',False)
		
		combineText = title + line1 + line2
		textElement = genHTMLElement('text',
										['font-size','font-family','font-weight','text-anchor'],
										['16px',fontFamily,'bold','left'],
										combineText)
										
		#Generate legend text
		legend = genTextElement(10,360,'bold','#428bca','Legend')
		fieldLabel = genTextElement(34,390,'normal','grey','Fields')
		findLabel = genTextElement(34,420,'normal','grey','Finds (diff colour per class)',False)
		highlightLabel = genTextElement(34,450,'normal','grey','Current Selection')
		
		combineLegend = legend + fieldLabel + findLabel + highlightLabel
		legendText = genHTMLElement('text',
										['font-size','font-family','font-weight','text-anchor'],
										['14px',fontFamily,'normal','start'],
										combineLegend)
		
		#Generate legend shapes
		rectElement = genHTMLElement('rect',
										['x','y','width','height','fill','fill-opacity','stroke','stroke-width'],
										[10,374,18,18,'lightgreen',1,'black',2])
										
		circleElement = genHTMLElement('circle',
										['cx','cy','r','fill','stroke','stroke-width'],
										[20,414,9,'red','black','2'])
										
		highlightElement = genHTMLElement('rect',
										['x','y','width','height','fill','fill-opacity'],
										[10,440,18,10,'yellow',1])
		
		#combine shapes
		legendElement = legendText + rectElement + circleElement + highlightElement
									
		#SVG group of all Elements
		combineAll = textElement + legendElement
		groupElement = genHTMLElement('svg',
										['width','height','viewbox','visibility'],
										['100%','100%',viewBox,'visible'],
										combineAll)
		
		return groupElement
	
	def _renderObjects(self,objList,style):
		"""Private method for rendering fields and finds geographic objects"""
	
		#Define ViewBox
		viewBox = self._viewBoxMapInner
		
		#Get obj Elements
		objElements = ''
		for obj in objList:
			objElements = objElements + obj.renderGeo(style,self._maxY)
	
		#Create SVG element
		svgElement = genHTMLElement('svg',
									['width','height','viewBox'],
									[str(self._maxX),str(self._maxY),viewBox],
									objElements)
		
		#Shift to account for axes 		
		translateSvg = genHTMLElement('g',
									['transform'],
									['translate(1,1)'],
									svgElement)
		
		return translateSvg
		
	def _renderObjectInfo(self,objList):
		"""Private method for rendering fields and finds information"""
		
		objElements = ''
		for obj in objList:
			objElements = objElements + obj.renderInfo()
		return objElements
	
	@property
	def areaId(self):
		return self._areaId
		
	@property
	def maxX(self):
		return self._maxX
		
	@property
	def maxY(self):
		return self._maxY
		
