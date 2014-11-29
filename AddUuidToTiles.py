import os, string, slippytiles, uuid
import xml.etree.cElementTree as ET

def AddUuidTagToObj(obj, objUuid):
	#Check if already tagged
	done = False
	for mem in obj:
		if mem.tag != "tag": continue
		if mem.attrib["k"] != "meta:uuid": continue

		#Update existing tag
		mem.attrib["v"] = str(objUuid)
		return

	#Create new tag to contain value
	uuidTag = ET.Element("tag")
	uuidTag.attrib["k"] = "meta:uuid"
	uuidTag.attrib["v"] = str(objUuid)
	obj.append(uuidTag)

def AddUuidsToTile(fina, zoom, tilex, tiley, finaOut):
	tree = ET.parse(fina)
	root = tree.getroot()
	bounds1 = slippytiles.num2deg(tilex, tiley, zoom)
	bounds2 = slippytiles.num2deg(tilex+1, tiley+1, zoom)
	lats = [bounds1[0], bounds2[0]]
	lons = [bounds1[1], bounds2[1]]
	latMax, latMin = max(lats), min(lats)
	lonMax, lonMin = max(lons), min(lons)

	namespaceUuid = uuid.UUID("{b3ab2f3c-64ef-4486-82df-643c8657a446}")

	print bounds1, bounds2
	nodesOutside = set()
	observedNodes = set()
	totalNodeCount = 0

	#Add uuid to all objects
	for obj in root:
		if obj.tag != "node": continue
		oid = int(obj.attrib["id"])
		#AddUuidTagToObj(obj, str(uuid.uuid5(namespaceUuid, "node"+str(oid))))
		obj.attrib["uuid"] = str(uuid.uuid5(namespaceUuid, "node"+str(oid)))
		del obj.attrib["id"]
		del obj.attrib["changeset"]
		del obj.attrib["timestamp"]
		del obj.attrib["uid"]
		if "user" in obj.attrib: del obj.attrib["user"]
		del obj.attrib["visible"]
		obj.attrib["lat"] = str(round(float(obj.attrib["lat"]), 8))
		obj.attrib["lon"] = str(round(float(obj.attrib["lon"]), 8))

	for obj in root:
		if obj.tag != "way": continue
		wid = int(obj.attrib["id"])
		#AddUuidTagToObj(obj, str(uuid.uuid5(namespaceUuid, "way"+str(wid))))
		obj.attrib["uuid"] = str(uuid.uuid5(namespaceUuid, "way"+str(wid)))
		del obj.attrib["id"]
		del obj.attrib["changeset"]
		del obj.attrib["timestamp"]
		del obj.attrib["uid"]
		if "user" in obj.attrib: del obj.attrib["user"]
		del obj.attrib["visible"]

		#Convert member nodes
		for mem in obj:
			if mem.tag != "nd": continue
			nid = int(mem.attrib['ref'])
			del mem.attrib['ref']
			mem.attrib['uuid'] = str(uuid.uuid5(namespaceUuid, "node"+str(nid)))

		#Remove unnecessary tags
		toRemove = []
		for mem in obj:
			if mem.tag != "tag": continue
			if mem.attrib["k"] in ["meta:id", "meta:lastEdit"]:
				toRemove.append(mem)
				continue
			

		for tag in toRemove:
			obj.remove(tag)

	for obj in root:
		if obj.tag != "relation": continue
		rid = int(obj.attrib["id"])
		#AddUuidTagToObj(obj, str(uuid.uuid5(namespaceUuid, "relation"+str(rid))))
		obj.attrib["uuid"] = str(uuid.uuid5(namespaceUuid, "relation"+str(rid)))
		del obj.attrib["id"]
		del obj.attrib["changeset"]
		del obj.attrib["timestamp"]
		del obj.attrib["uid"]
		if "user" in obj.attrib: del obj.attrib["user"]
		del obj.attrib["visible"]

		#Convert member objects
		for mem in obj:
			if mem.tag != "member": continue
			memId = int(mem.attrib['ref'])
			memTy = str(mem.attrib['type'])

			del mem.attrib['ref']
			mem.attrib['uuid'] = str(uuid.uuid5(namespaceUuid, memTy+str(memId)))

	tree.write(finaOut)

if __name__ == "__main__":

	pth = "/home/tim/Desktop/surrey"
	pthOut = "/home/tim/Desktop/surrey-uuid"

	if not os.path.exists(pthOut):
		os.mkdir(pthOut)

	#Iterate over zoom levels
	for f in os.listdir(pth):
		if not f.isdigit():
			continue
		zoom = int(f)
		pth1 = os.path.join(pth, f)
		pthOut1 = os.path.join(pthOut, f)

		if not os.path.exists(pthOut1):
			os.mkdir(pthOut1)

		#Iterate over x
		for f2 in os.listdir(pth1):
			tilex = int(f2)
			pth2 = os.path.join(pth1, f2)
			pthOut2 = os.path.join(pthOut1, f2)
			
			if not os.path.exists(pthOut2):
				os.mkdir(pthOut2)

			for f3 in os.listdir(pth2):
				f3split = os.path.splitext(f3)
				tiley = int(f3split[0])
				fina = os.path.join(pth2, f3)
				finaOut = os.path.join(pthOut2, f3)

				print fina
				AddUuidsToTile(fina, zoom, tilex, tiley, finaOut)

