import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane


class AddLeafAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add leaf"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		return( (modul == "tree" or modul.startswith("tree.")) and actionName=="add.leaf" )

	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True)
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="leaf" )
		pane.addWidget( edwg )
		pane.focus()

actionDelegateSelector.insert( 1, AddLeafAction.isSuitableFor, AddLeafAction )


class AddNodeAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( AddNodeAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add node"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		return( (modul == "tree" or modul.startswith("tree.")) and actionName=="add.node" )

	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True)
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="node" )
		pane.addWidget( edwg )
		pane.focus()

actionDelegateSelector.insert( 1, AddNodeAction.isSuitableFor, AddNodeAction )


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
		return( (modul == "tree" or modul.startswith("tree.")) and actionName=="edit")

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
			edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, key=s.data["id"], skelType=skelType)
			pane.addWidget( edwg )
			pane.focus()

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )