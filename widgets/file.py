import html5
from network import NetworkService, DeferredCall
from widgets.tree import TreeWidget, LeafWidget
from priorityqueue import displayDelegateSelector

class LeafFileWidget( LeafWidget ):
	def __init__(self, modul, data, *args, **kwargs ):
		super( LeafFileWidget, self ).__init__( modul, data, *args, **kwargs )
		if "servingurl" in data.keys():
			self.appendChild( html5.Img( data["servingurl"]) )
		if "metamime" in data.keys():
			try:
				ftype, fformat = data["metamime"].split("/")
				self["class"].append("type_%s" % ftype )
				self["class"].append("format_%s" % fformat )
			except:
				pass
		self["class"].append("file")

class Uploader( html5.Progress ):
	def __init__(self, file, node, *args, **kwargs):
		super(Uploader, self).__init__( *args, **kwargs )
		#self.files = files
		r = NetworkService.request("file","getUploadURL", successHandler=self.onUploadUrlAvaiable, secure=True)
		r.file = file
		r.node = node

	def onUploadUrlAvaiable(self, req ):
		r = NetworkService.request("","/skey", successHandler=self.onSkeyAvaiable)
		r.file = req.file
		r.node = req.node
		r.destUrl = req.result

	def onSkeyAvaiable(self, req):
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
		if self.xhr.status==200:
			print("UPLOAD OKAY")
			DeferredCall(self.onSuccess, _delay=1000)
		else:
			print("UPLOAD FAILED")

	def onProgress(self, event):
		print(event.lengthComputable)
		if event.lengthComputable:
			complete = int(event.loaded / event.total * 100 )
			self["value"] = complete
			self["max"] = 100

	def onSuccess(self, *args, **kwargs):
		self.parent().removeChild(self)
		NetworkService.notifyChange("file")

class FileWidget( TreeWidget ):
	leafWidget = LeafFileWidget

	def __init__(self,*args, **kwargs):
		super( FileWidget, self ).__init__( *args, **kwargs)
		self.sinkEvent("onDragOver", "onDrop")

	@staticmethod
	def canHandle( modul, modulInfo ):
		print(modulInfo["handler"].startswith("tree.simple.file" ))
		return( modulInfo["handler"].startswith("tree.simple.file" ) )

	def onDragOver(self, event):
		print("DRAG OVER")
		event.preventDefault()
		event.stopPropagation()
		#print("%s %s" % (event.offsetX, event.offsetY))


	def onDrop(self, event):
		print("DROP EVENT")
		event.preventDefault()
		event.stopPropagation()
		files = event.dataTransfer.files
		for x in range(0,files.length):
			self.appendChild( Uploader(files.item(x), self.node ))

displayDelegateSelector.insert( 3, FileWidget.canHandle, FileWidget )