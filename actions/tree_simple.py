import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from html5.ext.inputdialog import InputDialog

class AddNodeAction( html5.ext.Button ):
	"""
		Adds a new directory to a tree.simple application.
	"""
	def __init__(self, *args, **kwargs):
		super( AddNodeAction, self ).__init__( "Add Node", *args, **kwargs )
		self["class"] = "icon mkdir"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		correctAction = actionName=="add.node"
		correctHandler = handler == "tree.simple" or handler.startswith("tree.simple.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-add" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "add-node" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )


	def onClick(self, sender=None):
		i = InputDialog( "Directory Name", successHandler=self.createDir, title="Create directory",successLbl="Create" )
		i["class"].append( "create" )
		i["class"].append( "directory" )

	def createDir(self, dialog, dirName ):
		if len(dirName)==0:
			return
		r = NetworkService.request(self.parent().parent().modul,"add/node",{"node": self.parent().parent().node,"name":dirName}, secure=True, modifies=True, successHandler=self.onMkDir)
		r.dirName = dirName

	def onMkDir(self, req):
		dirName = req.dirName
		conf["mainWindow"].log("success","Directory \"%s\" created." % dirName)

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, AddNodeAction.isSuitableFor, AddNodeAction )


class EditAction( html5.ext.Button ):
	"""
		Provides editing in a tree.simple application.
		If a directory is selected, it opens a dialog for renaming that directory,
		otherwise the full editWidget is used.
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( "Edit", *args, **kwargs )
		self["class"] = "icon edit"

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
		correctAction = actionName=="edit"
		correctHandler = handler == "tree.simple" or handler.startswith("tree.simple.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-edit" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "edit" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )

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

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, EditAction.isSuitableFor, EditAction )