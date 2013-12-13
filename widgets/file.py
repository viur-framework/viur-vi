import html5
from network import NetworkService, DeferredCall
from widgets.tree import TreeWidget, LeafWidget
from priorityqueue import displayDelegateSelector
from event import EventDispatcher
from config import conf
import json

class LeafFileWidget( LeafWidget ):
	"""
		Displays a file inside a tree application.
	"""
	def __init__(self, modul, data, structure, *args, **kwargs ):
		super( LeafFileWidget, self ).__init__( modul, data, structure, *args, **kwargs )
		if "servingurl" in data.keys():
			self.appendChild( html5.Img( data["servingurl"]) )
		if "mimetype" in data.keys():
			try:
				ftype, fformat = data["mimetype"].split("/")
				self["class"].append("type_%s" % ftype )
				self["class"].append("format_%s" % fformat )
			except:
				pass
		self["class"].append("file")

class Uploader( html5.Progress ):
	"""
		Uploads a file to the server while providing visual feedback of the progress.
	"""
	def __init__(self, file, node, *args, **kwargs):
		"""
			@param file: The file to upload
			@type file: A javascript "File" Object
			@param node: Key of the desired node of our parents tree application or None for an anonymous upload.
			@type node: String or None
		"""
		super(Uploader, self).__init__( *args, **kwargs )
		self.uploadSuccess = EventDispatcher("uploadSuccess")
		self.responseValue = None
		#self.files = files
		r = NetworkService.request("file","getUploadURL", successHandler=self.onUploadUrlAvaiable, secure=True)
		r.file = file
		r.node = node
		conf["mainWindow"].log("progress", self)
		self.parent()["class"].append( "is_uploading" )

	def onUploadUrlAvaiable(self, req ):
		"""
			Internal callback - the actual upload url (retrieved by calling /file/getUploadURL) is known.
		"""
		r = NetworkService.request("","/skey", successHandler=self.onSkeyAvaiable)
		r.file = req.file
		r.node = req.node
		r.destUrl = req.result

	def onSkeyAvaiable(self, req):
		"""
			Internal callback - the Security-Key is known.
		"""
		formData = eval("new FormData();")
		formData.append("file", req.file )
		formData.append("node", req.node )
		formData.append("skey", NetworkService.decode(req) )
		self.xhr = eval("new XMLHttpRequest()")
		self.xhr.open("POST", req.destUrl )
		self.xhr.onload = self.onLoad
		self.xhr.upload.onprogress = self.onProgress
		self.xhr.send( formData )

	def onLoad(self, *args, **kwargs ):
		"""
			Internal callback - The state of our upload changed.
		"""
		if self.xhr.status==200:
			print("UPLOAD OKAY")
			self.responseValue = json.loads( self.xhr.responseText )
			DeferredCall(self.onSuccess, _delay=1000)
		else:
			print("UPLOAD FAILED")

	def onProgress(self, event):
		"""
			Internal callback - further bytes have been transmitted
		"""
		if event.lengthComputable:
			complete = int(event.loaded / event.total * 100 )
			self["value"] = complete
			self["max"] = 100

	def onSuccess(self, *args, **kwargs):
		"""
			Internal callback - The upload succeeded.
		"""
		for v in self.responseValue["values"]:
			self.uploadSuccess.fire( self, v )
		NetworkService.notifyChange("file")
		self.parent()["class"].remove("is_uploading")
class FileWidget( TreeWidget ):
	"""
		Extends the TreeWidget to allow drag&drop upload of files to the current node.
	"""
	leafWidget = LeafFileWidget

	def __init__(self,*args, **kwargs):
		super( FileWidget, self ).__init__( *args, **kwargs)
		self.sinkEvent("onDragOver", "onDrop")
		self["class"].append("supports_upload")

	@staticmethod
	def canHandle( modul, modulInfo ):
		return( modulInfo["handler"].startswith("tree.simple.file" ) )

	def onDragOver(self, event):
		event.preventDefault()
		event.stopPropagation()
		#print("%s %s" % (event.offsetX, event.offsetY))


	def onDrop(self, event):
		event.preventDefault()
		event.stopPropagation()
		files = event.dataTransfer.files
		for x in range(0,files.length):
			Uploader(files.item(x), self.node )

displayDelegateSelector.insert( 3, FileWidget.canHandle, FileWidget )