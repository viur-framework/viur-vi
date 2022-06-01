# -*- coding: utf-8 -*-
from flare import html5

from vi.config import conf
from flare.i18n import translate
from flare.network import NetworkService,requestGroup,DeferredCall
from vi.priorityqueue import actionDelegateSelector
from vi.widgets.edit import EditWidget
from flare.button import Button
from flare.popup import Confirm


class AddAction(Button):
	"""
		Adds a new node in a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__( translate("Add"), icon="icon-add")
		self["class"] = "bar-item btn btn--small btn--primary"

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
		node = self.parent().parent().currentKey
		if not node:
			node = self.parent().parent().rootNode

		conf[ "mainWindow" ].openView(
			translate( "Add" ),  # AnzeigeName
			"icon-add",  # Icon
			"edithandler",  # viewName
			self.parent().parent().module,  # Modulename
			"add",  # Action
			data = { "context" : self.parent().parent().context,
					 "baseType": EditWidget.appHierarchy,
					 "node"    : node,
					 "skelType": "node"
					 },
			target = "popup" if self.parent().parent().isSelector else "mainNav"
		)

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction(Button):
	"""
		Edits a node in a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( translate("Edit"), icon="icon-edit")
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

	def onSelectionChanged(self, table, selection, *args, **kwargs ):
		if len( selection ) > 0:
			if self.isDisabled:
				self.isDisabled = False
			self[ "disabled" ] = False
		else:
			if not self.isDisabled:
				self[ "disabled" ] = True
				self.isDisabled = True

	def onSelectionActivated(self, table, selection):
		if len(selection)>0:
			self.openEditor(selection[0].data["key"])

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
		selection = self.parent().parent().selection
		if not selection:
			return

		for s in selection:
			self.openEditor( s.data["key"] )

	def openEditor(self, key):
		conf[ "mainWindow" ].openView(
			translate( "Edit" ),  # AnzeigeName
			"icon-edit",  # Icon
			"edithandler",  # viewName
			self.parent().parent().module,  # Modulename
			"edit",  # Action
			data = { "context" : self.parent().parent().context,
					 "baseType": EditWidget.appHierarchy,
					 "skelType": "node",
					 "key"	   :key
					 },
			target = "popup" if self.parent().parent().isSelector else "mainNav"
		)



	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )

class CloneAction(Button):
	"""
		Allows cloning an entry (including its subentries) in a hierarchy application.
	"""

	def __init__(self, *args, **kwargs):
		super( CloneAction, self ).__init__( translate("Clone"), icon="icon-clone")
		self["class"] = "bar-item btn btn--small btn--clone"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(CloneAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(CloneAction,self).onDetach()

	def onSelectionChanged(self, table, selection, *args, **kwargs ):
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
		selection = self.parent().parent().selection
		if not selection:
			return

		for s in selection:
			self.openEditor( s.data[ "key" ] )

	def openEditor(self, key):
		conf[ "mainWindow" ].openView(
			translate( "Clone" ),  # AnzeigeName
			"icon-clone",  # Icon
			"edithandler",  # viewName
			self.parent().parent().module,  # Modulename
			"add",  # Action
			data = { "context" : self.parent().parent().context,
					 "baseType": EditWidget.appHierarchy,
					 "node"    : self.parent().parent().rootNode,
					 "skelType": "node",
					 "key"     :key,
					 "clone"   : True
					 },
			target = "popup" if self.parent().parent().isSelector else "mainNav"
		)


	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, CloneAction.isSuitableFor, CloneAction )


class DeleteAction(Button):
	"""
		Deletes a node from a hierarchy application.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__( translate("Delete"), icon="icon-delete")
		self["class"] = "bar-item btn btn--small btn--delete"
		self["disabled"]= True
		self.isDisabled = True

	def onAttach(self):
		super(DeleteAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DeleteAction,self).onDetach()

	def onSelectionChanged(self, table, selection, *args, **kwargs ):
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
		selection = self.parent().parent().selection
		if not selection:
			return
		d = Confirm(translate("Delete {{amt}} Entries?",amt=len(selection)) ,title=translate("Delete them?"), yesCallback=self.doDelete, yesLabel=translate("Delete"), noLabel=translate("Keep") )
		d.deleteList = [x.data[ "key" ] for x in selection]
		d.addClass( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		agroup = requestGroup( self.allDeletedSuccess )
		for x in deleteList:
			NetworkService.request( self.parent().parent().module, "delete", {"key": x, "skelType":"node"}, secure=True,group=agroup)

		agroup.call()

	def allDeletedSuccess( self,success ):
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
		correctAction = actionName=="reload"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		self.addClass("is-loading")
		NetworkService.notifyChange( self.parent().parent().module )

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")

actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )


class ListViewAction(Button):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( ListViewAction, self ).__init__( translate("ListViewAction"), icon="icon-list")
		self["class"] = "bar-item btn btn--small btn--list"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="listview"
		correctHandler = handler == "hierarchy" or handler.startswith("hierarchy.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		#self.addClass("is-loading")
		self.parent().parent().toggleListView()

	def resetLoadingState(self):
		pass
		#if self.hasClass("is-loading"):
		#	self.removeClass("is-loading")

actionDelegateSelector.insert( 1, ListViewAction.isSuitableFor, ListViewAction )
