import html5
from network import NetworkService, DeferredCall
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from widgets.file import Uploader, LeafFileWidget
from i18n import translate

class FileSelectUploader( html5.Input ):
	"""
		Small wrapper around <input type="file">.
		Creates the element; executes the click (=opens the file dialog);
		runs the callback if a file has been selected and removes itself from its parent.

	"""
	def __init__(self, *args, **kwargs):
		super( FileSelectUploader, self ).__init__( *args, **kwargs )
		self["type"] = "file"
		self["style"]["display"] = "none"
		self.sinkEvent("onChange")

	def onChange(self, event):
		if event.target.files.length > 0:
			Uploader( event.target.files.item(0), self.parent().node )

		self.parent().removeChild( self )

class AddLeafAction( html5.ext.Button ):
	"""
		Allows uploading of files using the file dialog.
	"""
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( translate("Add"), *args, **kwargs )
		self["class"] = "icon upload"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		if modul is None:
			return( False )
		correctAction = actionName=="add.leaf"
		correctHandler = handler == "tree.simple.file" or handler.startswith("tree.simple.file.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or modul+"-add" in conf["currentUser"]["access"])
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "add-leaf" in conf["modules"][modul]["disabledFunctions"]
		return(  correctAction and correctHandler and hasAccess and not isDisabled )


	def onClick(self, sender=None):
		uploader = FileSelectUploader()
		self.parent().parent().appendChild( uploader )
		uploader.element.click()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, AddLeafAction.isSuitableFor, AddLeafAction )


class DownloadAction( html5.ext.Button ):
	"""
		Allows downloading files from the server.
	"""
	def __init__(self, *args, **kwargs):
		super( DownloadAction, self ).__init__( translate("Download"), *args, **kwargs )
		self["class"] = "icon download"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(DownloadAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DownloadAction,self).onDetach()

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
		if modul is None:
			return( False )
		correctAction = actionName=="download"
		correctHandler = handler == "tree.simple.file" or handler.startswith("tree.simple.file.")
		isDisabled = modul is not None and "disabledFunctions" in conf["modules"][modul].keys() and conf["modules"][modul]["disabledFunctions"] and "download" in conf["modules"][modul]["disabledFunctions"]
		return( correctAction and correctHandler and not isDisabled )


	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		backOff = 50
		self.disableViUnloadingWarning()
		for s in selection:
			if not isinstance( s, LeafFileWidget):
				continue
			DeferredCall( self.doDownload, s.data, _delay=backOff )
			backOff += 50
		DeferredCall( self.enableViUnloadingWarning, _delay=backOff+1000 )

	def disableViUnloadingWarning(self, *args, **kwargs ):
		eval("window.top.preventViUnloading = false;")

	def enableViUnloadingWarning(self, *args, **kwargs ):
		eval("window.top.preventViUnloading = true;")

	def doDownload(self, fileData):
		a = html5.A()
		a["href"] = "/file/download/%s/%s?download=1" % (fileData["dlkey"],fileData["name"])
		a.element.click()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DownloadAction.isSuitableFor, DownloadAction )