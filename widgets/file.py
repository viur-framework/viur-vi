import json
from vi import html5
from vi.i18n import translate
import vi.utils as utils
from vi.config import conf

from vi.widgets.tree import TreeLeafWidget, TreeNodeWidget, TreeBrowserWidget
from vi.widgets.search import Search
from vi.framework.components.icon import Icon


from vi.framework.event import EventDispatcher
from vi.network import NetworkService, DeferredCall
from vi.priorityqueue import displayDelegateSelector, moduleWidgetSelector




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
		self.preview.imageDownload = True
		self.preview.download()

class FilePreviewImage(html5.Div):
	def __init__(self, file = None, size=150, *args, **kwargs):
		super(FilePreviewImage, self).__init__(*args, **kwargs)
		self.addClass("vi-file-imagepreview")
		self.sinkEvent("onClick")

		self.size = size

		self.downloadA = html5.A()
		self.downloadA.hide()
		self.appendChild(self.downloadA)
		self.isImage = False
		self.downloadOnly = False
		self.currentFile = None
		self.previewIcon = None
		self.setFile(file)
		self.imageDownload = False

	def setFile(self, file):
		if self.previewIcon:
			self.removeChild(self.previewIcon)

		if not file:
			self.addClass("is-hidden")
			return

		self.removeClass("is-hidden")

		svg = None
		self.currentFile = file

		preview = utils.getImagePreview(file, cropped=True, size=self.size) if file else None

		if preview:
			self.downloadOnly = self.isImage = True

		else:
			self.isImage = False
			self.downloadOnly = True

			if file:
				mime = file.get("mimetype")
				if mime:
					for mimesplit in mime.split("/"):
						for icon in ["text", "pdf", "image", "audio", "video", "zip"]:
							if icon in mimesplit:
								svg = "icons-%s-file" % icon
								self.downloadOnly = False
								break
			else:
				self.addClass("no-preview")

			if not svg:
				svg = "icons-file"

		if preview:
			self.removeClass("no-preview")

		self.previewIcon = Icon(self.currentFile.get("name"), preview or svg)
		self.appendChild(self.previewIcon)

		if self.currentFile:
			self.addClass("is-clickable")
		else:
			self.removeClass("is-clickable")

	def download(self):
		if not self.currentFile:
			return

		if conf["core.version"][0] == 3:
			self.downloadA["href"] = self.currentFile["downloadUrl"]
		else:
			self.downloadA["href"] = "/file/download/" + self.currentFile["dlkey"]
			self.downloadA["download"] = self.currentFile.get("name", self.currentFile["dlkey"])
		self.downloadA["target"] = "_blank"
		self.downloadA.element.click()

	def onClick(self,sender=None):
		if not self.currentFile:
			return

		if self.isImage and not self.imageDownload:
			FileImagePopup(self)
		else:
			self.imageDownload = False
			if self.downloadOnly:
				self.download()
				return

			if self.currentFile.get("name"):
				if conf["core.version"][0] == 3:
					file = "%s/fileName=%s" % (self.currentFile[ "downloadUrl" ], self.currentFile["name"])
				else:
					file = "/file/download/%s/%s" % (self.currentFile[ "dlkey" ], self.currentFile["name"])

			html5.window.open(file)

class Uploader(html5.ignite.Progress):
	"""
		Uploads a file to the server while providing visual feedback of the progress.
	"""

	def __init__(self, file, node, context=None, *args, **kwargs):
		"""
			:param file: The file to upload
			:type file: A javascript "File" Object
			:param node: Key of the desired node of our parents tree application or None for an anonymous upload.
			:type node: str or None
		"""
		super(Uploader, self).__init__()
		self.uploadSuccess = EventDispatcher("uploadSuccess")
		self.responseValue = None
		self.targetKey = None

		self.context = context

		r = NetworkService.request("file", "getUploadURL",
			params={"node": node} if node else {},
			successHandler=self.onUploadUrlAvailable,
			failureHandler=self.onFailed,
			secure=True
		)
		r.file = file
		r.node = node
		self.node = node

		conf["mainWindow"].log("progress", self)
		self.parent().addClass("is-uploading")

	def onUploadUrlAvailable(self, req):
		"""
			Internal callback - the actual upload url (retrieved by calling /file/getUploadURL) is known.
		"""
		if conf["core.version"][0] == 3:
			params = NetworkService.decode(req)["values"]

			formData = html5.jseval("new FormData();")

			#if self.context:
			#	for k, v in self.context.items():
			#		formData.append(k, v)

			#if req.node and str(req.node) != "null":
			#	formData.append("node", req.node)

			for key, value in params["params"].items():
				if key == "key":
					self.targetKey = value[:-16]  # Truncate source/file.dat
					fileName = req.file.name
					value = value.replace("file.dat", fileName)

				formData.append(key, value)
			formData.append("file", req.file)

			html5.window.fetch(params["url"], {"method": "POST", "body": formData, "mode": "no-cors"}).then(self.onLoad)

		else:
			r = NetworkService.request("", "/vi/skey", successHandler=self.onSkeyAvailable)
			r.file = req.file
			r.node = req.node
			r.destUrl = req.result


	def onSkeyAvailable(self, req):
		"""
			Internal callback - the Security-Key is known.
			Only for core 2.x needed
		"""
		formData = html5.jseval("new FormData();")
		formData.append("file", req.file)

		if self.context:
			for k, v in self.context.items():
				formData.append(k, v)

		if req.node and str(req.node) != "null":
			formData.append("node", req.node)

		formData.append("skey", NetworkService.decode(req))
		self.xhr = html5.jseval("new XMLHttpRequest()")
		self.xhr.open("POST", req.destUrl)
		self.xhr.onload = self.onLoad
		self.xhr.upload.onprogress = self.onProgress
		self.xhr.send(formData)

	def onLoad(self, *args, **kwargs):
		"""
			Internal callback - The state of our upload changed.
		"""
		if conf["core.version"][0] == 3:
			NetworkService.request(
				"file", "add", {
					"key": self.targetKey,
					"node": self.node,
					"skelType": "leaf"
				},
			    successHandler=self.onUploadAdded,
				failureHandler=self.onFailed,
				secure=True
				)
		else:
			if self.xhr.status == 200:
				self.responseValue = json.loads(self.xhr.responseText)
				DeferredCall(self.onSuccess, _delay=1000)
			else:
				DeferredCall(self.onFailed, self.xhr.status, _delay=1000)

	def onUploadAdded(self, req):
		self.responseValue = NetworkService.decode(req)
		DeferredCall(self.onSuccess, _delay=1000)

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
		if isinstance(self.responseValue["values"], list):
			for v in self.responseValue["values"]:
				self.uploadSuccess.fire(self, v)

		else:
			self.uploadSuccess.fire(self, self.responseValue["values"])

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

class FileLeafWidget(TreeLeafWidget):

	def EntryIcon( self ):
		self.previewImg = FilePreviewImage( self.data )
		self.nodeImage.appendChild( self.previewImg )
		self.nodeImage.removeClass( "is-hidden" )

	def setStyle( self ):
		self.buildDescription()
		self.EntryIcon()

class FileNodeWidget(TreeNodeWidget):
	def setStyle( self ):
		self.buildDescription()
		self.EntryIcon()

class FileWidget(TreeBrowserWidget):

	leafWidget = FileLeafWidget
	nodeWidget = FileNodeWidget

	def __init__( self, module, rootNode = None, selectMode = None, node=None, context = None, *args, **kwargs ):
		super(FileWidget,self).__init__(module,rootNode,selectMode,node,context,*args,**kwargs)
		self.searchWidget()
		self.addClass("supports-upload")
		self.entryFrame.addClass( "vi-tree-selectioncontainer" )
		self.entryFrame["title"] = "Ziehe Deine Dateien hier her."

	def searchWidget( self ):
		searchBox = html5.Div()
		searchBox.addClass( "vi-search-wrap" )
		self.appendChild( searchBox )

		self.search = Search()
		self.search.addClass( "input-group" )
		searchBox.appendChild( self.search )
		self.search.searchLbl.addClass( "label" )
		self.search.startSearchEvent.register( self )

	def onStartSearch(self, searchStr, *args, **kwargs):
		if not searchStr:
			self.setRootNode(self.rootNode)
		else:
			for c in self.entryFrame._children[ : ]:
				self.entryFrame.removeChild( c )

			for c in self.pathList._children[:]:
				self.pathList.removeChild(c)
			s = html5.Span()
			s.appendChild(html5.TextNode("Search"))
			self.pathList.appendChild(s)
			self.loadNode(node = self.rootNode ,overrideParams = {"search": searchStr})

	def getChildKey(self, widget):
		"""
			Derives a string used to sort the entries on each level
		"""
		name = str(widget.data.get("name")).lower()

		if isinstance(widget, self.nodeWidget):
			return "0-%s" % name
		elif isinstance(widget, self.leafWidget):
			return "1-%s" % name
		else:
			return "2-"


	@staticmethod
	def canHandle( module, moduleInfo ):
		return (moduleInfo[ "handler" ].startswith( "tree.file" ) or moduleInfo[ "handler" ].startswith( "tree.simple.file" ) )


moduleWidgetSelector.insert(2, FileWidget.canHandle, FileWidget)
displayDelegateSelector.insert(2, FileWidget.canHandle, FileWidget)
