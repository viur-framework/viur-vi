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
		return( (handler == "list" or handler.startswith("list.")) and actionName=="add" )

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
		#self.setEnabled(False)
		self["class"] = "icon edit"
		#self.setStyleAttribute("opacity","0.5")

	def onAttach(self):
		super(EditAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(EditAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		return
		if len(selection)>0:
			self.setEnabled(True)
		else:
			self.setEnabled(False)


	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( (handler == "list" or handler.startswith("list.")) and actionName=="edit")

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			pane = Pane("Edit", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_list", "action_edit" ])
			conf["mainWindow"].stackPane( pane )
			edwg = EditWidget( self.parent().parent().modul, EditWidget.appList, key=s["id"])
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
		#self.setEnabled(False)
		#self.setStyleAttribute("opacity","0.5")


	def onAttach(self):
		super(DeleteAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DeleteAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		return
		if len(selection)>0:
			self.setEnabled(True)
		else:
			self.setEnabled(False)


	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( (handler == "list" or handler.startswith("list.")) and actionName=="delete")

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog("Delete %s Entries?" % len(selection),title="Delete them?", yesCallback=self.doDelete)
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
		return( handler == "list" or handler.startswith("list.") and actionName=="preview" )
		#FIXME: Maybe this test..
		if modul in conf["modules"].keys():
			modulConfig = conf["modules"][modul]
			print( modulConfig )
			if "previewurls" in modulConfig.keys() and modulConfig["previewurls"]:
				return( True )
		return( False )

actionDelegateSelector.insert( 1, ListPreviewAction.isSuitableFor, ListPreviewAction )