# -*- coding: utf-8 -*-
from vi import html5

from vi.config import conf
from vi.i18n import translate
from vi.network import DeferredCall
from vi.priorityqueue import actionDelegateSelector
from vi.widgets.file import Uploader, LeafFileWidget
from vi.framework.components.button import Button


class FileSelectUploader(html5.Input):
	"""
		Small wrapper around <input type="file">.
		Creates the element; executes the click (=opens the file dialog);
		runs the callback if a file has been selected and removes itself from its parent.

	"""
	def __init__(self, *args, **kwargs):
		super( FileSelectUploader, self ).__init__( *args, **kwargs )
		self["type"] = "file"
		self["multiple"] = True
		self["style"]["display"] = "none"
		self.sinkEvent("onChange")

	def onChange(self, event):
		if event.target.files.length > 0:
			for i in range(event.target.files.length):
				Uploader(event.target.files.item(i), self.parent().node)

		self.parent().removeChild( self )

class AddLeafAction(Button):
	"""
		Allows uploading of files using the file dialog.
	"""
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( translate("Add"), icon="icons-upload-file", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--upload"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add.leaf"
		correctHandler = handler == "tree.simple.file" or handler.startswith("tree.simple.file.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add-leaf" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		uploader = FileSelectUploader()
		self.parent().parent().appendChild(uploader)
		uploader.element.click()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, AddLeafAction.isSuitableFor, AddLeafAction )


class DownloadAction(Button):
	"""
		Allows downloading files from the server.
	"""
	def __init__(self, *args, **kwargs):
		super( DownloadAction, self ).__init__( translate("Download"), icon="icons-download-file", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--download"
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
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="download"
		correctHandler = handler == "tree.simple.file" or handler.startswith("tree.simple.file.")
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "download" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and not isDisabled


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
