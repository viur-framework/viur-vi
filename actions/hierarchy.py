import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane


class AddAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		return( (modul == "hierarchy" or modul.startswith("hierarchy.")) and actionName=="add")

	def onClick(self, sender=None):
		print("ADD ACTION HIERARCHY", self.parent().parent().rootNode)
		pane = Pane("Add", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_hierarchy", "action_add" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appHierarchy, node=self.parent().parent().rootNode )
		pane.addWidget( edwg )
		pane.focus()

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction( html5.ext.Button ):
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
	def isSuitableFor( modul, actionName ):
		return( (modul == "hierarchy" or modul.startswith("hierarchy.")) and actionName=="edit")

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			pane = Pane("Edit", closeable=True)
			conf["mainWindow"].stackPane( pane )
			edwg = EditWidget( self.parent().parent().modul, EditWidget.appHierarchy, key=s["id"])
			pane.addWidget( edwg )
			pane.focus()

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )

class YesNoDialog( html5.Div ):
	def __init__(self, topic, question, funcYes=None, funcNo=None, *args, **kwargs):
		super( YesNoDialog, self ).__init__( *args, **kwargs )
		self.yesFunc = funcYes
		self.noFunc = funcNo
		self["style"]["z-index"] = 10
		self["style"]["display"] = "block"
		self["style"]["width"] = "400px"
		self["style"]["height"] = "400px"
		self["style"]["position"] = "absolute"
		self["style"]["background-color"] = "green"
		#DOM.setStyleAttribute(self.getElement(),"z-index","99")

		#self.setText( topic )
		l = html5.Label(question)
		self.appendChild( html5.Label(question) )
		self.yesBtn = html5.ext.Button("Yes", self.onYesSelected)
		self.appendChild( self.yesBtn )
		self.noBtn = html5.ext.Button("No",self.onNoSelected)
		self.appendChild( self.noBtn )
		html5.Body().appendChild( self )

	def onYesSelected(self, *args, **kwargs):
		if self.yesFunc:
			self.yesFunc( self )
		self.yesFunc = None
		self.noFunc = None
		html5.Body().removeChild( self )

	def onNoSelected(self, *args, **kwargs ):
		if self.noFunc:
			self.noFunc( self )
		self.yesFunc = None
		self.noFunc = None
		html5.Body().removeChild( self )


class DeleteAction( html5.ext.Button ):
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
	def isSuitableFor( modul, actionName ):
		return( (modul == "hierarchy" or modul.startswith("hierarchy.")) and actionName=="delete")

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		print( "Deleting "+str([x["id"] for x in selection]))
		d = YesNoDialog("Delete %s Entries?" % len(selection),"Delete them?", funcYes=self.doDelete)
		d.deleteList = [x["id"] for x in selection]
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

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )
