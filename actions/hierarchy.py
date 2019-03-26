# -*- coding: utf-8 -*-
import html5
from config import conf
from i18n import translate
from network import NetworkService
from pane import Pane
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget


class AddAction( html5.ext.Button ):
	"""
		Adds a new node in a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__( translate("Add"), *args, **kwargs )
		self["class"] = "icon add"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		pane = Pane(translate("Add"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_hierarchy", "action_add" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appHierarchy,
		                    node=self.parent().parent().rootNode,
		                    context=self.parent().parent().context)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction( html5.ext.Button ):
	"""
		Edits a node in a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( translate("Edit"), *args, **kwargs )
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

	def onSelectionChanged(self, table, selection ):
		if selection:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	def onSelectionActivated(self, table, selection):
		if not self.parent().parent().selectMode and len(selection)>0:
			self.openEditor( selection[0].data["key"] )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="edit"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "edit" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			self.openEditor( s["key"] )

	def openEditor(self, key):
		pane = Pane(translate("Edit"), closeable=True)
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appHierarchy, key=key,
		                    context=self.parent().parent().context)
		pane.addWidget( edwg )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )

class CloneAction( html5.ext.Button ):
	"""
		Allows cloning an entry (including its subentries) in a hierarchy application.
	"""

	def __init__(self, *args, **kwargs):
		super( CloneAction, self ).__init__( translate("Clone"), *args, **kwargs )
		self["class"] = "icon clone"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(CloneAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(CloneAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if selection:
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

		correctAction = actionName=="clone"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "clone" in conf["modules"][module]["disabledFunctions"]
		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			self.openEditor( s["key"] )

	def openEditor(self, key):
		pane = Pane(translate("Clone"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_hierarchy", "action_edit" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appHierarchy,
		                  node=self.parent().parent().rootNode, key=key,
		                    context=self.parent().parent().context,
		                    clone=True)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, CloneAction.isSuitableFor, CloneAction )


class DeleteAction( html5.ext.Button ):
	"""
		Deletes a node from a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__( translate("Delete"), *args, **kwargs )
		self["class"] = "icon delete"
		self["disabled"]= True
		self.isDisabled = True

	def onAttach(self):
		super(DeleteAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DeleteAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if selection:
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
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-delete" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "delete" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog(translate("Delete {amt} Entries?",amt=len(selection)) ,title=translate("Delete them?"), yesCallback=self.doDelete, yesLabel=translate("Delete"), noLabel=translate("Keep") )
		d.deleteList = [x["key"] for x in selection]
		d["class"].append( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			NetworkService.request( self.parent().parent().module, "delete", {"key": x}, secure=True, modifies=True )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ReloadAction( html5.ext.Button ):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( translate("Reload"), *args, **kwargs )
		self["class"] = "icon reload"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="reload"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		self["class"].append("is_loading")
		NetworkService.notifyChange( self.parent().parent().module )

	def resetLoadingState(self):
		if "is_loading" in self["class"]:
			self["class"].remove("is_loading")

actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )


class SelectRootNode(html5.Select):
	"""
		Selector for hierarchy root nodes.
	"""
	def __init__(self, module, handler, actionName, *args, **kwargs):
		super( SelectRootNode, self ).__init__( *args, **kwargs )
		self.sinkEvent("onChange")
		self.hide()

	def onAttach(self):
		super(SelectRootNode, self).onAttach()
		self.parent().parent().rootNodeChangedEvent.register(self)

		if self.parent().parent().rootNode is None:
			self.update()

	def onDetach(self):
		self.parent().parent().rootNodeChangedEvent.unregister(self)
		super(SelectRootNode, self).onDetach()

	def update(self):
		self.removeAllChildren()
		NetworkService.request(self.parent().parent().module, "listRootNodes",
		                        successHandler=self.onRootNodesAvailable)

	def onRootNodeChanged(self, newNode):
		for option in self._children:
			if option["value"] == newNode:
				option["selected"] = True
				return

	def onRootNodesAvailable(self, req):
		res = NetworkService.decode(req)

		for node in res:
			option = html5.Option()
			option["value"] = node["key"]
			option.appendChild(node["name"])

			if node["key"] == self.parent().parent().rootNode:
				option["selected"] = True

			self.appendChild(option)

		if len(self.children()) > 1:
			self.show()
		else:
			self.hide()

	def onChange(self, event):
		newRootNode = self["options"].item(self["selectedIndex"]).value
		self.parent().parent().setRootNode(newRootNode)

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName == "selectrootnode" and (handler == "hierarchy" or handler.startswith("hierarchy."))

actionDelegateSelector.insert( 1, SelectRootNode.isSuitableFor, SelectRootNode )
