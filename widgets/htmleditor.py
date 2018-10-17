import html5
import network
from __pyjamas__ import JS
from i18n import translate


class TextInsertImageAction(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(TextInsertImageAction, self).__init__(translate("Insert Image"), *args, **kwargs)
		self["class"] = "icon text image"
		self["title"] = translate("Insert Image")

	def onClick(self, sender=None):
		currentSelector = FileWidget("file", isSelector=True)
		currentSelector.selectionActivatedEvent.register(self)
		conf["mainWindow"].stackWidget(currentSelector)

	def onSelectionActivated(self, selectWdg, selection):
		print("onSelectionActivated")

		if not selection:
			return

		print(selection)

		for item in selection:
			dataUrl = "/file/download/%s/%s" % (item.data["dlkey"], item.data["name"].replace("\"", ""))
			if "mimetype" in item.data.keys() and item.data["mimetype"].startswith("image/"):
				print "insert img %s " % dataUrl
			# self.execCommand("insertImage", dataUrl)
			else:
				print "insert link %s " % dataUrl
		# self.execCommand("createLink", dataUrl + "?download=1")

	@staticmethod
	def isSuitableFor(modul, handler, actionName):
		return (actionName == "text.image")

	def resetLoadingState(self):
		pass


# actionDelegateSelector.insert( 1, TextInsertImageAction.isSuitableFor, TextInsertImageAction )


# class ImageEditor( html5.Div ):
# 	def __init__(self, *args, **kwargs):
# 		super( ImageEditor, self ).__init__( *args, **kwargs )
# 		self["class"].append("imageeditor")
# 		self["style"]["display"] = "none"
# 		self.widthInput = html5.Input()
# 		self.widthInput["type"] = "number"
# 		self.appendChild(self.widthInput)
# 		l = html5.Label(translate("Width"), self.widthInput)
# 		l["class"].append("widthlbl")
# 		self.appendChild( l )
# 		self.keepAspectRatio = html5.Input()
# 		self.keepAspectRatio["type"] = "checkbox"
# 		self.appendChild( self.keepAspectRatio )
# 		l = html5.Label(translate("Keep aspect ratio"), self.keepAspectRatio)
# 		l["class"].append("aspectlbl")
# 		self.appendChild( l )
# 		self.heightInput = html5.Input()
# 		self.heightInput["type"] = "number"
# 		self.appendChild(self.heightInput)
# 		l = html5.Label(translate("Height"), self.heightInput)
# 		l["class"].append("heightlbl")
# 		self.appendChild( l )
# 		self.titleInput = html5.Input()
# 		self.titleInput["type"] = "text"
# 		self.appendChild(self.titleInput)
# 		l = html5.Label(translate("Title"), self.titleInput)
# 		l["class"].append("titlelbl")
# 		self.appendChild( l )
# 		self.currentElem = None
# 		self.sinkEvent("onChange")
#
# 	def onChange(self, event):
# 		super(ImageEditor,self).onChange( event )
# 		aspect = self.currentElem.naturalWidth/self.currentElem.naturalHeight
# 		if event.target == self.widthInput.element:
# 			if self.keepAspectRatio["checked"]:
# 				self.heightInput["value"] = int(float(self.widthInput["value"])/aspect)
# 		elif event.target == self.heightInput.element:
# 			if self.keepAspectRatio["checked"]:
# 				self.widthInput["value"] = int(float(self.heightInput["value"])*aspect)
# 		self.currentElem.width = int(self.widthInput["value"])
# 		self.currentElem.height = int(self.heightInput["value"])
#
# 	def getImgFromTagStack(self, tagStack):
# 		for elem in tagStack:
# 			if not "tagName" in dir(elem):
# 				continue
# 			if elem.tagName=="IMG":
# 				return( elem )
# 		return( None )
#
# 	def onCursorMoved(self, tagStack):
# 		newElem = self.getImgFromTagStack(tagStack)
# 		if newElem is not None and self.currentElem is not None:
# 			self.doClose()
# 			self.doOpen( newElem )
# 		elif self.currentElem is None and newElem is not None:
# 			self.doOpen( newElem )
# 		elif self.currentElem is not None and newElem is None:
# 			self.doClose()
#
# 	def doOpen(self, elem):
# 		self.currentElem = elem
# 		self["style"]["display"] = ""
# 		self.heightInput["value"] = elem.height
# 		self.widthInput["value"] = elem.width
# 		self.titleInput["value"] = elem.title
#
# 	def doClose(self):
# 		if self.currentElem is None:
# 			return
# 		self.currentElem.width = int( self.widthInput["value"] )
# 		self.currentElem.height = int( self.heightInput["value"] )
# 		self.currentElem.title = self.titleInput["value"]
# 		self["style"]["display"] = "none"
# 		self.currentElem = None
#
# 	def findImg(self, linkTarget, elem):
# 		if "tagName" in dir(elem):
# 			if elem.tagName == "IMG":
# 				if elem.href == linkTarget or elem.href.endswith(linkTarget):
# 					return( elem )
# 		if "children" in dir(elem):
# 			for x in range(0,elem.children.length):
# 				child = elem.children.item(x)
# 				r = self.findImg( linkTarget, child)
# 				if r is not None:
# 					return( r )
# 		return( None )
#
# 	def openLink(self, linkTarget):
# 		self.doOpen( self.findHref( linkTarget, self.parent().editor.element ) )
# 		self.linkTxt["value"] = ""
# 		self.linkTxt.focus()


class HtmlEditor(html5.Div):
	def __init__(self, input, *args, **kwargs):
		super(HtmlEditor, self).__init__(*args, **kwargs)

		self.value = ""
		self.summernote = None
		self.enabled = True

		# FIXME build imagewidget
		imagebtn = TextInsertImageAction()
		self.appendChild(imagebtn)

		self.summernoteContainer = self

	def _attachSummernote(self, retry=0):
		elem = self.summernoteContainer.element

		try:
			self.summernote = JS("""window.top.createSummernote(@{{elem}})""")

		except:
			if retry >= 3:
				alert("Unable to connect summernote, please contact technical support...")
				return

			print("Summernote initialization failed, retry will start in 1sec")
			network.DeferredCall(self._attachSummernote, retry=retry + 1, _delay=1000)
			return

		self.summernote.on("summernote.change", self.onEditorChange)

		if self.value:
			self["value"] = self.value

	def onAttach(self):
		super(HtmlEditor, self).onAttach()

		if self.summernote:
			return

		self._attachSummernote()

		if not self.enabled:
			self.summernote.summernote("disable")

	def onDetach(self):
		super(HtmlEditor, self).onDetach()
		self.value = self["value"]
		self.summernote.summernote('destroy')
		self.summernote = None

	def onEditorChange(self, e, *args, **kwargs):
		if self.parent():
			e = JS("new Event('keyup')")
			self.parent().element.dispatchEvent(e)

	def _getValue(self):
		if not self.summernote:
			return self.value

		ret = self.summernote.summernote("code")
		return ret

	def _setValue(self, val):
		if not self.summernote:
			self.value = val
			return

		self.summernote.summernote("code", val)
		self.summernote.summernote("editor.historyReset")

	def enable(self):
		super(HtmlEditor, self).enable()

		self.enabled = True
		self.removeClass("is-disabled")

		if self.summernote:
			self.summernote.summernote("enable")

	def disable(self):
		super(HtmlEditor, self).disable()

		self.enabled = False
		self.addClass("is-disabled")

		if self.summernote:
			self.summernote.summernote("disable")
