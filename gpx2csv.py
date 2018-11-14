import argparse
import csv
import logging
import os
import sys
import xml.etree.ElementTree as ET

# Configure a logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

####
# Prompts the user for a yes no answer to a question
#
# PARAMS:
#       question: The question to ask the user
#       default: The default response to the question
####
def getYesNo(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with a 'yes' or 'no' (or 'y' or 'n').\n")

####
# Parses the GPX to get all of the waypoints
#
# Returns a list of waypoints and their attributes
####
def parseGPX(gpx_path):
    # Setup the GPX namespace
    namespace = {"gpx": "http://www.topografix.com/GPX/1/1"}

    # Start parsing the GPX XML
    gpxTree = ET.parse(gpx_path)
    root = gpxTree.getroot()

    # Create list to store the GPX items
    waypoints = []

    # Iterate over all of the waypoints
    for waypoint in root.findall("gpx:wpt", namespace):
        wpt = {'lat': waypoint.attrib['lat'], 'lon': waypoint.attrib['lon'], 'ele': '', 'time': '', 'name': '', 'desc': ''}

        for item in waypoint:
            if item.tag == "{http://www.topografix.com/GPX/1/1}ele":
                wpt['ele'] = item.text.encode('utf-8')
            if item.tag == '{http://www.topografix.com/GPX/1/1}time':
                wpt['time'] = item.text.encode('utf-8')
            if item.tag == '{http://www.topografix.com/GPX/1/1}name':
                wpt['name'] = item.text.encode('utf-8')
            if item.tag == '{http://www.topografix.com/GPX/1/1}desc':
                wpt['desc'] = item.text.encode('utf-8')

        waypoints.append(wpt)

    return waypoints


####
# Coverts the GPX file to a CSV file
####
def convertGPX(gpx_path, csv_path, overwriteCSV=False):
    if os.path.isfile(csv_path) and not overwriteCSV:
        logger.error(csv_path + " already exists. Exiting...")
        sys.exit() # Nothing we can do here
    if not os.path.isfile(gpx_path):
        logger.error(gpx_path + " does not exis.encode('utf-8')t. Exiting...")
        sys.exit() # Nothing to work with!

    # Get the waypoints from the GPX file
    waypoints = parseGPX(gpx_path)

    # Write the data to CSV
    csvFields = ['name', 'lat', 'lon', 'ele', 'desc', 'time']

    with open(csv_path, 'w') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames = csvFields)
        writer.writeheader()

        writer.writerows(waypoints)


# Handle the command line arguments
parser = argparse.ArgumentParser(description="A simple utility to convert GPX files to a CSV file.")
parser.add_argument("--input", dest="gpx_path", help="Path to the GPX file")
parser.add_argument("--output", dest="csv_path", help="Path to the resulting CSV file")
args = parser.parse_args()

# Rather or not to overwrite an existing CSV file
overwriteCSV = False

if not args.gpx_path or not args.csv_path:
    logger.error("You must supply an input and output!");
elif not os.path.isfile(args.gpx_path):
    logger.error("The input GPX file " + args.gpx_path + " does not exist")
elif os.path.isfile(args.csv_path):
    if getYesNo("'%s' exists. Overwrite it?" % args.csv_path):
        overwriteCSV = True
    else:
        # Output already exists and user doesn't want to overwrite it, exit...
        sys.exit()
else:
    logger.info("Converting GPX file " + args.gpx_path + " to a CSV file...")
    convertGPX(args.gpx_path, args.csv_path, overwriteCSV)
