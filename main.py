#!/usr/bin/env python3

""" Main entry to fields and finds code

This is the main entry point to the fields and finds website python code.
This code creates an instance of the website passing in any parameters.
It then prints the output to screen.
It also catches any exceptions preventing the website to crash in the event of an error.
"""


#Import CGI so python can interact with browser
import cgi

#FieldsFindsLibrary is the main library for generating the website
import fieldsFindsLibrary as ffLib

#Get parameters submitted
params = cgi.FieldStorage()

#Try catch block around website - don't want website to crash if anything goes wrong
try:
	#Initialise website
	website = ffLib.WebsiteFieldsFinds(params)
	
	#Perform actions and create website
	website.run()
	
	#Print to screen
	print(website)
	
except Exception as e:
	#Create basic error display in case website experiences a major failure such as the database being offline
	print("Content-Type: text/html\n")
	print("<!DOCTYPE html>")
	print("<head>")
	print("<title>Error</title>")
	print("</head>")
	print('<body><br><center>Ooops !!! Something went wrong: <br><br><font color="red">')
	print(e)
	print("</font><br><br>Please contact s1783947@sms.ed.ac.uk</center></body>")
	print("</html>")



