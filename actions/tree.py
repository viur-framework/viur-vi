import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane


class AddLeafAction( html5.ext.Button ):
	"""
		Creates a new leaf (ie. a file) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add leaf"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		return( (modul == "tree" or modul.startswith("tree.")) and actionName=="add.leaf" )

	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True)
		conf["mainWindow"].stackPane( pane, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_add_leaf" ] )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="leaf" )
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddLeafAction.isSuitableFor, AddLeafAction )


class AddNodeAction( html5.ext.Button ):
	"""
		Creates a new node (ie. a directory) for a tree application
	"""
	def __init__(self, *args, **kwargs):
		super( AddNodeAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon add node"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		return( (modul == "tree" or modul.startswith("tree.")) and actionName=="add.node" )

	def onClick(self, sender=None):
		pane = Pane("Add", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_add_node" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="node" )
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddNodeAction.isSuitableFor, AddNodeAction )


class EditAction( html5.ext.Button ):
	"""
		Edits an entry inside a tree application.
		The type (node or leaf) of the entry is determined dynamically
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
			edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, key=s.data["id"], skelType=skelType, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_edit" ])
			pane.addWidget( edwg )
			pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )


class DeleteAction( html5.ext.Button ):
	"""
		Allows deleting an entry in a tree-modul.
		The type (node or leaf) of the entry is determined dynamically.
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
	def isSuitableFor( modul, actionName ):
		return( (modul == "tree" or modul.startswith("tree.")) and actionName=="delete")

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog("Delete %s Entries?" % len(selection),title="Delete them?", yesCallback=self.doDelete)
		d.deleteList = selection

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			if isinstance(x,self.parent().parent().nodeWidget ):
				NetworkService.request( self.parent().parent().modul, "delete/node", {"id": x.data["id"]}, secure=True, modifies=True )
			elif isinstance(x,self.parent().parent().leafWidget ):
				NetworkService.request( self.parent().parent().modul, "delete/leaf", {"id": x.data["id"]}, secure=True, modifies=True )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )