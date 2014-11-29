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

	#Find nodes outside
	for obj in root:
		if obj.tag != "node": continue
		lat, lon, nid = float(obj.attrib['lat']), float(obj.attrib['lon']), int(obj.attrib['id'])
		totalNodeCount += 1
		observedNodes.add(nid)
		#print lat, lon, nid

		if lat <= latMin or lat >= latMax:
			nodesOutside.add(nid)
			continue
		if lon <= lonMin or lon >= lonMax:
			nodesOutside.add(nid)
			continue

	print "Num nodes outside", len(nodesOutside), "of", totalNodeCount, "outside"

	#Find ways outside
	waysOutside = set()
	totalWayCount = 0
	observedWays = set()

	for obj in root:
		if obj.tag != "way": continue
		wid = int(obj.attrib["id"])
		totalWayCount += 1
		observedWays.add(wid)

		for wayMem in obj:
			if wayMem.tag != "nd": continue
			nid = int(wayMem.attrib['ref'])
			if nid in nodesOutside:
				waysOutside.add(wid)

	print "Ways", len(waysOutside),"of",totalWayCount, "outside"

	#Check relations that need uuids
	relationsOutside = set()
	totalRelationCount=  0
	for obj in root:
		if obj.tag != "relation": continue
		rid = int(obj.attrib["id"])
		totalRelationCount += 1

		#print obj.attrib
		outside = False
		for relMem in obj:
			if relMem.tag != "member": continue
			#print relMem.tag, relMem.attrib
			memTy = relMem.attrib["type"]
			memRef = int(relMem.attrib["ref"])
			if memTy == "node" and (memRef in nodesOutside or memRef not in nodesOutside):
				outside = True
				break
			if memTy == "way" and (memRef in waysOutside or memRef not in observedWays):
				outside = True
				break

		if outside:
			relationsOutside.add(rid)

	print "Relations", len(relationsOutside), "of", totalRelationCount, "outside"

	#Find first generation children of outside relations
	firstGenChildren = {'node': set(), 'way': set(), 'relation': set()}

	for obj in root:
		if obj.tag != "relation": continue
		rid = int(obj.attrib["id"])
		if rid not in relationsOutside: continue
		for mem in obj:
			if mem.tag != "member": continue
			childTy = mem.attrib["type"]
			childRef = int(mem.attrib["ref"])
			firstGenChildren[childTy].add(childRef)

	for obj in root:
		if obj.tag != "way": continue
		rid = int(obj.attrib["id"])
		if rid not in waysOutside: continue
		for mem in obj:
			if mem.tag != "nd": continue
			childRef = int(mem.attrib["ref"])
			firstGenChildren["node"].add(childRef)

	print "First gen child nodes", len(firstGenChildren["node"])
	print "First gen child ways", len(firstGenChildren["way"])
	print "First gen child relations", len(firstGenChildren["relation"])

	#Add uuid to objects
	for obj in root:
		if obj.tag != "node": continue
		oid = int(obj.attrib["id"])
		if oid in firstGenChildren["node"]:
			AddUuidTagToObj(obj, str(uuid.uuid5(namespaceUuid, "node"+str(oid))))

	for obj in root:
		if obj.tag != "way": continue
		wid = int(obj.attrib["id"])
		if wid in waysOutside or wid in firstGenChildren["way"]:
			AddUuidTagToObj(obj, str(uuid.uuid5(namespaceUuid, "way"+str(wid))))

	for obj in root:
		if obj.tag != "relation": continue
		rid = int(obj.attrib["id"])
		if rid in relationsOutside or rid in firstGenChildren["relation"]:
			AddUuidTagToObj(obj, str(uuid.uuid5(namespaceUuid, "relation"+str(rid))))

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

