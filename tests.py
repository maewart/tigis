#!/usr/bin/env python3
from nose.tools import assert_equals, assert_raises
import fieldsFindsLibrary as ffLib

class TestHTML:
	def test_noElement(self):
		""" Test HTML element creation with no inner element value """
		elementName = 'xyz'
		paramNames = ['A','B','C']
		paramValues = ['a','b','c']
		text = ffLib.genHTMLElement(elementName,paramNames,paramValues)
		expectedResult = '<xyz A="a" B="b" C="c"/>'
		assert_equals(text,expectedResult)
		
	def test_withElement(self):
		""" Test HTML element creation with element value """
		elementName = 'xyz'
		paramNames = ['A','B','C']
		paramValues = ['a','b','c']
		elementValue = 'Easy as ABC'
		text = ffLib.genHTMLElement(elementName,paramNames,paramValues,elementValue)
		expectedResult = '<xyz A="a" B="b" C="c">Easy as ABC</xyz>'
		assert_equals(text,expectedResult)
	
	def test_failsDiffLengths(self):
		""" Test different length exception gets thrown """
		elementName = 'xyz'
		paramNames = ['A','B','C']
		paramValues = ['a','b']
		elementValue = 'Easy as ABC'
		assert_raises(AssertionError,ffLib.genHTMLElement,elementName,paramNames,paramValues,elementValue)

	def test_embed(self):
		""" Test embedding element within element works """
		elementName = 'xyz'
		paramNames = ['A','B','C']
		paramValues = ['a','b','c']
		elementValue = ffLib.genHTMLElement(elementName,paramNames,paramValues)
		text = ffLib.genHTMLElement(elementName,paramNames,paramValues,elementValue)
		expectedResult = '<xyz A="a" B="b" C="c"><xyz A="a" B="b" C="c"/></xyz>'
		assert_equals(text,expectedResult)
		
		
class TestDatabase:
	def test_dbOpen(self):
		""" Test can connect to db """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		
	def test_dbCloseWhenOpen(self):
		""" Test can close an open connection """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		ff.closeConnection()
		
	def test_dbCloseWhenNotOpen(self):
		""" Test throws error if connection not open """
		ff = ffLib.DbFieldsFinds()
		assert_raises(AssertionError,ff.closeConnection)
		

	def test_canLoadDefaultArea(self):
		""" Ensure can load default area """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		area=ff.getMapArea('Default')
		expectedMaxX = 16
		assert_equals(area.maxX,expectedMaxX)
		ff.closeConnection()
		
	def test_canLoadFields(self):
		""" Ensure can load fields from database """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		fields=ff.getFields(1)
		assert len(fields) > 0
		ff.closeConnection()
		
	def test_canLoadFinds(self):
		""" Ensure can load finds from database """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		finds=ff.getFinds(1)
		assert len(finds) > 0
		ff.closeConnection()
	
	def test_loadLists(self):
		""" Ensure all data lists load ok """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		assert len(ff.getMapAreaList()) > 0
		assert len(ff.getCropList()) > 0
		assert len(ff.getClassList()) > 0
		assert len(ff.getOwnerList()) > 0
		

class TestGeoObjects:
	def test_mapArea(self):
		""" Check mapArea rendering works """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		area=ff.getMapArea('Default')
		map=area.renderMap(500,500)
		info=area.renderInfo(300,500)
		assert map[:4] == '<svg'
		assert info[:4] == '<svg'
		assert map[-6:] == '</svg>'
		assert info[-6:] == '</svg>'
		ff.closeConnection()
	
	def test_field(self):
		""" Check field rendering works """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		field=ff.getFields(1)[0]
		geo=field.renderGeo('xxx',20)
		info=field.renderInfo()
		assert geo[:5] == '<text'
		assert info[:4] == '<svg'
		assert geo[-7:] == '</rect>'
		assert info[-6:] == '</svg>'
		ff.closeConnection()
		
	def test_find(self):
		""" Check find rendering works """
		ff = ffLib.DbFieldsFinds()
		ff.openConnection()
		find=ff.getFinds(1)[0]
		geo=find.renderGeo('xxx',20)
		info=find.renderInfo()
		assert geo[:5] == '<text'
		assert info[:4] == '<svg'
		assert geo[-9:] == '</circle>'
		assert info[-6:] == '</svg>'
		ff.closeConnection()
		

class TestWebObjects:
	def test_formList(self):
		""" Check list creation correct """
		list = ['aa','bb']
		obj = ffLib.FormList(list)
		expectedResult = '<option>aa</option><option>bb</option>'
		assert_equals(str(obj),expectedResult)
		
	def test_mapLists(self):
		""" Ensure map lists correct """
		list = ['aa','bb']
		obj = ffLib.AreaDropDown(list)
		expectedResult = '<li><a href="https://www.geos.ed.ac.uk/~s1783947/cgi-bin/webmapping/main.py?MapArea=aa">aa</a></li><li><a href="https://www.geos.ed.ac.uk/~s1783947/cgi-bin/webmapping/main.py?MapArea=bb">bb</a></li>'
		assert_equals(str(obj),expectedResult)
	
	def test_statusSuccess(self):
		""" Check success status html """
		obj = ffLib.Status('Success','Happy Days')
		expectedResult = '<div class="alert alert-success"><strong>Success</strong> Happy Days</div>'
		assert_equals(str(obj),expectedResult)

	def test_statusError(self):
		""" Check error status html """
		obj = ffLib.Status('Error','Oh No')
		expectedResult = '<div class="alert alert-danger"><strong>Error</strong> Oh No<br><br>Hit back and expand action box to see values entered</div>'
		assert_equals(str(obj),expectedResult)

	def test_statusFilter(self):
		""" Check filter status html """
		obj = ffLib.Status('Filter Applied','Happy Days')
		expectedResult = '<div class="alert alert-warning"><strong>Filter Applied</strong> Happy Days</div>'
		assert_equals(str(obj),expectedResult)