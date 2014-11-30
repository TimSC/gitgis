import slippytiles
import xml.etree.cElementTree as ET
import os, uuid

def GetObjUuid(obj):
	return uuid.UUID(obj.attrib["uuid"])

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
		self.uuids = {}

	def AssignExternalId(self, objTy, objUuid):
		#Check if the uuid already has an external ID
		if str(objUuid) in self.uuids:
			return self.uuids[str(objUuid)]

		#Assign new external id
		externalId = self.nextExternalId[objTy]
		self.nextExternalId[objTy] += 1
		self.uuids[str(objUuid)] = externalId
		return externalId

	def AssignExternalIdToObj(self, obj):
		#Check if the uuid already has an external ID
		objUuid = GetObjUuid(obj)
		if str(objUuid) in self.uuids:
			return self.uuids[str(objUuid)]

		#Assign new external id
		externalId = self.nextExternalId[str(obj.tag)]
		self.nextExternalId[str(obj.tag)] += 1
		self.uuids[str(objUuid)] = externalId
		return externalId

class CollectedData(object):
	def __init__(self):
		self.data = ET.Element("osm")
		self.data.attrib["version"] = str(0.6)
		self.data.attrib["upload"] = "true"
		self.data.attrib["generator"] = "py"
		self.tree = ET.ElementTree(self.data)
		self.seenUuids = set()

		self.objIdMapping = ObjIdMapping()
	
	def Add(self, obj, repoId, tilex, tiley, zoom):

		if obj.tag == "bounds":
			self.data.append(obj)
			return

		#Find if this object has a uuid
		objUuid = GetObjUuid(obj)

		if obj.tag == "way":
			#Renumber members of way
			for mem in obj:
				if mem.tag != "nd": continue
				nuuid = uuid.UUID(mem.attrib['uuid'])

				externalId = self.objIdMapping.AssignExternalId("node", nuuid)

				mem.attrib['ref'] = str(externalId)
				del mem.attrib['uuid']

		if obj.tag == "relation":
			#Renumber members of relation
			for mem in obj:
				if mem.tag != "member": continue
				memUuid = uuid.UUID(mem.attrib['uuid'])
				memTy = str(mem.attrib['type'])
			
				#This function must handle incomplete relations that have not yet had uuids assigned
				externalId = self.objIdMapping.AssignExternalId(memTy, memUuid)

				mem.attrib['ref'] = str(externalId)
				del mem.attrib['uuid']

		#Write to output
		if objUuid is not None:
			if objUuid in self.seenUuids:
				#This object has already been sent to output
				pass
				#print "already seen:", objUuid
			else:
				#Rewrite object id with new external reference
				objExternalId = self.objIdMapping.AssignExternalIdToObj(obj)
				obj.attrib["id"] = str(objExternalId)
				del obj.attrib['uuid']

				self.data.append(obj)	

				#Remember this has already been added
				self.seenUuids.add(objUuid)

		else:
			objExternalId = self.objIdMapping.AssignExternalIdToObj(obj)
			internalId = int(obj.attrib["id"])
			obj.attrib["id"] = str(objExternalId)
			del obj.attrib['uuid']
			self.data.append(obj)

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

	
