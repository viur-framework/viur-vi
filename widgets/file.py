import html5
import json
import utils
from config import conf
from event import EventDispatcher
from i18n import translate
from network import NetworkService, DeferredCall
from priorityqueue import displayDelegateSelector, moduleHandlerSelector
from widgets.search import Search
from widgets.tree import TreeWidget, LeafWidget


class FileImagePopup(html5.ext.Popup):
	def __init__(self, preview, *args, **kwargs):
		super(FileImagePopup, self).__init__(title=preview.currentFile.get("name", translate("Unnamed Image")), className="image-viewer", *args, **kwargs)
		self.sinkEvent("onClick")
		self.preview = preview

		img = html5.Img()
		img["src"] = utils.getImagePreview(preview.currentFile, size=None)
		self.popupBody.appendChild(img)

		btn = html5.ext.Button(translate("Download"), self.onDownloadBtnClick)
		btn.addClass("btn--download")
		self.popupFoot.appendChild(btn)

		btn = html5.ext.Button(translate("Close"), self.onClick)
		btn.addClass("btn--close")
		self.popupFoot.appendChild(btn)


	def onClick(self, event):
		self.close()

	def onDownloadBtnClick(self, sender = None):
		self.preview.download()

class FilePreviewImage(html5.Div):
	def __init__(self, file = None, size=150, *args, **kwargs):
		super(FilePreviewImage, self).__init__(*args, **kwargs)
		self.addClass("previewimg")
		self.sinkEvent("onClick")

		self.size = size

		self.downloadA = html5.A()
		self.downloadA.hide()
		self.appendChild(self.downloadA)

		self.isImage = False
		self.downloadOnly = False
		self.currentFile = None

		self.setFile(file)

	def setFile(self, file):
		self.currentFile = file

		preview = utils.getImagePreview(file, cropped=True, size = self.size) if file else None

		if preview:
			self.downloadOnly = self.isImage = True

		else:
			self.isImage = False
			self.downloadOnly = True

			if file:
				preview = "embedsvg/icons-file.svg"
				mime = file.get("mimetype")
				if mime:
					for icon in ["bmp", "doc", "gif", "jpg", "pdf", "png", "tiff", "image", "audio", "video", "zip"]:
						if icon in mime:
							preview = "embedsvg/icons-%s-file.svg" % icon
							self.downloadOnly = False
							break

		if preview:
			self["style"]["background-image"] = "url('%s')" % preview
		else:
			self["style"]["background-image"] = None

		if self.currentFile:
			self.addClass("is-clickable")
		else:
			self.removeClass("is-clickable")


	def download(self):
		if not self.currentFile:
			return

		self.downloadA["href"] = "/file/download/" + self.currentFile["dlkey"]
		self.downloadA["download"] = self.currentFile.get("name", self.currentFile["dlkey"])
		self.downloadA.element.click()

	def onClick(self, event):
		if not self.currentFile:
			return

		if self.isImage:
			FileImagePopup(self)
		else:
			if self.downloadOnly:
				self.download()
				return

			file = "/file/download/%s" % self.currentFile["dlkey"]

			if self.currentFile.get("name"):
				file += "?fileName=%s" % self.currentFile["name"]

			html5.window.open(file)


class LeafFileWidget(LeafWidget):
	"""
		Displays a file inside a tree application.
	"""

	def __init__(self, modul, data, structure, *args, **kwargs):
		super(LeafFileWidget, self).__init__(modul, data, structure, *args, **kwargs)

		self.previewImg = FilePreviewImage(data)
		self.prependChild(self.previewImg)

		self.sinkEvent("onDragOver", "onDragLeave")

	def onDragOver(self, event):
		if not "insert-before" in self["class"]:
			self.addClass("insert-before")
		super(LeafFileWidget, self).onDragOver(event)

	def onDragLeave(self, event):
		if "insert-before" in self["class"]:
			self.removeClass("insert-before")
		super(LeafFileWidget,self).onDragLeave( event )


class Uploader(html5.Progress):
	"""
		Uploads a file to the server while providing visual feedback of the progress.
	"""

	def __init__(self, file, node, context=None, *args, **kwargs):
		"""
			@param file: The file to upload
			@type file: A javascript "File" Object
			@param node: Key of the desired node of our parents tree application or None for an anonymous upload.
			@type node: String or None
		"""
		super(Uploader, self).__init__(*args, **kwargs)
		self.uploadSuccess = EventDispatcher("uploadSuccess")
		self.responseValue = None
		self.context = context
		# self.files = files
		r = NetworkService.request("file", "getUploadURL", successHandler=self.onUploadUrlAvaiable, secure=True)
		r.file = file
		r.node = node
		conf["mainWindow"].log("progress", self)
		self.parent().addClass( "is-uploading" )

	def onUploadUrlAvaiable(self, req):
		"""
			Internal callback - the actual upload url (retrieved by calling /file/getUploadURL) is known.
		"""
		r = NetworkService.request("", "/admin/skey", successHandler=self.onSkeyAvaiable)
		r.file = req.file
		r.node = req.node
		r.destUrl = req.result

	def onSkeyAvaiable(self, req):
		"""
			Internal callback - the Security-Key is known.
		"""
		formData = eval("new FormData();")
		formData.append("file", req.file)

		if self.context:
			for k, v in self.context.items():
				formData.append(k, v)

		if req.node and str(req.node) != "null":
			formData.append("node", req.node)

		formData.append("skey", NetworkService.decode(req))
		self.xhr = eval("new XMLHttpRequest()")
		self.xhr.open("POST", req.destUrl)
		self.xhr.onload = self.onLoad
		self.xhr.upload.onprogress = self.onProgress
		self.xhr.send(formData)

	def onLoad(self, *args, **kwargs):
		"""
			Internal callback - The state of our upload changed.
		"""
		if self.xhr.status == 200:
			self.responseValue = json.loads(self.xhr.responseText)
			DeferredCall(self.onSuccess, _delay=1000)
		else:
			DeferredCall(self.onFailed, self.xhr.status, _delay=1000)

	def onProgress(self, event):
		"""
			Internal callback - further bytes have been transmitted
		"""
		if event.lengthComputable:
			complete = int(event.loaded / event.total * 100)
			self["value"] = complete
			self["max"] = 100

	def onSuccess(self, *args, **kwargs):
		"""
			Internal callback - The upload succeeded.
		"""
		for v in self.responseValue["values"]:
			self.uploadSuccess.fire(self, v)

		NetworkService.notifyChange("file")
		self.replaceWithMessage("Upload complete", isSuccess=True)

	def onFailed(self, errorCode, *args, **kwargs):
		self.replaceWithMessage("Upload failed with status code %s" % errorCode, isSuccess=False)

	def replaceWithMessage(self, message, isSuccess):
		self.parent().removeClass("is-uploading")
		self.parent().removeClass("log-progress")
		if isSuccess:
			self.parent().addClass("log-success")
		else:
			self.parent().addClass("log-failed")
		msg = html5.Span()
		msg.appendChild(html5.TextNode(message))
		self.parent().appendChild(msg)
		self.parent().removeChild(self)


class FileWidget(TreeWidget):
	"""
		Extends the TreeWidget to allow drag&drop upload of files to the current node.
	"""
	defaultActions = ["add.node", "add.leaf", "selectrootnode", "edit", "delete", "reload", "download"]
	leafWidget = LeafFileWidget

	def __init__(self, *args, **kwargs):
		super(FileWidget, self).__init__(*args, **kwargs)
		self.sinkEvent("onDragOver", "onDrop")
		self.addClass("supports-upload")
		self.search = Search()
		self.appendChild(self.search)
		self.search.startSearchEvent.register(self)

	def onStartSearch(self, searchStr, *args, **kwargs):
		if not searchStr:
			self.setRootNode(self.rootNode)
		else:
			for c in self.pathList._children[:]:
				self.pathList.removeChild(c)
			s = html5.Span()
			s.appendChild(html5.TextNode("Search"))
			self.pathList.appendChild(s)
			self.reloadData({"node": self.rootNode, "search": searchStr})

	def setNode(self, node):
		"""
			Override setNode sothat we can reset our search field if a folder has been clicked
		:param node:
		:return:
		"""
		self.search.searchInput["value"] = ""
		super(FileWidget, self).setNode(node)

	@staticmethod
	def canHandle(modul, moduleInfo):
		return (moduleInfo["handler"].startswith("tree.simple.file"))

	def onDragOver(self, event):
		event.preventDefault()
		event.stopPropagation()

	# print("%s %s" % (event.offsetX, event.offsetY))

	def onDrop(self, event):
		event.preventDefault()
		event.stopPropagation()
		files = event.dataTransfer.files
		for x in range(0, files.length):
			Uploader(files.item(x), self.node)

	@staticmethod
	def render(moduleName, adminInfo, context):
		rootNode = context.get("rootNode") if context else None
		return FileWidget(module=moduleName, rootNode=rootNode, context=context)


displayDelegateSelector.insert(3, FileWidget.canHandle, FileWidget)
moduleHandlerSelector.insert(3, FileWidget.canHandle, FileWidget.render)
