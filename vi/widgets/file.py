import json, pyodide
from flare import html5
from flare.button import Button
from flare.icons import SvgIcon
from flare.popup import Popup
from flare.i18n import translate
from flare.ignite import Progress
import vi.utils as utils
from vi.config import conf

from vi.widgets.tree import TreeLeafWidget, TreeNodeWidget, TreeBrowserWidget
from vi.widgets.search import Search
from flare.icons import Icon


from flare.event import EventDispatcher
from flare.network import NetworkService, DeferredCall, requestGroup
from vi.priorityqueue import displayDelegateSelector, moduleWidgetSelector

class FileImagePopup(Popup):
	def __init__(self, preview, *args, **kwargs):
		super(FileImagePopup, self).__init__(title=preview.currentFile.get("name", translate("Unnamed Image")), className="image-viewer", *args, **kwargs)
		self.sinkEvent("onClick")
		self.preview = preview

		img = html5.Img()
		img["src"] = utils.getImagePreview(preview.currentFile, size=None)
		self.popupBody.appendChild(img)

		btn = Button(translate("Download"), self.onDownloadBtnClick)
		btn.addClass("btn--download")
		self.popupFoot.appendChild(btn)

		btn = Button(translate("Close"), self.onClick)
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
								svg = "icon-%s-file" % icon
								self.downloadOnly = False
								break
			else:
				self.addClass("no-preview")

			if not svg:
				svg = "icon-file"

		if preview:
			self.removeClass("no-preview")

		self.previewIcon = Icon( preview or svg, title = self.currentFile.get("name"))
		self.appendChild(self.previewIcon)

		if self.currentFile:
			self.addClass("is-clickable")
		else:
			self.removeClass("is-clickable")

	def download(self):
		if not self.currentFile:
			return

		self.downloadA["href"] = self.currentFile["downloadUrl"]
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
				file = "%s/fileName=%s" % (self.currentFile[ "downloadUrl" ], self.currentFile["name"])

			html5.window.open(file)

class Uploader(html5.Div):
	"""
		Uploads a file to the server while providing visual feedback of the progress.
	"""

	def __init__(self, file, node, context=None, module="file", *args, **kwargs):
		"""
			:param file: The file to upload
			:type file: A javascript "File" Object
			:param node: Key of the desired node of our parents tree application or None for an anonymous upload.
			:type node: str or None
		"""
		super(Uploader, self).__init__()
		self.uploadSuccess = EventDispatcher("uploadSuccess")
		self.module = module
		self.responseValue = None
		self.targetKey = None
		self.addClass("is-loading")
		self.appendChild(SvgIcon("icon-loader", title = "uploading..."))
		self.proxy_callback = None
		self.context = context
		params = {"fileName": file.name, "mimeType": (file.type or "application/octet-stream")}
		if node:
			params["node"] = node

		r = NetworkService.request(module, "getUploadURL",
			params=params,
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
		params = NetworkService.decode(req)["values"]

		self.proxy_callback = pyodide.create_proxy(self.onLoad)

		if "uploadKey" in params:  # New Resumeable upload format
			self.targetKey = params["uploadKey"]
			html5.window.fetch(params["uploadUrl"], **{"method": "POST", "body": req.file, "mode": "no-cors"}).then(
				self.proxy_callback)
		else:
			formData = html5.jseval( "new FormData();" )

			for key, value in params[ "params" ].items():
				if key == "key":
					self.targetKey = value[ :-16 ]  # Truncate source/file.dat
					fileName = req.file.name
					value = value.replace( "file.dat", fileName )

				formData.append( key, value )
			formData.append( "file", req.file )

			html5.window.fetch( params[ "url" ], **{ "method": "POST", "body": formData, "mode": "no-cors" } ).then( self.proxy_callback )


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
		NetworkService.request(
			self.module, "add", {
				"key": self.targetKey,
				"node": self.node,
				"skelType": "leaf"
			},
			successHandler = self.onUploadAdded,
			failureHandler = self.onFailed,
			secure = True
		)
		if self.proxy_callback:
			self.proxy_callback.destroy()
		return 0

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

class MultiUploader(html5.Div):
	def __init__(self, files, node, context=None, module="file", *args, **kwargs):
		"""
			:param file: The file to upload
			:type file: A javascript "File" Object
			:param node: Key of the desired node of our parents tree application or None for an anonymous upload.
			:type node: str or None
		"""
		super(MultiUploader, self).__init__()
		self.uploadSuccess = EventDispatcher("uploadSuccess")
		self.module = module
		self.node = node
		self.responseValue = None
		self.targetKey = None
		#self.addClass("is-loading")
		#self.appendChild(SvgIcon("icon-loader", title="uploading..."))
		self.msg = html5.Span(html5.TextNode("uploading..."))
		self.appendChild(self.msg )
		self.context = context
		self.files = files
		self.filesToUpload = files[:]
		self.proxy_callback=None
		self.handleFile(self.filesToUpload.pop(0))

		self.logMessage = conf["mainWindow"].log("progress", self)
		self.parent().addClass("is-uploading")

	def handleFile(self, file):
		print("uploading %s/%s" % (len(self.files) - len(self.filesToUpload), len(self.files)))

		params = {"fileName": file.name, "mimeType": (file.type or "application/octet-stream")}
		if self.node:
			params["node"] = self.node


		## request uploadurl with skey
		r = NetworkService.request(self.module, "getUploadURL",
								   params=params,
								   successHandler=self.onUploadUrlAvailable,
								   failureHandler=self.onFailed,
								   secure=True,
								   )
		r.file = file
		r.node = self.node
		self.replaceWithMessage("Uploading %s/%s" % (len(self.files) - len(self.filesToUpload), len(self.files)),
								isSuccess="progress")

	def onUploadUrlAvailable(self, req):
		"""
			Internal callback - the actual upload url (retrieved by calling /file/getUploadURL) is known.
		"""
		params = NetworkService.decode(req)["values"]

		self.proxy_callback = pyodide.create_proxy(self.onLoad)

		if "uploadKey" in params:  # New Resumeable upload format
			self.targetKey = params["uploadKey"]
			html5.window.fetch(params["uploadUrl"], **{"method": "POST", "body": req.file, "mode": "no-cors"}).then(
				self.proxy_callback)
		else:
			formData = html5.jseval("new FormData();")

			for key, value in params["params"].items():
				if key == "key":
					self.targetKey = value[:-16]  # Truncate source/file.dat
					fileName = req.file.name
					value = value.replace("file.dat", fileName)

				formData.append(key, value)
			formData.append("file", req.file)

			html5.window.fetch(params["url"], **{"method": "POST", "body": formData, "mode": "no-cors"}).then(self.proxy_callback)

	def onLoad(self, *args, **kwargs):
		"""
			Internal callback - The state of our upload changed.
		"""
		NetworkService.request(
			self.module, "add", {
				"key": self.targetKey,
				"node": self.node,
				"skelType": "leaf"
			},
			successHandler=self.onUploadAdded,
			failureHandler=self.onFailed,
			secure=True
		)
		if self.proxy_callback:
			self.proxy_callback.destroy()
		return 0

	def onUploadAdded(self, req):
		self.responseValue = NetworkService.decode(req)
		DeferredCall(self.onSuccess, _delay=1000)

	def onSuccess(self, *args, **kwargs):
		"""
			Internal callback - The upload succeeded.
		"""
		if isinstance(self.responseValue["values"], list):
			for v in self.responseValue["values"]:
				self.uploadSuccess.fire(self, v)

		else:
			self.uploadSuccess.fire(self, self.responseValue["values"])

		if len(self.filesToUpload) == 0:
			NetworkService.notifyChange("file")
			self.replaceWithMessage("Upload complete", isSuccess="finished")
			self.parent().removeClass("is-uploading")
			self.parent().removeClass("log-progress")
			DeferredCall(self.closeMessage,_delay=2500)
		else:
			self.handleFile(self.filesToUpload.pop(0))


	def onFailed(self, errorCode, *args, **kwargs):
		self.replaceWithMessage("Upload failed with status code %s" % errorCode, isSuccess=False)

	def replaceWithMessage(self, message, isSuccess):
		if isSuccess == "finished":
			self.parent().addClass("log-success")
		elif not isSuccess:
			self.parent().addClass("log-failed")

		self.removeChild(self.msg)
		self.msg = html5.Span(html5.TextNode(message))
		self.appendChild(self.msg )

	def closeMessage(self):
		conf["mainWindow"].logWdg.removeInfo(self.logMessage)

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

import logging

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

	def onDrop(self, event):
		event.preventDefault()
		event.stopPropagation()
		self.removeClass("insert-here")
		files = event.dataTransfer.files
		if files:
			filelist = []

			for x in range(0,len(files)):
				filelist.append(files.item(x))

			if len(filelist) == 1:
				Uploader(files.item(0), self.node, self.module)
			else:
				MultiUploader(filelist, self.node, self.module)
		else:
			super().onDrop(event)

	@staticmethod
	def canHandle( module, moduleInfo ):
		return (moduleInfo[ "handler" ].startswith( "tree.file" ) or moduleInfo[ "handler" ].startswith( "tree.simple.file" ) )

moduleWidgetSelector.insert(5, FileWidget.canHandle, FileWidget)
displayDelegateSelector.insert(5, FileWidget.canHandle, FileWidget)
