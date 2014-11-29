import slippytiles
import xml.etree.cElementTree as ET
import os, uuid

def GetObjUuid(obj):

	for mem in obj:
		if mem.tag != "tag": continue
		if mem.attrib["k"] != "meta:uuid": continue	
		return uuid.UUID(mem.attrib["v"])

	return None

def UpdateTagInObj(obj, tag, val):
	#Check if already tagged
	done = False
	for mem in obj:
		if mem.tag != "tag": continue
		if mem.attrib["k"] != tag: continue

		#Update existing tag
		mem.attrib["v"] = str(val)
		return

	#Create new tag to contain value
	uuidTag = ET.Element("tag")
	uuidTag.attrib["k"] = tag
	uuidTag.attrib["v"] = str(val)
	obj.append(uuidTag)

class ObjIdMapping(object):
	def __init__(self):
		self.nextExternalId = {'node': 1, 'way': 1, 'relation': 1}
		self.mapping = {'node': {}, 'way': {}, 'relation': {}}
		self.uuids = {}

	def AddId(self, objTy, objInternal, externalId, repoId, tilex, tiley, zoom, uuid):
		self.mapping[objTy][(tilex, tiley, zoom, objInternal)] = externalId
		self.uuids[str(uuid)] = externalId
		if objInternal == 1787634:
			print 1787634

	def GetIdByInternalId(self, objTy, objInternal, tilex, tiley, zoom):
		return self.mapping[objTy][(tilex, tiley, zoom, objInternal)] 

	def GetIdByUuid(self, uuidIn):
		return self.uuids[str(uuidIn)]

	def GetNewExternalId(self, objType):
		oid = self.nextExternalId[str(objType)]
		self.nextExternalId[str(objType)] += 1
		return oid

class CollectedData(object):
	def __init__(self):
		self.data = ET.Element("osm")
		self.data.attrib["version"] = str(0.6)
		self.tree = ET.ElementTree(self.data)
		self.seenUuids = set()

		self.objIdMapping = ObjIdMapping()
	
	def Add(self, obj, repoId, tilex, tiley, zoom):

		if obj.tag == "bounds":
			self.data.append(obj)
			return

		#Find if this object has a uuid
		objUuid = GetObjUuid(obj)

		#Renumber members of object
		if obj.tag == "way":
			for mem in obj:
				if mem.tag != "nd": continue
				nid = int(mem.attrib['ref'])
			
				externalId = self.objIdMapping.GetIdByInternalId("node", nid, tilex, tiley, zoom)

				mem.attrib['ref'] = str(externalId)

		if obj.tag == "relation":
			for mem in obj:
				if mem.tag != "member": continue
				memId = int(mem.attrib['ref'])
				memTy = str(mem.attrib['type'])
			
				externalId = self.objIdMapping.GetIdByInternalId(memTy, memId, tilex, tiley, zoom)

				mem.attrib['ref'] = str(externalId)

		#Write to output
		if objUuid is not None:
			if objUuid in self.seenUuids:
				#This object has already been sent to output
				pass
				#print "already seen:", objUuid
			else:
				#Rewrite object id with new external reference
				objExternalId = self.objIdMapping.GetNewExternalId(obj.tag)
				internalId = int(obj.attrib["id"])
				obj.attrib["id"] = str(objExternalId)

				self.data.append(obj)	

				#Remember this has already been added
				self.seenUuids.add(objUuid)

				#Store mapping
				self.objIdMapping.AddId(str(obj.tag), internalId, objExternalId, repoId, tilex, tiley, zoom, objUuid)

		else:
			objExternalId = self.objIdMapping.GetNewExternalId(obj.tag)
			internalId = int(obj.attrib["id"])
			obj.attrib["id"] = str(objExternalId)
			self.data.append(obj)
			self.objIdMapping.AddId(str(obj.tag), internalId, objExternalId, repoId, tilex, tiley, zoom, objUuid)

	def Save(self):
		self.tree.write("out.xml", encoding="UTF-8")

def ExportFromTile(repoId, tilex, tiley, zoom, pth, out):
	print tilex, tiley, zoom
	fina = os.path.join(pth, str(zoom), str(tilex), str(tiley)+".osm")
	xml = ET.parse(fina)
	xmlRoot = xml.getroot()

	for obj in xmlRoot:
		if obj.tag != "bounds": continue
		out.Add(obj, repoId, tilex, tiley, zoom)

	for obj in xmlRoot:
		if obj.tag != "node": continue
		out.Add(obj, repoId, tilex, tiley, zoom)

	for obj in xmlRoot:
		if obj.tag != "way": continue
		out.Add(obj, repoId, tilex, tiley, zoom)

	for obj in xmlRoot:
		if obj.tag != "relation": continue
		out.Add(obj, repoId, tilex, tiley, zoom)

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
	repoId = 1

	pth = "/home/tim/Desktop/surrey"
	for tilex in range(boundsTL[0], boundsBR[0]+1):
		for tiley in range(boundsTL[1], boundsBR[1]+1):
			ExportFromTile(repoId, tilex, tiley, zoom, pth, out)

	print "Write output"
	out.Save()

if __name__ == "__main__":

	lats = [51.3390982, 51.3485562]
	lons = [-0.8027645, -0.7914039]
	zoom = 12
	ExportBbox(lats, lons, zoom)

	
