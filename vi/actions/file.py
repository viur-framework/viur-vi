# -*- coding: utf-8 -*-
from flare import html5
from flare.popup import Prompt
from flare.network import NetworkService
from vi.widgets.edit import EditWidget
from vi.config import conf
from flare.i18n import translate
from flare.network import DeferredCall
from vi.priorityqueue import actionDelegateSelector
from vi.widgets.file import Uploader,MultiUploader
from flare.button import Button


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
			try:
				node = self.parent().node
			except:
				node = None

			filelist = []
			files = event.target.files
			for x in range(0, len(files)):
				filelist.append(files.item(x))

			if len(filelist) == 1:
				ul = Uploader(files.item(0), node, self.parent().module)
			else:
				ul = MultiUploader(filelist, node,self.parent().module)

			if "filebone" in dir(self):
				ul.uploadSuccess.register( self.filebone )

		self.parent().removeChild( self )

class AddNodeAction(Button):
	"""
		Adds a new directory to a tree.simple application.
	"""
	def __init__(self, *args, **kwargs):
		super(AddNodeAction, self).__init__(
			translate("Add folder"),
			icon="icon-add-folder"
		)
		self.addClass("bar-item btn btn--small btn--mkdir")

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add.node"
		correctHandler = handler == "tree.simple.file" or handler == "tree.file" or handler.startswith("tree.file.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add-node" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		i = Prompt(
			translate("Directory Name"),
			successHandler=self.createDir,
			title=translate("Create directory"),
			successLbl=translate("Create")
		)

		i.addClass( "create directory" )

	def createDir(self, dialog, dirName ):
		if len(dirName)==0:
			return
		r = NetworkService.request(self.parent().parent().module,"add/node",{"node": self.parent().parent().node,"name":dirName}, secure=True, modifies=True, successHandler=self.onMkDir)
		r.dirName = dirName

	def onMkDir(self, req):
		dirName = req.dirName
		conf["mainWindow"].log("success",translate("Directory \"{{name}}\" created.", icon="icon-add-folder",name=dirName))

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, AddNodeAction.isSuitableFor, AddNodeAction )

class AddLeafAction(Button):
	"""
		Allows uploading of files using the file dialog.
	"""
	def __init__(self, *args, **kwargs):
		super(AddLeafAction, self).__init__(
			translate("Upload"),
			icon="icon-upload-file"
		)
		self.addClass("bar-item btn btn--small btn--upload btn--primary")

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add.leaf"
		correctHandler = handler == "tree.simple.file" or handler == "tree.file" or handler.startswith("tree.file.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add-leaf" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled


	def onClick(self, sender=None):
		uploader = FileSelectUploader()
		if "filebone" in dir(self):
			uploader.filebone = self.filebone
		self.parent().parent().appendChild(uploader)
		uploader.element.click()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, AddLeafAction.isSuitableFor, AddLeafAction )

class EditAction(Button):
	"""
		Provides editing in a tree.simple application.
		If a directory is selected, it opens a dialog for renaming that directory,
		otherwise the full editWidget is used.
	"""
	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( translate("Edit"), icon="icon-edit")
		self["class"] = "bar-item btn btn--small btn--edit"
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

	def onSelectionActivated(self, table, selection ):
		if not self.parent().parent().selectionCallback and len(selection)==1 and isinstance(selection[0], self.parent().parent().leafWidget):
			conf[ "mainWindow" ].openView(
				translate( "Edit" ),  # AnzeigeName
				"icon-edit",  # Icon
				"edithandler",  # viewName
				self.parent().parent().module,  # Modulename
				"edit",  # Action
				data = { "context" : self.parent().parent().context,
						 "baseType": EditWidget.appTree,
						 "skelType": "leaf",
						 "key"     : selection[0].data["key"]
						 },
				target = "popup" if self.parent().parent().isSelector else "mainNav"
			)


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

		correctAction = actionName=="edit"
		correctHandler = handler == "tree.simple.file" or handler == "tree.file" or handler.startswith("tree.file.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "edit" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().selection
		if not selection:
			return

		for s in selection:
			if isinstance(s,self.parent().parent().nodeWidget):
				i = Prompt(
					translate("Directory Name"),
					successHandler=self.editDir,
					value=s.data["name"]
				)
				i.dirKey = s.data["key"]
				return

			conf[ "mainWindow" ].openView(
				translate( "Edit" ),  # AnzeigeName
				"icon-edit",  # Icon
				"edithandler",  # viewName
				self.parent().parent().module,  # Modulename
				"edit",  # Action
				data = { "context" : self.parent().parent().context,
						 "baseType": EditWidget.appTree,
						 "skelType": "leaf",
						 "key"     : s.data["key"]
						 },
				target = "popup" if self.parent().parent().isSelector else "mainNav"
			)



	def editDir(self, dialog, dirName ):
		NetworkService.request( self.parent().parent().module, "edit/node", {"key": dialog.dirKey,"name": dirName}, secure=True, modifies=True)

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, EditAction.isSuitableFor, EditAction )




class DownloadAction(Button):
	"""
		Allows downloading files from the server.
	"""
	def __init__(self, *args, **kwargs):
		super( DownloadAction, self ).__init__( translate("Download"), icon="icon-download-file")
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
		correctHandler = handler == "tree.simple.file" or handler == "tree.file" or handler.startswith("tree.file.")
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "download" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and not isDisabled


	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		backOff = 50
		self.disableViUnloadingWarning()
		for s in selection:
			if not isinstance( s, self.parent().parent().leafWidget):
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
