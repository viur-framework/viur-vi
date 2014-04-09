import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane


class AddLeafAction( html5.ext.Button ):
	"""
		Creates a new leaf (ie. a file) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add leaf"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		if modul is None:
			return( False )
		correctAction = actionName=="add.leaf"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-add" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "add-leaf" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True)
		conf["mainWindow"].stackPane( pane, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_add_leaf" ] )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="leaf" )
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddLeafAction.isSuitableFor, AddLeafAction )


class AddNodeAction( html5.ext.Button ):
	"""
		Creates a new node (ie. a directory) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddNodeAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add node"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		if modul is None:
			return( False )
		correctAction = actionName=="add.node"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-add" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "add-node" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_add_node" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="node" )
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddNodeAction.isSuitableFor, AddNodeAction )


class EditAction( html5.ext.Button ):
	"""
		Edits an entry inside a tree application.
		The type (node or leaf) of the entry is determined dynamically
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( "Edit", *args, **kwargs )
		self["class"] = "icon edit"
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
		if not self.parent().parent().isSelector and len(selection)==1:
			pane = Pane("Edit", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_edit" ])
			conf["mainWindow"].stackPane( pane )
			if isinstance( selection[0], self.parent().parent().nodeWidget):
				skelType = "node"
			elif isinstance( selection[0], self.parent().parent().leafWidget):
				skelType = "leaf"
			else:
				raise ValueError("Unknown selection type: %s" % str(type(selection[0])))
			edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, key=selection[0].data["id"], skelType=skelType)
			pane.addWidget( edwg )
			pane.focus()

	def onSelectionChanged(self, table, selection ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		if modul is None:
			return( False )
		correctAction = actionName=="edit"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-edit" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "edit" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

	def onClick(self, sender=None):
		print("EDIT ACTION CLICKED")
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		print(selection)
		for s in selection:
			pane = Pane("Edit", closeable=True)
			conf["mainWindow"].stackPane( pane )
			if isinstance(s,self.parent().parent().nodeWidget):
				skelType = "node"
			elif isinstance(s,self.parent().parent().leafWidget):
				skelType = "leaf"
			else:
				raise ValueError("Unknown selection type: %s" % str(type(s)))
			edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, key=s.data["id"], skelType=skelType, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_edit" ])
			pane.addWidget( edwg )
			pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )


class DeleteAction( html5.ext.Button ):
	"""
		Allows deleting an entry in a tree-modul.
		The type (node or leaf) of the entry is determined dynamically.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__( "Delete", *args, **kwargs )
		self["class"] = "icon delete"
		self["disabled"]= True
		self.isDisabled=True


	def onAttach(self):
		super(DeleteAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DeleteAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True


	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		if modul is None:
			return( False )
		correctAction = actionName=="delete"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-delete" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "delete" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog("Delete %s Entries?" % len(selection),title="Delete them?", yesCallback=self.doDelete, yesLabel="Delete", noLabel="Keep")
		d.deleteList = selection
		d["class"].append( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			if isinstance(x,self.parent().parent().nodeWidget ):
				NetworkService.request( self.parent().parent().modul, "delete/node", {"id": x.data["id"]}, secure=True, modifies=True )
			elif isinstance(x,self.parent().parent().leafWidget ):
				NetworkService.request( self.parent().parent().modul, "delete/leaf", {"id": x.data["id"]}, secure=True, modifies=True )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ReloadAction( html5.ext.Button ):
	"""
		Allows adding an entry in a list-modul.
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( "Reload", *args, **kwargs )
		self["class"] = "icon reload"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="reload"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		return(  correctAction and correctHandler )

	def onClick(self, sender=None):
		self["class"].append("is_loading")
		NetworkService.notifyChange( self.parent().parent().modul )

	def resetLoadingState(self):
		if "is_loading" in self["class"]:
			self["class"].remove("is_loading")

actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )


class SelectRootNode( html5.Select ):
	"""
		Allows selecting a different rootNode in Tree applications
	"""
	def __init__(self, *args, **kwargs):
		super( SelectRootNode, self ).__init__( *args, **kwargs )
		self.sinkEvent("onChange")

	def onAttach(self):
		super( SelectRootNode, self ).onAttach()
		NetworkService.request( self.parent().parent().modul, "listRootNodes", successHandler=self.onRootNodesAvaiable, cacheable=True )
		self.parent().parent().rootNodeChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().rootNodeChangedEvent.unregister( self )
		super( SelectRootNode, self ).onDetach()

	def onRootNodeChanged(self, newNode):
		for option in self._children:
			if option["value"] == newNode:
				option["selected"] = True
				return

	def onRootNodesAvaiable(self, req):
		res = NetworkService.decode( req )
		for node in res:
			option = html5.Option()
			option["value"] = node["key"]
			option.appendChild( html5.TextNode(node["name"][:32]))
			if node["key"] == self.parent().parent().rootNode:
				option["selected"] = True
			self.appendChild( option )

	def onChange(self, event):
		newRootNode = self["options"].item(self["selectedIndex"]).value
		self.parent().parent().setRootNode( newRootNode )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="selectrootnode"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		return(  correctAction and correctHandler )

actionDelegateSelector.insert( 1, SelectRootNode.isSuitableFor, SelectRootNode )