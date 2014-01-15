import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from widgets.preview import Preview

class EditPane( Pane ):
	pass

"""
	Provides the actions suitable for list applications
"""
class AddAction( html5.ext.Button ):
	"""
		Allows adding an entry in a list-modul.
	"""
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add list"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="add"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-add" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "add" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

	def onClick(self, sender=None):
		pane = EditPane("Add", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_list", "action_add" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appList)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction( html5.ext.Button ):
	"""
		Allows editing an entry in a list-modul.
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
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	def onSelectionActivated(self, table, selection ):
		if not self.parent().parent().isSelector and len(selection)==1:
			self.openEditor( selection[0]["id"] )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="edit"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-edit" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "edit" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			self.openEditor( s["id"] )

	def openEditor(self, id ):
		pane = Pane("Edit", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_list", "action_edit" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appList, key=id)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )



class DeleteAction( html5.ext.Button ):
	"""
		Allows deleting an entry in a list-modul.
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
		correctAction = actionName=="delete"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-delete" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "delete" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )


	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog("Delete %s Entries?" % len(selection),title="Delete them?", yesCallback=self.doDelete, yesLabel="Delete", noLabel="Keep" )
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

class ListPreviewAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( ListPreviewAction, self ).__init__( "Preview", *args, **kwargs )
		self["class"] = "icon preview"
		self.urls = None

	def onAttach(self):
		super(ListPreviewAction,self).onAttach()
		modul = self.parent().parent().modul
		if modul in conf["modules"].keys():
			modulConfig = conf["modules"][modul]
			if "previewurls" in modulConfig.keys() and modulConfig["previewurls"]:
				self.urls = modulConfig["previewurls"]
				pass
			else:
				self["disabled"] = True


	def onClick(self, sender=None):
		if self.urls is None:
			return
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		if len( selection )>0:
			widget = Preview( self.urls, selection[0], self.parent().parent().modul )
			conf["mainWindow"].stackWidget( widget )
	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="preview"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-view" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "view" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

actionDelegateSelector.insert( 1, ListPreviewAction.isSuitableFor, ListPreviewAction )


class CloseAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( CloseAction, self ).__init__( "Close", *args, **kwargs )
		self["class"] = "icon close"

	def onClick(self, sender=None):
		conf["mainWindow"].removeWidget( self.parent().parent() )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="close" )

actionDelegateSelector.insert( 1, CloseAction.isSuitableFor, CloseAction )

class ActivateSelectionAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( ActivateSelectionAction, self ).__init__( "Select", *args, **kwargs )
		self["class"] = "icon select"

	def onClick(self, sender=None):
		self.parent().parent().activateCurrentSelection()

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="select" )

actionDelegateSelector.insert( 1, ActivateSelectionAction.isSuitableFor, ActivateSelectionAction )


class SelectFieldsPopup( html5.ext.Popup ):
	def __init__(self, listWdg, *args, **kwargs):
		super( SelectFieldsPopup, self ).__init__( title="Select fields", *args, **kwargs )
		self["class"].append("selectfields")
		self.listWdg = listWdg
		for key, bone in self.listWdg._structure:
			chkBox = html5.Input()
			chkBox["type"] = "checkbox"
			chkBox["value"] = key
			self.appendChild(chkBox)
			if key in self.listWdg.getFields():
				chkBox["checked"] = True
			lbl = html5.Label(bone["descr"],forElem=chkBox)
			self.appendChild(lbl)
		applyBtn = html5.ext.Button("Apply", callback=self.doApply)
		self.appendChild(applyBtn)


	def doApply(self, *args, **kwargs):
		res = []
		for c in self._children:
			if isinstance(c,html5.Input) and c["checked"]:
				res.append( c["value"] )
		print("___NEW FIELDS", res)
		self.listWdg.setFields( res )
		self.close()

class SelelectFieldsAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( SelelectFieldsAction, self ).__init__( "Select fields", *args, **kwargs )
		self["class"] = "icon selectfields"

	def onClick(self, sender=None):
		SelectFieldsPopup( self.parent().parent() )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="selectfields" )

actionDelegateSelector.insert( 1, SelelectFieldsAction.isSuitableFor, SelelectFieldsAction )

