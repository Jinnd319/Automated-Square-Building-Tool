import arcpy
import time
import os
import sys
import xlrd
import math


# Folder to create FGDB
########################################################################
Directory = r"Location file goes here"

# Calculate date, time, and FGDB name
date = time.strftime('%Y%m%d_%H%M%S')
GDB_Name = date + '_NewFootprints.gdb'

# Create a new FileGDB
arcpy.CreateFileGDB_management(Directory, GDB_Name)

# Set to path of created FileGDB
GDB = os.path.join(Directory, GDB_Name)

########################################################################
connection_name = "Connection goes here"
database_platform = "SQL_SERVER"
########################################################################
instance = "Instance goes here"
authentication = "DATABASE_AUTH"
username = "Viewer"
password = "viewer"
savePW = "SAVE_USERNAME"
########################################################################
database = "Database goes here"

if not os.path.isdir(Directory):
    os.path.makedirs(Directory)

if not os.path.isfile(connection_name):
    print ("Making connection file")
    arcpy.CreateDatabaseConnection_management(Directory,
                                          connection_name,
                                          database_platform,
                                          instance,
                                          authentication,
                                          username,
                                          password,
                                          savePW,
                                          database)

########################################################################                               
GISProdFDS = r"Feature Dataset for spatial reference goes here"
########################################################################
FeatureClass = r"Feature Class for spatial reference goes here"
FullPathFC = os.path.join(Directory, connection_name, GISProdFDS, FeatureClass)
sr = arcpy.Describe(FullPathFC).spatialReference

arcpy.CreateFeatureDataset_management(GDB,
                                      "BuildingFootprints",
                                      sr)

newFDS = os.path.join(GDB, "BuildingFootprints")

out_path = newFDS
newFC_name = "NewFootprints"
geometry_type = "POLYGON"
template = FullPathFC
has_m = "DISABLED"
has_z = "SAME_AS_TEMPLATE"

arcpy.CreateFeatureclass_management(out_path, newFC_name, geometry_type,
                                    template, has_m, has_z, sr)

print ("New File GDB, fds, and feature class have been created")
########################################################################
FilePathA = r"First part of excel sheet file path"
########################################################################
FilePathB = r"Second part of excle sheet file path. Delete if you don't use"
inputFile = os.path.join(FilePathA, FilePathB)
book = xlrd.open_workbook(inputFile)
sheet = book.sheet_by_index(0)
#iterating over all the rows starting at the 3rd row.
# Populate list with all data in the spreadsheet
inputs = [[sheet.cell(i,col_index).value for col_index in range(sheet.ncols)]
          for i in range(2,sheet.nrows)]

# Go through inputs list (now nested) and build list of addresses found
# in space 1 for this example (id is space 0).
fullAddress = [inputs0[1] for inputs0 in inputs]

##print fullAddress

# Make a list of PINs
pins = [str(int(inputs1[2])) for inputs1 in inputs]

##print pins

# Make a list of Square footage values
SqFt = [(math.sqrt(float(inputs2[3]))/2) for inputs2 in inputs]

# Function to build a list of the parcel centroids (XYs) based on the
# pins in the spreadsheet.
def phatCentroids():
    centroidsList = []
    pinsList = pins
##    print pinsList
########################################################################
    parcelsFC = r"Feature class of parcels to be edited"
    featureClass = os.path.join(Directory, connection_name,
                                GISProdFDS, parcelsFC)
    fields = "SHAPE@XY"
    for pin in pinsList:
        whereClause = "PIN = " + "'" + pin + "'"
        with arcpy.da.SearchCursor(featureClass, fields, whereClause) as cursor:
##            print cursor
            for row in cursor:
##                print "It worked!"
                centroidsList.append(row[0])
                
    print centroidsList
    return centroidsList

# Loop through drawing the footprints based on centroidslist and SqFt list
# after zipping the two lists together
centroidsList = phatCentroids()
fc = os.path.join(newFDS, newFC_name)

def drawSquares(xCoordinate, yCoordinate, SqFt, fc):
    # Calculates and creates an array of vertex points, opens an
    # insert cursor, creates a polygon using the arra, and inserts
    # building into the appropriate database.
    
    vertices = []
    vertices.append(arcpy.Point((xCoordinate + SqFt), (yCoordinate + SqFt)))
    vertices.append(arcpy.Point((xCoordinate + SqFt), (yCoordinate - SqFt)))
    vertices.append(arcpy.Point((xCoordinate - SqFt), (yCoordinate - SqFt)))
    vertices.append(arcpy.Point((xCoordinate - SqFt), (yCoordinate + SqFt)))
    vertices.append(arcpy.Point((xCoordinate + SqFt), (yCoordinate + SqFt)))

    cursor = arcpy.da.InsertCursor( fc, ["SHAPE@"])
    array = arcpy.Array(vertices)
    simpleBuilding = arcpy.Polygon(array)
    cursor.insertRow([simpleBuilding])
            
    del cursor
##    print "Building should be drawn"

for centroids, sideLengthHalf in zip(centroidsList, SqFt):
    drawSquares(centroids[0], centroids[1], sideLengthHalf, fc)
