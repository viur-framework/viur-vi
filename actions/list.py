import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane


class AddAction( html5.ext.Button ):
	def __init__(self, parent, *args, **kwargs):
		super( AddAction, self ).__init__( "Add", *args, **kwargs )
		self["style"] = "icon add"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		return( (modul == "list" or modul.startswith("list.") and actionName=="add") )

	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True)
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appList)
		pane.addWidget( edwg )
		pane.focus()

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction( html5.ext.Button ):
	def __init__(self, parent, *args, **kwargs):
		super( EditAction, self ).__init__( "Edit", *args, **kwargs )
		#self.setEnabled(False)
		self["style"] = "icon edit"
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
		return( (modul == "list" or modul.startswith("list.") and actionName=="edit") )

	def onClick(self, sender=None):
		selection = self.parent.getCurrentSelection()
		if not selection:
			return
		for s in selection:
			pane = Pane("Edit", closeable=True)
			conf["mainWindow"].stackPane( pane )
			edwg = EditWidget( self.parent.modul, EditWidget.appList, key=s["id"])
			pane.addWidget( edwg )
			pane.focus()

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )

class YesNoDialog( html5.Div ):
	def __init__(self, topic, question, funcYes=None, funcNo=None, *args, **kwargs):
		super( YesNoDialog, self ).__init__( modal=True, *args, **kwargs )
		self.yesFunc = funcYes
		self.noFunc = funcNo
		DOM.setStyleAttribute(self.getElement(),"z-index","99")
		self.setText( topic )
		l = Label(question)
		self.panel.add(Label(question), 1, 0 )
		self.yesBtn = Button("Yes", self.onYesSelected)
		self.panel.add( self.yesBtn, 2, 0 )
		self.noBtn = Button("No",self.onNoSelected)
		self.panel.add( self.noBtn, 2, 1 )
		self.center()
		self.show()

	def onYesSelected(self, *args, **kwargs):
		self.hide()
		if self.yesFunc:
			self.yesFunc( self )
		self.yesFunc = None
		self.noFunc = None

	def onNoSelected(self, *args, **kwargs ):
		self.hide()
		if self.noFunc:
			self.noFunc( self )
		self.yesFunc = None
		self.noFunc = None


class DeleteAction( html5.ext.Button ):
	def __init__(self, parent, *args, **kwargs):
		super( DeleteAction, self ).__init__( "Delete", *args, **kwargs )
		self["style"] = "icon delete"
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
		return( (modul == "list" or modul.startswith("list.") and actionName=="delete") )

	def onClick(self, sender=None):
		selection = self.parent.getCurrentSelection()
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
			NetworkService.request( self.parent.modul, "delete", {"id": x}, secure=True, modifies=True )

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )
