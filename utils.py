#-*- coding: utf-8 -*-

from vi import html5
from js import CustomEvent
from vi.config import conf

def formatOneEntry(key, format, data, structure = None, prefix = None, language = None, context=None, _rec = 0):
	res = format
	val = data[ key ]

	# Get structure if available
	struct = structure.get( key ) if structure else None
	if isinstance( struct, list ):
		struct = { k: v for k, v in struct }

	if isinstance( val, dict ): # if bone is multilang, only render current lang
		if struct and ("$(%s)" % ".".join( prefix + [ key ] )) in res:
			langs = struct.get( "languages" )
			if langs:
				if language and language in langs:
					val = val.get( language, "" )
				else:
					val = ", ".join([str(value) for value in val.values()])

			else:
				return ""

		else:
			res = formatString( res, val, structure, prefix + [ key ], language, _rec = _rec + 1 )

	elif isinstance( val, list ) and len( val ) > 0 and isinstance( val[ 0 ], dict ): #if bone is relationalbone with rel and dest
		if struct and "dest" in val[ 0 ] and "rel" in val[ 0 ]:
			if "relskel" in struct and "format" in struct:
				format = struct[ "format" ]
				struct = struct[ "relskel" ]

			res = res.replace( "$(%s)" % ".".join( prefix + [ key ] ), ", ".join( [ formatString( format, v, struct, [ ], language, _rec = _rec + 1 ) for v in val ] ) )
		else:
			res = formatString( res, val[ 0 ], struct, prefix + [ key ], language, _rec = _rec + 1 )

	elif isinstance( val, list ): # list values like multistr
		val = ", ".join( map( str, val ) )

	# Check for select-bones
	if isinstance( struct, dict ) and "values" in struct and struct[ "values" ]: #if selectbone translate key to value
		vals = struct[ "values" ]

		if isinstance( vals, list ):
			vals = { k: v for k, v in vals }

		# NO elif!
		if isinstance( vals, dict ):
			if val in vals:
				val = vals[ val ]

	res = res.replace( "$(%s)" % (".".join( prefix + [ key ] )), str( val ) )
	return res

def formatString(format, data, structure = None, prefix = None, language = None, context=None, _rec = 0):
	"""
	Parses a string given by format and substitutes placeholders using values specified by data.

	The syntax for the placeholders is $(%s).
	Its possible to traverse to sub-dictionarys by using a dot as seperator.
	If data is a list, the result each element from this list applied to the given string; joined by ", ".

	Example:

		data = {"name": "Test","subdict": {"a":"1","b":"2"}}
		formatString = "Name: $(name), subdict.a: $(subdict.a)"

	Result: "Name: Test, subdict.a: 1"

	:param format: String containing the format.
	:type format: str

	:param data: Data applied to the format String
	:type data: list | dict

	:param structure: Parses along the structure of the given skeleton.
	:type structure: dict

	:return: The traversed string with the replaced values.
	:rtype: str
	"""

	#if _rec == 0:
	#	print("--- formatString ---")
	#	print(format)
	#	print(data)
	#	print(structure)
	#	print(prefix)
	#	print(language)

	if structure and isinstance(structure, list):
		structure = {k:v for k, v in structure}

	prefix = prefix or []
	res = format

	if isinstance(data,  list):
		return ", ".join([formatString(format, x, structure, prefix, language, _rec = _rec + 1) for x in data])

	elif isinstance(data, str):
		return data

	elif not data:
		return res

	for key in data.keys():
		res = formatOneEntry(key, res, data, structure, prefix, language, context, _rec)

	res = html5.utils.unescape(res) #all strings will be unescaped

	return res


def getImagePreview(data, cropped = False, size = 150):
	if conf["core.version"][0] == 3:
		print(data["downloadUrl"])
		return data["downloadUrl"] #fixme ViUR3
	else:
		if "mimetype" in data.keys() and isinstance(data["mimetype"], str) and data["mimetype"].startswith("image/svg"):
			return "/file/download/%s/%s" % (data["dlkey"], data.get("name", "").replace("\"", ""))

		elif "servingurl" in data.keys():
			if data["servingurl"]:
				return data["servingurl"] + (("=s%d" % size) if size else "") + ("-c" if cropped else "")

			return ""

		return None

def setPreventUnloading(mode = True):
	try:
		count = html5.window.top.preventViUnloading
	except:
		return

	print("setPreventUnloading", count, mode)

	if not mode:
		if count == 0:
			return

	count += (1 if mode else -1)

	html5.window.top.preventViUnloading = count
	return count



class indexeddbConnector():
	dbResult = None
	dbTransaction = None

	def __init__(self,dbName, version=None):
		self.dbName = dbName
		self.dbVersion = version
		self.dbHandler = None
		for dbvar in ["indexedDB"]:#, "mozIndexedDB", "webkitIndexedDB", "msIndexedDB"]:
			if dbvar in dir(html5.window):
				self.dbHandler = getattr(html5.window, dbvar)


	def connect(self):
		#print("Version")
		#print(self.dbVersion)
		self.db = None
		if self.dbVersion:
			self.db = self.dbHandler.open(self.dbName,self.dbVersion)
		else:
			self.db = self.dbHandler.open(self.dbName)
		self.db.addEventListener("error", self.db_error)
		self.db.addEventListener("blocked", self.db_blocked)
		self.db.addEventListener("upgradeneeded", self.db_onupgradeneeded)
		self.db.addEventListener("success", self.db_success)
		return self.db

	def db_error( self,event ):
		print("error")

	def db_blocked( self, events ):
		print( "blocked --------------------------" )

	def db_version( self, event):
		db = event.target
		print('Version changed %s'%db)
		self.dbResult.close()

	def db_onupgradeneeded( self,event ):
		event.target.dispatchEvent(CustomEvent.new("db_update"))
		#self.createObjectStore(event.target,"vi_log")

	def db_success(self, event):
		#event.target.dispatchEvent(CustomEvent.new("upgradeneeded"))
		self.dbResult = self.db.result
		self.dbVersion = self.dbResult.version
		event.target.result.addEventListener("versionchange", self.db_version)
		self.dbTransaction = self.db.transaction
		self.db.dispatchEvent(CustomEvent.new("db_ready"))

class indexeddb():
	queue = []
	dbqueue = []
	def __init__(self,dbName, dbVersion=None):
		self.dbName = dbName
		self.dbVersion = dbVersion
		self.objectStoreNames = []
		self.connect()

	def connect(self):
		dbObj = indexeddbConnector(self.dbName,self.dbVersion)
		db = dbObj.connect()
		db.addEventListener("success", self.db_success)
		return db

	def getList(self,name):
		db = self.connect()
		db.listName = name
		db.addEventListener("db_ready", self._getList)
		return db

	def _getList(self,event):
		name = event.target.listName
		db = event.target
		def fetchedData(event):
			db.dispatchEvent(CustomEvent.new("dataready",{"detail":{"data":event.target.result}}))

		dbResult = event.target.result
		dbTransaction = event.target.result.transaction

		trans = dbTransaction([name], "readwrite")

		StoreHandler = trans.objectStore(name)

		all = StoreHandler.getAll()
		all.addEventListener("success", fetchedData)



	def db_success(self,event):
		self.dbVersion = event.target.result.version
		self.objectStoreNames = event.target.result.objectStoreNames


	def dbAction(self,action,name,key=None,obj=None):
		if action in ["createStore", "deleteStore"]:
			self.dbqueue.append([action, name, key, obj])
			self.dbVersion +=1
		else:
			self.queue.append([action,name,key,obj])
		db = self.connect()

		db.addEventListener("db_ready", self._processQueue)
		db.addEventListener("db_update", self._processDbUpdate)

	def _processDbUpdate(self,event):
		print("READY 2")
		dbResult = event.target.result
		dbTransaction = event.target.result.transaction
		for item in self.dbqueue:
			if item[0] == "createStore":
				self._registerObjectStore(item, dbResult, dbTransaction)
			elif item[0] == "deleteStore":
				self._deleteObjectStore(item, dbResult, dbTransaction)
			else:
				print("UNDEFINED ACTION %s"%item[0])


	def _processQueue(self,event):
		print("READY")
		dbResult = event.target.result
		dbTransaction = event.target.result.transaction

		for item in self.queue:
			if item[0] == "add":
				self._writeToStore(item,dbResult,dbTransaction)
			elif item[0] == "delete":
				self._deleteFromStore(item, dbResult, dbTransaction)
			elif item[0] == "edit":
				self._updateToStore(item, dbResult, dbTransaction)
			else:
				print("UNDEFINED ACTION %s"%item[0])

			self.queue.remove(item)

	def _writeToStore(self,item,dbResult,dbTransaction):
		name = item[1]
		key = item[2]
		obj = item[3]

		trans = dbTransaction([name], "readwrite")
		StoreHandler = trans.objectStore(name)
		if key:
			print("FFFFF")
			print(key)
			StoreHandler.add(obj, key)
		else:
			StoreHandler.add(obj)

	def _deleteFromStore(self,item,dbResult,dbTransaction):
		name = item[1]
		key = item[2]
		obj = item[3]

		trans = dbTransaction([name], "readwrite")
		StoreHandler = trans.objectStore(name)
		StoreHandler.delete(key)

	def _updateToStore(self,item,dbResult,dbTransaction):
		name = item[1]
		key = item[2]
		obj = item[3]

		trans = dbTransaction([name], "readwrite")
		StoreHandler = trans.objectStore(name)

		def update(event):
			result = event.target.result
			print(result)
			print(dir(result))
			for k,v in obj.items():
				setattr(result,k,v)
			print(dir(result))
			StoreHandler.put(result,key)

		currentEntry = StoreHandler.get(key)
		currentEntry.addEventListener("success", update)

	def _deleteObjectStore(self,item,dbResult,dbTransaction):
		name = item[1]
		dbResult.deleteObjectStore(name)
		dbResult.dispatchEvent(CustomEvent.new("versionchange"))

	def _registerObjectStore(self,item,dbResult,dbTransaction):
		name = item[1]
		obj = item[3]
		if not obj:
			obj = {}

		#if "storeOptions" not in obj or obj["storeOptions"] == "default":
		#	obj.update({"autoIncrement": True})

		dbResult.createObjectStore(name, obj)
		dbResult.dispatchEvent(CustomEvent.new("versionchange"))


def mergeDict(original, target):
	for key, value in original.items():
		if isinstance(value, dict):
			node = target.setdefault(key, {})
			mergeDict(value, node)
		else:
			target[key] = value

	return target
