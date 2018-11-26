# -*- coding: utf-8 -*-
import html5, utils
from priorityqueue import editBoneSelector, viewDelegateSelector, extractorDelegateSelector
from widgets.file import FileWidget, LeafFileWidget
from config import conf
from bones.relational import RelationalMultiSelectionBone, RelationalSingleSelectionBone, RelationalMultiSelectionBoneEntry
from widgets.file import Uploader, FilePreviewImage
from i18n import translate
from network import NetworkService
from widgets.edit import EditWidget
from pane import Pane
from bones.base import BaseBoneExtractor


class FileBoneExtractor(BaseBoneExtractor):
	def __init__(self, module, boneName, structure):
		super(FileBoneExtractor, self).__init__(module, boneName, structure)
		self.format = "$(dest.name)"
		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]

	def renderFileentry(self, fileentry):
		return ("%s %s/file/download/%s?download=1&fileName=%s" %
		            (fileentry["dest"]["name"], html5.window.location.origin,
		                str(fileentry["dest"]["dlkey"]), str(fileentry["dest"]["name"])))

	def render(self, data, field ):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field,self.boneName)
		val = data.get(field, "")

		if isinstance(val, list):
			return [self.renderFileentry(f) for f in val]
		elif isinstance(val, dict):
			return self.renderFileentry(val)

		return val

class FileViewBoneDelegate(object):

	def __init__(self, modul, boneName, structure):
		super(FileViewBoneDelegate, self).__init__()
		self.format = "$(name)"

		if "format" in structure[boneName].keys():
			self.format = structure[boneName]["format"]

		self.module = modul
		self.structure = structure
		self.boneName = boneName

	def renderFileentry(self, fileEntry):
		if not "dest" in fileEntry.keys():
			return None

		fileEntry = fileEntry["dest"]

		if not "name" in fileEntry.keys() and not "dlkey" in fileEntry.keys():
			return None

		adiv = html5.Div()
		if "mimetype" in fileEntry.keys():
			try:
				ftype, fformat = fileEntry["mimetype"].split("/")
				adiv["class"].append("type_%s" % ftype )
				adiv["class"].append("format_%s" % fformat )
			except:
				pass

		adiv.appendChild(FilePreviewImage(fileEntry))

		aspan=html5.Span()
		aspan.appendChild(html5.TextNode(str(fileEntry.get("name", ""))))#fixme: formatstring!
		adiv.appendChild(aspan)

		adiv["class"].append("fileBoneViewCell")
		#adiv["draggable"]=True
		#metamime="application/octet-stream"

		#if "mimetype" in fileEntry.keys():
		#   metamime=str(fileEntry["mimetype"])

		#adiv["download"]="%s:%s:/file/download/%s?download=1&fileName=%s" % (metamime, str(fileEntry["name"]),
		#                                                            str(fileEntry["dlkey"]), str(fileEntry["name"]))
		#adiv["href"]="/file/download/%s?download=1&fileName=%s" % (str(fileEntry["dlkey"]), str(fileEntry["name"]))
		return adiv

	def render(self, data, field ):
		assert field == self.boneName, "render() was called with field %s, expected %s" % (field,self.boneName)
		val = data.get(field, "")

		if isinstance(val, list):
			#MultiFileBone
			cell = html5.Div()

			for f in val:
				cell.appendChild(self.renderFileentry(f))

			return cell

		elif isinstance(val, dict):
			return self.renderFileentry(val)

		if val:
			return self.renderFileentry(val)

		return html5.Div()

class FileMultiSelectionBoneEntry(RelationalMultiSelectionBoneEntry):

	def __init__(self, *args, **kwargs):
		super(FileMultiSelectionBoneEntry, self).__init__(*args, **kwargs)
		self.addClass("fileentry")

		self.previewImg = FilePreviewImage()
		self.prependChild(self.previewImg)

		if self.data["dest"]:
			if "key" in self.data["dest"] and len(self.data["dest"]) == 1:
				self.fetchEntry(self.data["dest"]["key"])
			else:
				self.previewImg.setFile(self.data["dest"])

	def fetchEntry(self, key):
		NetworkService.request(self.module, "view/leaf/" + key,
		                        successHandler=self.onSelectionDataAvailable,
		                        cacheable=True)

	def onSelectionDataAvailable(self, req):
		data = NetworkService.decode(req)
		assert self.data["dest"]["key"] == data["values"]["key"]
		self.data["dest"] = data["values"]

		self.updateLabel()
		self.previewImg.setFile(self.data["dest"])

	def onEdit(self, *args, **kwargs):
		"""
			Edit the image entry.
		"""
		pane = Pane(translate("Edit"), closeable=True, iconClasses=[ "modul_%s" % self.parent.destModule,
		                                                                "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane(pane, focus=True)

		try:
			edwg = EditWidget(self.parent.destModule, EditWidget.appTree, key=self.data["dest"]["key"], skelType="leaf")
			pane.addWidget(edwg)
		except AssertionError:
			conf["mainWindow"].removePane(pane)

	def update(self):
		NetworkService.request(self.parent.destModule, "view/leaf",
		                        params={"key": self.data["dest"]["key"]},
		                        successHandler=self.onModuleViewAvailable)

class FileMultiSelectionBone( RelationalMultiSelectionBone ):

	def __init__(self, *args, **kwargs):
		super(FileMultiSelectionBone, self).__init__( *args, **kwargs )
		self.sinkEvent("onDragOver","onDrop")
		self["class"].append("supports_upload")

	def onDragOver(self, event):
		super(FileMultiSelectionBone,self).onDragOver(event)
		event.preventDefault()
		event.stopPropagation()

	def onDrop(self, event):
		event.preventDefault()
		event.stopPropagation()
		files = event.dataTransfer.files
		for x in range(0,files.length):
			ul = Uploader(files.item(x), None, context=self.context)
			ul.uploadSuccess.register( self )

	def onUploadSuccess(self, uploader, file ):
		self.setSelection([{"dest": file,"rel":{}}])
		self.changeEvent.fire(self)

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		currentSelector = FileWidget(self.destModule, isSelector="leaf")
		currentSelector.selectionReturnEvent.register(self)
		conf["mainWindow"].stackWidget(currentSelector)
		self.parent()["class"].append("is-active")

	def onSelectionReturn(self, table, selection ):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		hasValidSelection = False
		for s in selection:
			if isinstance( s, LeafFileWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return
		self.setSelection( [{"dest": x.data, "rel": {}} for x in selection if isinstance(x, LeafFileWidget)] )
		self.changeEvent.fire(self)

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict | list[dict]
		"""
		if selection is None:
			return

		for data in selection:
			entry = FileMultiSelectionBoneEntry(self, self.destModule, data, using=self.using, errorInfo={})
			self.addEntry( entry )

class FileSingleSelectionBone( RelationalSingleSelectionBone ):

	def __init__(self, *args, **kwargs):
		super(FileSingleSelectionBone, self).__init__( *args, **kwargs )
		self.sinkEvent("onDragOver","onDrop")
		self["class"].append("supports_upload")

		self.previewImg = FilePreviewImage()
		self.prependChild(self.previewImg)

		self.selection = None
		self.currentSelector = None

	def onDragOver(self, event):
		super(FileSingleSelectionBone,self).onDragOver(event)
		event.preventDefault()
		event.stopPropagation()

	def onDrop(self, event):
		event.preventDefault()
		event.stopPropagation()
		files = event.dataTransfer.files

		if files.length > 1:
			conf["mainWindow"].log("error",translate("You cannot drop more than one file here!"))
			return

		for x in range(0,files.length):
			ul = Uploader(files.item(x), None, context = self.context)
			ul.uploadSuccess.register( self )

	def onUploadSuccess(self, uploader, file):
		self.setSelection({"dest": file, "rel":{}})
		self.changeEvent.fire(self)

	def onShowSelector(self, *args, **kwargs):
		"""
			Opens a TreeWidget sothat the user can select new values
		"""
		if not self.currentSelector:
			fileSelector = conf.get("fileSelector")

			if not fileSelector or conf["mainWindow"].containsWidget(fileSelector):
				fileSelector = FileWidget(self.destModule, isSelector="leaf")

			if not conf.get("fileSelector"):
				conf["fileSelector"] = fileSelector

			self.currentSelector = fileSelector

		self.currentSelector.selectionReturnEvent.register(self, reset=True)

		conf["mainWindow"].stackWidget(self.currentSelector)
		self.parent().addClass("is_active")

	def onSelectionReturn(self, table, selection):
		"""
			Merges the selection made in the TreeWidget into our value(s)
		"""
		hasValidSelection = False
		for s in selection:
			if isinstance( s, LeafFileWidget ):
				hasValidSelection = True
				break
		if not hasValidSelection: #Its just a folder that's been activated
			return

		self.setSelection([{"dest": x.data for x in selection if isinstance(x,LeafFileWidget)}][0] )
		self.changeEvent.fire(self)

	def onDetach(self):
		super(FileSingleSelectionBone, self).onDetach()

		if self.currentSelector:
			self.currentSelector.selectionReturnEvent.unregister(self)

	def onEdit(self, *args, **kwargs):
		"""
			Edit the image.
		"""
		if not self.selection:
			return

		pane = Pane(translate("Edit"), closeable=True, iconClasses=[ "modul_%s" % self.destModule,
		                                                                "apptype_list", "action_edit" ] )
		conf["mainWindow"].stackPane(pane, focus=True)

		try:
			edwg = EditWidget(self.destModule, EditWidget.appTree, key=self.selection["dest"]["key"], skelType="leaf")
			pane.addWidget(edwg)
		except AssertionError:
			conf["mainWindow"].removePane(pane)

	def setSelection(self, selection):
		"""
			Set our current value to 'selection'
			@param selection: The new entry that this bone should reference
			@type selection: dict
		"""
		self.selection = selection

		if selection:
			NetworkService.request(self.destModule, "view/leaf/%s" % selection["dest"]["key"],
			                        successHandler=self.onSelectionDataAvailable,
			                        cacheable=True)
			self.selectionTxt["value"] = translate("Loading...")

			self.previewImg.setFile(self.selection["dest"])
		else:
			self.previewImg.setFile(None)
			self.selectionTxt["value"] = ""

		self.updateButtons()


def CheckForFileBoneSingleSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForFileBone( moduleName, boneName, skelStructure ) and not isMultiple

def CheckForFileBoneMultiSelection( moduleName, boneName, skelStructure, *args, **kwargs ):
	isMultiple = "multiple" in skelStructure[boneName].keys() and skelStructure[boneName]["multiple"]
	return CheckForFileBone( moduleName, boneName, skelStructure ) and isMultiple

def CheckForFileBone(  moduleName, boneName, skelStucture, *args, **kwargs ):
	#print("CHECKING FILE BONE", skelStucture[boneName]["type"])
	return( skelStucture[boneName]["type"].startswith("treeitem.file") )

#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForFileBoneSingleSelection, FileSingleSelectionBone)
editBoneSelector.insert( 5, CheckForFileBoneMultiSelection, FileMultiSelectionBone)
viewDelegateSelector.insert( 3, CheckForFileBone, FileViewBoneDelegate)
extractorDelegateSelector.insert(3, CheckForFileBone, FileBoneExtractor)
