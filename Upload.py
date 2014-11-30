import slippytiles
import xml.etree.cElementTree as ET
import os, uuid



if __name__ == "__main__":

	fina = "mod.osm"
	xml = ET.parse(fina)
	root = xml.getroot()
	

	#Check which tiles contain the nodes
	for obj in root:
		if obj.tag != "node":
			continue
		print float(obj.attrib['lat']), float(obj.attrib['lat'])
	
