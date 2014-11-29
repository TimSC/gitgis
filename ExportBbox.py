import slippytiles
import xml.etree.cElementTree as ET
import os, uuid

def GetObjUuid(obj):

	for mem in obj:
		if mem.tag != "tag": continue
		if mem.attrib["k"] != "meta:uuid": continue	
		return uuid.UUID(mem.attrib["v"])

	return None

class CollectedData(object):
	def __init__(self):
		self.data = ET.Element("osm")
		self.data.attrib["version"] = str(0.6)
		self.tree = ET.ElementTree(self.data)
		self.seenUuids = set()
	
	def Add(self, obj):
		objUuid = GetObjUuid(obj)
		if objUuid is not None:
			if objUuid in self.seenUuids:
				print "already seen:", objUuid
			else:
				self.seenUuids.add(objUuid)

		self.data.append(obj)

	def Save(self):
		self.tree.write("out.xml")

def ExportFromTile(tilex, tiley, zoom, pth, out):
	print tilex, tiley, zoom
	fina = os.path.join(pth, str(zoom), str(tilex), str(tiley)+".osm")
	xml = ET.parse(fina)
	xmlRoot = xml.getroot()

	for obj in xmlRoot:
		#Is object a shared obj?
		#objUuid = GetObjUuid(obj)
		out.Add(obj)

def ExportBbox(lats, lons, zoom):

	latMin, latMax = min(lats), max(lats)
	lonMin, lonMax = min(lons), max(lons)
	print "lat", latMin, latMax
	print "lon", lonMin, lonMax

	boundsTL = slippytiles.deg2num(latMax, lonMin, zoom)
	boundsBR = slippytiles.deg2num(latMin, lonMax, zoom)
	print boundsTL
	print boundsBR

	out = CollectedData()

	pth = "/home/tim/Desktop/surrey"
	for tilex in range(boundsTL[0], boundsBR[0]+1):
		for tiley in range(boundsTL[1], boundsBR[1]+1):
			ExportFromTile(tilex, tiley, zoom, pth, out)

	out.Save()

if __name__ == "__main__":

	lats = [51.3390982, 51.3485562]
	lons = [-0.8027645, -0.7914039]
	zoom = 12
	ExportBbox(lats, lons, zoom)

	
