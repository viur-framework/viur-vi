from flare import html5,utils
from flare.viur.formatString import formatString as fl_formatString
from js import CustomEvent
from vi.config import conf
from pyodide import to_js
import pyodide


def render_url(url, module, entry=None, **kwargs):
	"""
	Renders a URL that contains {{variables}}, e.g. for previews.
	"""
	url = url.replace("{{modul}}", module)  # fixme: fallback for very old definitions
	url = url.replace("{{module}}", module)

	if conf["updateParams"]:
		for k, v in conf["default_params"].items():
			url = url.replace("{{%s}}" % k, str(v))

	if entry:
		for k, v in entry.items():
			url = url.replace("{{%s}}" % k, str(v))

	for k, v in kwargs.items():
		url = url.replace("{{%s}}" % k, str(v))

	return url.replace("'", "\\'")


def formatString(format, data, structure = None, language = None):
	"""
	Parses a string given by format and substitutes placeholders using values specified by data.
	"""
	return fl_formatString(format,data,structure,language)

def getImagePreview(data, cropped = False, size = 150):
	return data["downloadUrl"]

def setPreventUnloading(mode = True):
	try:
		count = html5.window.preventViUnloading
	except:
		return

	# print("setPreventUnloading", count, mode)

	if not mode:
		if count == 0:
			return

	count += (1 if mode else -1)

	html5.window.preventViUnloading = count
	return count



class indexeddbConnector():
	dbResult = None
	dbTransaction = None

	def __init__(self,dbName, version=None):
		self.dbName = dbName
		self.dbVersion = version or 0
		self.dbHandler = None
		for dbvar in ["indexedDB"]:#, "mozIndexedDB", "webkitIndexedDB", "msIndexedDB"]:
			if dbvar in dir(html5.window):
				self.dbHandler = getattr(html5.window, dbvar)


	def connect(self):
		self.db = None
		if self.dbVersion:
			self.db = self.dbHandler.open(self.dbName,self.dbVersion)
		else:
			self.db = self.dbHandler.open(self.dbName)
		self.db.addEventListener("error",  pyodide.create_proxy(self.db_error))
		self.db.addEventListener("blocked", pyodide.create_proxy(self.db_blocked))
		self.db.addEventListener("upgradeneeded", pyodide.create_proxy(self.db_onupgradeneeded))
		self.db.addEventListener("success", pyodide.create_proxy(self.db_success))
		return self.db

	def db_error( self,event ):
		print("error")

	def db_blocked( self, events ):
		print( "blocked --------------------------" )

	def db_version( self, event):
		db = event.target.version
		print('Version changed %s'%db)
		self.dbResult.close()

	def db_onupgradeneeded( self,event ):
		event.target.dispatchEvent(CustomEvent.new("db_update"))

	def db_success(self, event):
		self.dbResult = self.db.result
		self.dbVersion = self.dbResult.version
		event.target.result.addEventListener("versionchange", pyodide.create_proxy(self.db_version))
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
		db.addEventListener("success", pyodide.create_proxy(self.db_success))
		return db

	def getList(self,name):
		db = self.connect()
		db.listName = name
		db.addEventListener("db_ready", pyodide.create_proxy(self._getList))
		return db

	def _getList(self,event):
		name = event.target.listName
		db = event.target
		def fetchedData(event):
			db.dispatchEvent(CustomEvent.new("dataready",detail=to_js({"data":event.target.result})))

		dbResult = event.target.result
		dbTransaction = event.target.result.transaction
		trans = dbTransaction([name], "readwrite")
		StoreHandler = trans.objectStore(name)

		all = StoreHandler.getAll()
		all.addEventListener("success", pyodide.create_proxy(fetchedData))


	def getListKeys( self,name ):
		db = self.connect()
		db.listName = name
		db.addEventListener( "db_ready", pyodide.create_proxy(self._getListKey ))
		return db

	def _getListKey(self,event):
		name = event.target.listName
		db = event.target
		def fetchedData(event):
			db.dispatchEvent(CustomEvent.new("dataready",detail=to_js({"data":event.target.result})))


		dbResult = event.target.result
		dbTransaction = event.target.result.transaction
		trans = dbTransaction([name], "readwrite")
		StoreHandler = trans.objectStore(name)

		all = StoreHandler.getAllKeys()
		all.addEventListener("success", pyodide.create_proxy(fetchedData))

	def db_success(self,event):
		self.dbVersion = event.target.result.version
		self.objectStoreNames = event.target.result.objectStoreNames


	def dbAction(self,action,name,key=None,obj=None):
		if action in ["createStore", "deleteStore"]:
			self.dbqueue.append([action, name, key, obj])

			if self.dbVersion is None:
				self.dbVersion = 0

			self.dbVersion +=1
		else:
			self.queue.append([action,name,key,obj])
		db = self.connect()

		db.addEventListener("db_ready", pyodide.create_proxy(self._processQueue))
		db.addEventListener("db_update", pyodide.create_proxy(self._processDbUpdate))

	def _processDbUpdate(self,event):
		#print("READY 2")
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
		#print("READY")
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
			StoreHandler.add(to_js(obj), key)
		else:
			StoreHandler.add(to_js(obj))

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
			for k,v in obj.items():
				setattr(result,k,v)
			StoreHandler.put(result,key)

		currentEntry = StoreHandler.get(key)
		currentEntry.addEventListener("success", pyodide.create_proxy(update))

	def _deleteObjectStore(self,item,dbResult,dbTransaction):
		name = item[1]
		dbResult.deleteObjectStore(name)
		dbResult.dispatchEvent(CustomEvent.new("versionchange"))

	def _registerObjectStore(self,item,dbResult,dbTransaction):
		name = item[1]
		obj = item[3]
		if not obj:
			obj = {}

		dbResult.createObjectStore(name, **obj)
		dbResult.dispatchEvent(CustomEvent.new("versionchange"))


def mergeDict(original, target):
	for key, value in original.items():
		if isinstance(value, dict):
			node = target.setdefault(key, {})
			mergeDict(value, node)
		else:
			target[key] = value

	return target
