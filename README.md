#Automated Square Building Script ReadMe

	This is a script I wrote with a coworker that takes information from
	an excel sheet and draws square buildings on a new File Goedatabase 
	made from infomration in the script. This is intended to be used to
	draw temporary placeholder buildings on a new FGDB created by this 
	script based on information exported to an excel spreadsheet from a
	back end database so that placeholder buildings can be drawn with 
	minimal human input. I have gone through the script and placed 72 
	"#"s on the line above file paths that need to be changed in order 
	for this script to work for you. Additionally xlrd, the python module
	installed with Esri products, uses zero based counting. If your PIN,
	Full Address, and Square Feet information for the buildings you want
	to be drawn arenot on rows 1, 2, and 3 respectively, using zero based
	counting, then you will need to change the list comprehensions on 
	lines 88, 93 and 98 respectively. Everything in this script should 
	work. If there's a problem with the script or if you need help feel
	free to contact me.