from flare import html5
from flare.popup import Confirm
from vi.config import conf
from flare.i18n import translate
from flare.network import NetworkService,requestGroup,DeferredCall
from vi.priorityqueue import actionDelegateSelector
from flare.button import Button
from vi.widgets.edit import EditWidget

class AddLeafAction(Button):
	"""
		Creates a new leaf (ie. a file) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( translate("Add"), icon="icon-add")
		self["class"] = "bar-item btn btn--small btn--add-leaf btn--primary"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add.leaf"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add-leaf" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		conf[ "mainWindow" ].openView(
			translate( "Add" ),  # AnzeigeName
			"icon-add",  # Icon
			"edithandler",  # viewName
			self.parent().parent().module,  # Modulename
			"add",  # Action
			data = { "context": self.parent().parent().context,
					 "baseType":EditWidget.appTree,
					 "node":self.parent().parent().node,
					 "skelType":"leaf"
			},
			target = "popup" if self.parent().parent().isSelector else "mainNav"
		)


	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddLeafAction.isSuitableFor, AddLeafAction )


class AddNodeAction(Button):
	"""
		Creates a new node (ie. a directory) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddNodeAction, self ).__init__(  translate("Add"), icon="icon-add-folder")
		self["class"] = "bar-item btn btn--small btn--add-node"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add.node"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add-node" in conf["modules"][module]["disabledFunctions"]

		return  correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		conf[ "mainWindow" ].openView(
			translate( "Add" ),  # AnzeigeName
			"icon-add",  # Icon
			"edithandler",  # viewName
			self.parent().parent().module,  # Modulename
			"add",  # Action
			data = { "context" : self.parent().parent().context,
					 "baseType": EditWidget.appTree,
					 "node"    : self.parent().parent().node,
					 "skelType": "node"
					 },
			target = "popup" if self.parent().parent().isSelector else "mainNav"
		)



	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddNodeAction.isSuitableFor, AddNodeAction )


class EditAction(Button):
	"""
		Edits an entry inside a tree application.
		The type (node or leaf) of the entry is determined dynamically
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__(  translate("Edit"), icon="icon-edit")
		self["class"] = "bar-item btn btn--small btn--edit"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(EditAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )
		self.parent().parent().selectionActivatedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		self.parent().parent().selectionActivatedEvent.unregister( self )
		super(EditAction,self).onDetach()

	def onSelectionActivated(self, table, selection ):
		if (not self.parent().parent().selectionCallback
			and len(selection) == 1
			and isinstance(selection[0], self.parent().parent().leafWidget)):

			if isinstance( selection[0], self.parent().parent().nodeWidget):
				skelType = "node"

			elif isinstance( selection[0], self.parent().parent().leafWidget):
				skelType = "leaf"

			else:
				raise ValueError("Unknown selection type: %s" % str(type(selection[0])))

			conf[ "mainWindow" ].openView(
				translate( "Edit" ),  # AnzeigeName
				"icon-edit",  # Icon
				"edithandler",  # viewName
				self.parent().parent().module,  # Modulename
				"edit",  # Action
				data = { "context" : self.parent().parent().context,
						 "baseType": EditWidget.appTree,
						 "skelType": skelType,
						 "key"     : selection[0].data["key"]
						 },
				target = "popup" if self.parent().parent().isSelector else "mainNav"
			)

	def onSelectionChanged(self, table, selection, *args,**kwargs ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="edit"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "edit" in conf["modules"][module]["disabledFunctions"]
		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().selection
		if not selection:
			return

		for s in selection:
			if isinstance(s,self.parent().parent().nodeWidget):
				skelType = "node"
			elif isinstance(s,self.parent().parent().leafWidget):
				skelType = "leaf"
			else:
				raise ValueError("Unknown selection type: %s" % str(type(s)))

			conf[ "mainWindow" ].openView(
				translate( "Edit" ),  # AnzeigeName
				"icon-edit",  # Icon
				"edithandler",  # viewName
				self.parent().parent().module,  # Modulename
				"edit",  # Action
				data = { "context" : self.parent().parent().context,
						 "baseType": EditWidget.appTree,
						 "skelType": skelType,
						 "key": s.data[ "key" ]
						 },
				target = "popup" if self.parent().parent().isSelector else "mainNav"
			)



	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )


class DeleteAction(Button):
	"""
		Allows deleting an entry in a tree-module.
		The type (node or leaf) of the entry is determined dynamically.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__(translate("Delete"), icon="icon-delete")
		self["class"] = "bar-item btn btn--small btn--delete"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(DeleteAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DeleteAction,self).onDetach()

	def onSelectionChanged(self, table, selection, *args,**kwargs ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True


	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="delete"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-delete" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "delete" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().selection
		if not selection:
			return

		d = Confirm(translate("Delete {{amt}} Entries?",amt=len(selection)) ,title=translate("Delete them?"), yesCallback=self.doDelete, yesLabel=translate("Delete"), noLabel=translate("Keep") )
		d.deleteList = selection
		d.addClass( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		agroup = requestGroup( self.allDeletedSuccess )
		for x in deleteList:
			if isinstance(x,self.parent().parent().nodeWidget ):
				NetworkService.request( self.parent().parent().module, "delete/node", {"key": x.data["key"]}, secure=True, group=agroup )
			elif isinstance(x,self.parent().parent().leafWidget ):
				NetworkService.request( self.parent().parent().module, "delete/leaf", {"key": x.data["key"]}, secure=True, group=agroup )

		agroup.call()
		self.deleteProgressMessage = conf["mainWindow"].log("progress", translate("Einträge werden gelöscht... bitte warten"), modul=self.parent().parent().module,
							   action="delete")

	def allDeletedSuccess( self,success ):
		conf["mainWindow"].logWdg.removeInfo(self.deleteProgressMessage)

		if success:
			conf[ "mainWindow" ].log( "success", translate( "Einträge gelöscht" ), modul = self.parent().parent().module, action = "delete" )
		else:
			conf[ "mainWindow" ].log( "error", translate( "Ein oder mehrere Einträge konnten nicht gelöscht werden" ), modul = self.parent().parent().module, action = "delete" )

		DeferredCall(
			NetworkService.notifyChange, self.parent().parent().module,
			action = 'delete', _delay = 1500
		)

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ReloadAction(Button):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( translate("Reload"), icon="icon-reload")
		self["class"] = "bar-item btn btn--small btn--reload"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="reload" and (handler == "tree" or handler.startswith("tree."))

	def onClick(self, sender=None):
		self.addClass("is-loading")
		NetworkService.notifyChange( self.parent().parent().module )

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")

actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )


class SelectRootNode( html5.Select ):
	"""
		Allows selecting a different rootNode in Tree applications
	"""
	def __init__(self, module, handler, actionName, *args, **kwargs):
		super( SelectRootNode, self ).__init__( *args, **kwargs )
		self.addClass("select","select--small","bar-item")
		self.sinkEvent("onChange")
		self.hide()

	def onAttach(self):
		super( SelectRootNode, self ).onAttach()
		self.parent().parent().rootNodeChangedEvent.register( self )

		if self.parent().parent().rootNode is None:
			self.update()

	def onDetach(self):
		self.parent().parent().rootNodeChangedEvent.unregister( self )
		super( SelectRootNode, self ).onDetach()

	def update(self):
		self.removeAllChildren()
		NetworkService.request( self.parent().parent().module, "listRootNodes",
		                            successHandler=self.onRootNodesAvailable)

	def onRootNodeChanged(self, newNode, *args,**kwargs):
		for option in self._children:
			if option["value"] == newNode:
				option["selected"] = True
				return

	def onRootNodesAvailable(self, req):
		res = NetworkService.decode( req )
		for node in res:
			option = html5.Option()
			option["value"] = node["key"]
			option.appendChild( html5.TextNode( node[ "name"] ) )
			if node["key"] == self.parent().parent().rootNode:
				option["selected"] = True
			self.appendChild( option )

		if len(self.children()) > 1:
			self.show()
		else:
			self.hide()

	def onChange(self, event):
		newRootNode = self["options"].item(self["selectedIndex"]).value
		self.parent().parent().setRootNode( newRootNode )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="selectrootnode" and (handler == "tree" or handler.startswith("tree."))

actionDelegateSelector.insert( 1, SelectRootNode.isSuitableFor, SelectRootNode )
