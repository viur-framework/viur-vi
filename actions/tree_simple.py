import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from html5.ext.inputdialog import InputDialog

class AddNodeAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( AddNodeAction, self ).__init__( "Add Node", *args, **kwargs )
		self["class"] = "icon mkdir"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		print(modul, actionName)
		return( (modul == "tree.simple" or modul.startswith("tree.simple."))  and actionName=="add.node" )

	def onClick(self, sender=None):
		i = InputDialog( "Directory Name", successHandler=self.createDir )
		#self.appendChild( i )
		#pane = Pane("Add", closeable=True)
		#conf["mainWindow"].stackPane( pane )
		#edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="leaf" )
		#pane.addWidget( edwg )
		#pane.focus()


	def createDir(self, dialog, dirName ):
		if len(dirName)==0:
			return
		NetworkService.request(self.parent().parent().modul,"add/node",{"node": self.parent().parent().node,"name":dirName}, secure=True, modifies=True)
actionDelegateSelector.insert( 3, AddNodeAction.isSuitableFor, AddNodeAction )


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
		return( (modul == "tree.simple" or modul.startswith("tree.simple.")) and actionName=="edit")

	def onClick(self, sender=None):
		print("EDIT ACTION CLICKED")
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			if isinstance(s,self.parent().parent().nodeWidget):
				i = InputDialog( "Directory Name", successHandler=self.editDir, value=s.data["name"] )
				i.dirKey = s.data["id"]
				return
			pane = Pane("Edit", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_edit" ])
			conf["mainWindow"].stackPane( pane )
			skelType = "leaf"
			edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, key=s.data["id"], skelType=skelType)
			pane.addWidget( edwg )
			pane.focus()

	def editDir(self, dialog, dirName ):
		NetworkService.request( self.parent().parent().modul, "edit/node", {"id": dialog.dirKey,"name": dirName}, secure=True, modifies=True)

actionDelegateSelector.insert( 3, EditAction.isSuitableFor, EditAction )