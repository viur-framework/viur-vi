import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane


class AddAction( html5.ext.Button ):
	"""
		Adds a new node in a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="add"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-add" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "add" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )


	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_hierarchy", "action_add" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appHierarchy, node=self.parent().parent().rootNode )
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
		if not self.parent().parent().isSelector and len(selection)>0:
			self.openEditor( selection[0].data["id"] )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="edit"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-edit" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "edit" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )


	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			self.openEditor( s["id"] )

	def openEditor( self, id ):
		pane = Pane("Edit", closeable=True)
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appHierarchy, key=id)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )


class DeleteAction( html5.ext.Button ):
	"""
		Deletes a node from a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__( "Delete", *args, **kwargs )
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
		correctAction = actionName=="delete"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-delete" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "delete" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )


	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog("Delete %s Entries?" % len(selection), title="Delete them?", yesCallback=self.doDelete, yesLabel="Delete", noLabel="Keep")
		d.deleteList = [x["id"] for x in selection]
		d["class"].append( "delete" )
		return
		for s in selection:
			pane = Pane("Edit", closeable=True)
			conf["mainWindow"].stackPane( pane )
			edwg = EditWidget( self.parent.modul, EditWidget.appList, key=s["id"])
			pane.addWidget( edwg )
			pane.focus()

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			NetworkService.request( self.parent().parent().modul, "delete", {"id": x}, secure=True, modifies=True )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ReloadAction( html5.ext.Button ):
	"""
		Allows adding an entry in a list-modul.
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( "Reload", *args, **kwargs )
		self["class"] = "icon reload hierarchy"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="reload"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		return(  correctAction and correctHandler )

	def onClick(self, sender=None):
		NetworkService.notifyChange( self.parent().parent().modul )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )