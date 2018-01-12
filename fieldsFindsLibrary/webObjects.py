#!/usr/bin/env python3
import numpy as np
import copy
from .htmlHelper import genHTMLElement
__all__ = ['AreaDropDown','FormList','Status']

class AreaDropDown(object):
	"""Drop down list of Map Areas"""

	def __init__(self,areaList):
		"""Initialise object
		
		Keyword arguments:
		areaList -- list of Map Areas
		"""
		
		self._areaList = copy.deepcopy(areaList)
		
	def __str__(self):
		"""Returns dropdown html elements"""
		
		dropList = ''
		for area in self._areaList:
			link = 'https://www.geos.ed.ac.uk/~s1783947/cgi-bin/webmapping/main.py?MapArea=' + area
			aElement = genHTMLElement('a',['href'],[link],area)
			listElement = genHTMLElement('li',[],[],aElement)
			dropList = dropList + listElement
		return dropList

		
class FormList(object):
	"""Renders form option list from any input list"""

	def __init__(self,list):
		"""Initialise object
		
		Keyword arguments:
		list -- any list
		"""
		
		self._list = copy.deepcopy(list)
		
	def __str__(self):
		"""Returns html list elements"""
		
		html = ''
		for val in self._list:
			listElement = genHTMLElement('option',[],[],str(val))
			html = html + listElement
		return html

		
class Status(object):
	"""Create action status html elements"""

	def __init__(self,status,message):
		"""Initialise object
		
		Keyword arguments:
		status -- Success, Filter Applied or Error
		message -- Any message
		"""
		
		self._status = status
		self._message = message
		
	def __str__(self):
		"""Returns html status elements"""
		
		if self._status == 'Success':
			style = 'alert alert-success'
			back = ''
		elif self._status == 'Filter Applied':
			style = 'alert alert-warning'
			back = ''
		else:
			style = 'alert alert-danger'
			#Attach back instruction to see cause of error
			back = '<br><br>Hit back and expand action box to see values entered'
		
		#Create bold status and normal font message
		strong = genHTMLElement('strong',[],[],self._status)
		html = genHTMLElement('div',['class'],[style],strong + ' ' + self._message + back)
		
		return html


