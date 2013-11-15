# -*- coding: utf-8 -*-

import html5
from network import NetworkService
from config import conf
from priorityqueue import editBoneSelector
from widgets.tooltip import ToolTip
from priorityqueue import protocolWrapperInstanceSelector
from widgets.actionbar import ActionBar


class EditWidget( html5.Div ):
	appList = "list"
	appHierarchy = "hierarchy"
	appTree = "tree"
	appSingleton = "singleton"

	def __init__(self, modul, applicationType, key=0, node=None, skelType=None, clone=False, *args, **kwargs ):
		"""
			Initialize a new Edit or Add-Widget for the given modul.
			@param modul: Name of the modul
			@type modul: String
			@param applicationType: Defines for what application this Add / Edit should be created. This hides additional complexity introduced by the hierarchy / tree-application
			@type applicationType: Any of EditWidget.appList, EditWidget.appHierarchy, EditWidget.appTree or EditWidget.appSingleton
			@param id: ID of the entry. If none, it will add a new Entry.
			@type id: Number
			@param rootNode: If applicationType==EditWidget.appHierarchy, the new entry will be added under this node, if applicationType==EditWidget,appTree the final node is derived from this and the path-parameter. 
			Has no effect if applicationType is not appHierarchy or appTree or if an id have been set.
			@type rootNode: String
			@param path: Specifies the path from the rootNode for new entries in a treeApplication
			@type path: String
			@param clone: If true, it will load the values from the given id, but will save a new entry (i.e. allows "cloning" an existing entry)
			@type clone: Bool
		"""
		super( EditWidget, self ).__init__( *args, **kwargs )
		self.modul = modul
		# A Bunch of santy-checks, as there is a great chance to mess around with this widget
		assert applicationType in [ EditWidget.appList, EditWidget.appHierarchy, EditWidget.appTree, EditWidget.appSingleton ] #Invalid Application-Type?
		if applicationType==EditWidget.appHierarchy or applicationType==EditWidget.appTree:
			assert id is not None or node is not None #Need either an id or an node
		if clone:
			assert id is not None #Need an id if we should clone an entry
			assert not applicationType==EditWidget.appSingleton # We cant clone a singleton
			if applicationType==EditWidget.appHierarchy or applicationType==EditWidget.appTree:
				assert node is not None #We still need a rootNode for cloning
			if applicationType==EditWidget.appTree:
				assert path is not None #We still need a path for cloning #FIXME
		# End santy-checks
		self.applicationType = applicationType
		self.key = key
		self.node = node
		self.skelType = skelType
		self.clone = clone
		self.bones = {}
		self.closeOnSuccess = False
		self._lastData = {} #Dict of structure and values recived
		self.editTaskID = None
		self.actionbar = ActionBar( self.modul, self.applicationType, "edit" )
		self.appendChild( self.actionbar )
		self.form = html5.Form()
		self.appendChild(self.form)
		self.actionbar.setActions(["save.close","save.continue","reset"])
		self.reloadData( )



	def onBusyStateChanged( self, busy ):
		if busy:
			self.overlay.inform( self.overlay.BUSY )
		else:
			self.overlay.clear()

	def getBreadCrumb( self ):
		if self._lastData:
			config = conf.serverConfig["modules"][ self.modul ]
			if "format" in config.keys():
				format = config["format"]
			else:
				format = "$(name)"
			itemName = formatString( format, self._lastData["structure"], self._lastData["values"] )
		else:
			itemName = ""
		if self.clone:
			if itemName:
				descr = QtCore.QCoreApplication.translate("EditWidget", "Clone: %s") % itemName
			else:
				descr = QtCore.QCoreApplication.translate("EditWidget", "Clone entry")
			icon = QtGui.QIcon( "icons/actions/clone.png" )
		elif self.key or self.applicationType == EditWidget.appSingleton: #Were editing
			if itemName:
				descr = QtCore.QCoreApplication.translate("EditWidget", "Edit: %s") % itemName
			else:
				descr = QtCore.QCoreApplication.translate("EditWidget", "Edit entry")
			icon = QtGui.QIcon( "icons/actions/edit.svg" )
		else: #Were adding 
			descr = QtCore.QCoreApplication.translate("EditWidget", "Add entry") #We know that we cant know the name yet
			icon = QtGui.QIcon( "icons/actions/add.svg" )
		return( descr, icon )
		
	
	def onBtnCloseReleased(self, *args, **kwargs):
		event.emit( "popWidget", self )

	def reloadData(self):
		print("--RELOADING--")
		self.save( {} )
		return

	def save(self, data ):
		if self.modul=="_tasks":
			self.editTaskID = protoWrap.edit( self.key, **data )
			#request = NetworkService.request("/%s/execute/%s" % ( self.modul, self.id ), data, secure=True, successHandler=self.onSaveResult )
		elif self.applicationType == EditWidget.appList: ## Application: List
			if self.key and (not self.clone or not data):
				#self.editTaskID = protoWrap.edit( self.key, **data )
				NetworkService.request(self.modul,"edit/%s" % self.key, data, secure=len(data)>0, successHandler=self.setData)
			else:
				NetworkService.request(self.modul, "add", data, secure=len(data)>0, successHandler=self.setData )
				#self.editTaskID = protoWrap.add( **data )
		elif self.applicationType == EditWidget.appHierarchy: ## Application: Hierarchy
			if self.key and not self.clone:
				NetworkService.request(self.modul,"edit/%s" % self.key, data, secure=len(data)>0, successHandler=self.setData)
				#self.editTaskID = protoWrap.edit( self.key, **data )
			else:
				NetworkService.request(self.modul, "add/%s" % self.node, data, secure=len(data)>0, successHandler=self.setData )
				#self.editTaskID = protoWrap.add( self.node, **data )
		elif self.applicationType == EditWidget.appTree: ## Application: Tree
			if self.key and not self.clone:
				NetworkService.request(self.modul,"edit/%s/%s" % (self.skelType,self.key), data, secure=len(data)>0, successHandler=self.setData)
				#self.editTaskID = protoWrap.edit( self.key, self.skelType, **data )
			else:
				NetworkService.request(self.modul,"add/%s/%s" % (self.skelType,self.node), data, secure=len(data)>0, successHandler=self.setData)
				#self.editTaskID = protoWrap.add( self.node, self.skelType, **data )
		elif self.applicationType == EditWidget.appSingleton: ## Application: Singleton
			#self.editTaskID = protoWrap.edit( **data )
			NetworkService.request(self.modul,"edit", data, secure=len(data)>0, successHandler=self.setData)
		else:
			raise NotImplementedError() #Should never reach this

	def onBtnResetReleased( self, *args, **kwargs ):
		res = QtGui.QMessageBox.question(	self,
						QtCore.QCoreApplication.translate("EditWidget", "Confirm reset"),
						QtCore.QCoreApplication.translate("EditWidget", "Discard all unsaved changes?"),
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No
						)
		if res == QtGui.QMessageBox.Yes:
			self.setData( data=self.dataCache )

	def parseHelpText( self, txt ):
		"""Parses the HTML-Text txt and returns it with remote Images replaced with their local copys
		
		@type txt: String
		@param txt: HTML-Text
		@return: String
		"""
		res = ""
		while txt:
			idx = txt.find("<img src=")
			if idx==-1:
				res += txt
				return( res )
			startpos = txt.find( "\"", idx+8)+1
			endpos = txt.find( "\"", idx+13)
			url = txt[ startpos:endpos ]
			res += txt[ : startpos ]
			res += getFileName( url ) #FIXME: BROKEN
			txt = txt[ endpos : ]
		
		fileName = os.path.join( conf.currentPortalConfigDirectory, sha1(dlkey.encode("UTF-8")).hexdigest() )
		if not os.path.isfile( fileName ):
			try:
				data = NetworkService.request( dlkey )
			except:
				return( None )
			open( fileName, "w+b" ).write( data )	
		return( fileName )

	def clear(self):
		for c in self.form._children[ : ]:
			self.form.removeChild( c )


	def setData( self, request=None, data=None, ignoreMissing=False ):
		"""
		Rebuilds the UI according to the skeleton received from server
		
		@type data: dict
		@param data: The data recived
		"""
		assert (request or data)
		if request:
			data = NetworkService.decode( request )
		if "action" in data and (data["action"] == "addSuccess" or data["action"] == "editSuccess"):
			NetworkService.notifyChange(self.modul)
			self.clear()
			self.bones = {}
			self.reloadData()
			return
		#Clear the UI
		self.clear()
		self.bones = {}
		self.dataCache = data
		tmpDict = {}
		fieldSets = {}
		for key, bone in data["structure"]:
			tmpDict[ key ] = bone
		currRow = 0
		for key, bone in data["structure"]:
			if bone["visible"]==False:
				continue
			cat = "default"
			if "params" in bone.keys() and isinstance(bone["params"],dict) and "category" in bone["params"].keys():
				cat = bone["params"]["category"]
			if not cat in fieldSets.keys():
				fs = html5.Fieldset()
				fs["class"] = cat
				fs["id"] = "vi_%s_%s_%s" % (self.modul, "edit" if self.key else "add", cat)
				fs["name"] = cat
				legend = html5.Legend()
				legend["id"] = "vi_%s_%s_%s_legend" % (self.modul, "edit" if self.key else "add", cat)
				legend.appendChild( html5.TextNode(cat))
				fs.appendChild(legend)
				fieldSets[ cat ] = fs
			if "params" in bone.keys() and bone["params"] and "category" in bone["params"].keys():
				tabName = bone["params"]["category"]
			else:
				tabName = "Test"#QtCore.QCoreApplication.translate("EditWidget", "General")

			wdgGen = editBoneSelector.select( self.modul, key, tmpDict )
			widget = wdgGen.fromSkelStructure( self.modul, key, tmpDict )
			widget["id"] = "vi_%s_%s_%s_bn_%s" % (self.modul, "edit" if self.key else "add", cat, key)
			widget["class"].append(key)
			widget["class"].append(bone["type"])
			#self.prepareCol(currRow,1)
			descrLbl = html5.Label(bone["descr"])
			descrLbl["class"].append(key)
			descrLbl["class"].append(bone["type"])
			descrLbl["for"] = "vi_%s_%s_%s_bn_%s" % (self.modul, "edit" if self.key else "add", cat, key)
			if bone["required"]:
				descrLbl["class"].append("is_required")
			if bone["required"] and bone["error"] is not None:
				descrLbl["class"].append("is_invalid")
				descrLbl["title"] = bone["error"]
			if "params" in bone.keys() and isinstance(bone["params"], dict) and "tooltip" in bone["params"].keys():
				tmp = html5.Span()
				tmp.appendChild(descrLbl)
				tmp.appendChild( ToolTip(longText=bone["params"]["tooltip"]) )
				descrLbl = tmp
			fieldSets[ cat ].appendChild( descrLbl )
			#self["cell"][currRow][0] = descrLbl
			fieldSets[ cat ].appendChild( widget )
			#self["cell"][currRow][1] = widget
			currRow += 1
			self.bones[ key ] = widget
		tmpList = [(k,v) for (k,v) in fieldSets.items()]
		tmpList.sort( key=lambda x:x[0])
		for k,v in tmpList:
			self.form.appendChild( v )
		self.unserialize( data["values"] )
		self._lastData = data

	def unserialize(self, data):
		for bone in self.bones.values():
			bone.unserialize( data )

	"""def onBtnSaveContinueReleased(self, *args, **kwargs ):
		print( "BTN CLICK RECIVED")
		self.closeOnSuccess = False
		#self.overlay.inform( self.overlay.BUSY )
		res = {}
		for key, bone in self.bones.items():
			res.update( bone.serializeForPost( ) )
		self.save( res )
	"""
		
	def doSave( self, closeOnSuccess=False, *args, **kwargs ):
		self.closeOnSuccess = closeOnSuccess
		res = {}
		for key, bone in self.bones.items():
			res.update( bone.serializeForPost( ) )
		self.save( res )


	def onBtnPreviewReleased( self, *args, **kwargs ):
		res = {}
		for key, bone in self.bones.items():
			res.update( bone.serializeForPost() )
		self.preview = Preview( self.modul, res )
	
	def onSaveSuccess( self, editTaskID ):
		"""
			Adding/editing an entry just succeeded
		"""
		if editTaskID!=self.editTaskID: #Not our task
			return
		self.overlay.inform( self.overlay.SUCCESS, QtCore.QCoreApplication.translate("EditWidget", "Entry saved")  )
		if self.closeOnSuccess:
			event.emit( 'popWidget', self )
		else:
			self.reloadData()
	
	def onDataAvaiable( self, editTaskID, data, wasInitial ):
		"""
			Adding/editing failed, cause some required fields are missing/invalid
		"""
		if editTaskID!=self.editTaskID: #Not our task
			return
		self.setData( data=data, ignoreMissing=wasInitial )
		if not wasInitial:
			self.overlay.inform( self.overlay.MISSING, QtCore.QCoreApplication.translate("EditWidget", "Missing data") )
		
	
	def onSaveError( self, error ):
		"""
			Unspecified error on saving/editing
		"""
		self.overlay.inform( self.overlay.ERROR, QtCore.QCoreApplication.translate("EditWidget", "There was an error saving your changes") )
		return
	

	def taskAdded(self):
		QtGui.QMessageBox.information(	self,
									QtCore.QCoreApplication.translate("EditWidget", "Task created"), 
									QtCore.QCoreApplication.translate("EditWidget", "The task was sucessfully created."), 
									QtCore.QCoreApplication.translate("EditWidget", "Okay") )
		self.parent().deleteLater()
