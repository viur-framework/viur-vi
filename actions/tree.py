import html5

from vi.config import conf
from vi.i18n import translate
from vi.network import NetworkService
from vi.pane import Pane
from vi.priorityqueue import actionDelegateSelector
from vi.widgets.edit import EditWidget
from vi.widgets.button import Button


class AddLeafAction(Button):
	"""
		Creates a new leaf (ie. a file) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( translate("Add"), icon="icons-add-file", *args, **kwargs )
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
		pane = Pane("Add", iconURL="icons-add", closeable=True, iconClasses=["module_%s" % self.parent().parent().module, "apptype_tree", "action_add_leaf"])
		conf["mainWindow"].stackPane(pane)

		edwg = EditWidget( self.parent().parent().module, EditWidget.appTree, node=self.parent().parent().node, skelType="leaf" )
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddLeafAction.isSuitableFor, AddLeafAction )


class AddNodeAction(Button):
	"""
		Creates a new node (ie. a directory) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddNodeAction, self ).__init__(  translate("Add"), icons="icons-add-folder", *args, **kwargs )
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
		pane = Pane( translate("Add"), iconURL="icons-add", closeable=True, iconClasses=["module_%s" % self.parent().parent().module, "apptype_tree", "action_add_node" ])

		conf["mainWindow"].stackPane(pane)
		edwg = EditWidget(self.parent().parent().module, EditWidget.appTree, node=self.parent().parent().node, skelType="node")
		pane.addWidget(edwg)
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddNodeAction.isSuitableFor, AddNodeAction )


class EditAction(Button):
	"""
		Edits an entry inside a tree application.
		The type (node or leaf) of the entry is determined dynamically
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__(  translate("Edit"), icons="icons-edit", *args, **kwargs )
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
		if (not self.parent().parent().selectMode
			and len(selection) == 1
			and isinstance(selection[0], self.parent().parent().leafWidget)):

			pane = Pane(
				translate("Edit"),
				iconURL="icons-edit",
				closeable=True,
				iconClasses=["module_%s" % self.parent().parent().module, "apptype_tree", "action_edit"]
			)
			conf["mainWindow"].stackPane(pane)

			if isinstance( selection[0], self.parent().parent().nodeWidget):
				skelType = "node"

			elif isinstance( selection[0], self.parent().parent().leafWidget):
				skelType = "leaf"

			else:
				raise ValueError("Unknown selection type: %s" % str(type(selection[0])))

			edwg = EditWidget(
				self.parent().parent().module,
				EditWidget.appTree,
				key=selection[0].data["key"],
				skelType=skelType
			)
			pane.addWidget(edwg)
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
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="edit"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "edit" in conf["modules"][module]["disabledFunctions"]
		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		print(selection)
		for s in selection:
			pane = Pane(translate("Edit"), closeable=True)
			conf["mainWindow"].stackPane( pane, focus=True )
			if isinstance(s,self.parent().parent().nodeWidget):
				skelType = "node"
			elif isinstance(s,self.parent().parent().leafWidget):
				skelType = "leaf"
			else:
				raise ValueError("Unknown selection type: %s" % str(type(s)))
			edwg = EditWidget( self.parent().parent().module, EditWidget.appTree, key=s.data["key"], skelType=skelType, iconClasses=["module_%s" % self.parent().parent().module, "apptype_tree", "action_edit" ])
			pane.addWidget( edwg )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )


class DeleteAction(Button):
	"""
		Allows deleting an entry in a tree-module.
		The type (node or leaf) of the entry is determined dynamically.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__(translate("Delete"), icon="icons-delete", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--delete"
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
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="delete"
		correctHandler = handler == "tree" or handler.startswith("tree.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-delete" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "delete" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog(translate("Delete {amt} Entries?",amt=len(selection)) ,title=translate("Delete them?"), yesCallback=self.doDelete, yesLabel=translate("Delete"), noLabel=translate("Keep") )
		d.deleteList = selection
		d.addClass( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			if isinstance(x,self.parent().parent().nodeWidget ):
				NetworkService.request( self.parent().parent().module, "delete/node", {"key": x.data["key"]}, secure=True, modifies=True )
			elif isinstance(x,self.parent().parent().leafWidget ):
				NetworkService.request( self.parent().parent().module, "delete/leaf", {"key": x.data["key"]}, secure=True, modifies=True )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ReloadAction(Button):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( translate("Reload"), icon="icons-reload", *args, **kwargs )
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
		                            successHandler=self.onRootNodesAvailable,
		                                cacheable=True )

	def onRootNodeChanged(self, newNode):
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


class ReturnSelectionAction(Button):
	"""
		This is the new "activateSelectionAction" for Trees - we need a different event
		to avoid conflicts with "open that folder" action.
	"""
	def __init__(self, *args, **kwargs ):
		super( ReturnSelectionAction, self ).__init__( translate("Select"), icons="icons-select-add", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--activateselection"

	def onClick(self, sender=None):
		self.parent().parent().returnCurrentSelection()

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctHandler = handler == "tree" or handler.startswith("tree.")
		return( actionName=="select" and  correctHandler)

actionDelegateSelector.insert( 3, ReturnSelectionAction.isSuitableFor, ReturnSelectionAction )
