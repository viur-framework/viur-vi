import html5
import network
from __pyjamas__ import JS
from event import EventDispatcher
from i18n import translate
from priorityqueue import actionDelegateSelector
from widgets.actionbar import ActionBar


# class BasicEditorAction(html5.ext.Button):
#
# 	def execCommand(self, *args, **kwargs):
# 		return self.parent().parent().editor.execCommand(*args, **kwargs)
#
# class BasicTextAction(BasicEditorAction):
# 	cmd = None
# 	isActiveTag = None
# 	title = None
#
# 	def __init__(self, *args, **kwargs):
# 		assert self.cmd is not None
# 		super( BasicTextAction, self ).__init__( self.cmd, *args, **kwargs )
# 		self["class"] = "icon text style"
# 		self["class"].append( self.cmd )
# 		if self.title:
# 			self["title"] = self.title
#
# 	def onAttach(self):
# 		super(BasicTextAction, self).onAttach( )
# 		if self.isActiveTag:
# 			self.parent().parent().cursorMovedEvent.register( self )
#
# 	def onDetach(self):
# 		super(BasicTextAction, self).onDetach( )
# 		if self.isActiveTag:
# 			self.parent().parent().cursorMovedEvent.unregister( self )
#
# 	def onCursorMoved(self, nodeStack):
# 		if self.isActiveTag in [(x.tagName if "tagName" in dir(x) else "") for x in nodeStack]:
# 			if not "isactive" in self["class"]:
# 				self["class"].append("isactive")
# 		else:
# 			if "isactive" in self["class"]:
# 				self["class"].remove("isactive")
#
# 	def onClick(self, sender=None):
# 		self.execCommand(self.cmd)
#
# 	def resetLoadingState(self):
# 		pass
#
#
#
#
#
# class TextInsertImageAction(BasicEditorAction):
# 	def __init__(self, *args, **kwargs):
# 		super( TextInsertImageAction, self ).__init__( translate("Insert Image"), *args, **kwargs )
# 		self["class"] = "icon text image"
# 		self["title"] = translate("Insert Image")
#
# 	def onClick(self, sender=None):
# 		currentSelector = FileWidget( "file", isSelector=True )
# 		currentSelector.selectionActivatedEvent.register( self )
# 		conf["mainWindow"].stackWidget( currentSelector )
#
# 	def onSelectionActivated(self, selectWdg, selection):
# 		print("onSelectionActivated")
#
# 		if not selection:
# 			return
#
# 		print(selection)
#
# 		for item in selection:
# 			dataUrl = "/file/download/%s/%s" % (item.data["dlkey"], item.data["name"].replace("\"",""))
# 			if "mimetype" in item.data.keys() and item.data["mimetype"].startswith("image/"):
# 				self.execCommand("insertImage", dataUrl)
# 			else:
# 				self.execCommand("createLink", dataUrl + "?download=1")
#
# 	@staticmethod
# 	def isSuitableFor( modul, handler, actionName ):
# 		return( actionName=="text.image" )
#
# 	def resetLoadingState(self):
# 		pass
#
# actionDelegateSelector.insert( 1, TextInsertImageAction.isSuitableFor, TextInsertImageAction )


class TextSaveAction(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(TextSaveAction, self).__init__(translate("Save"), *args, **kwargs)
		self["class"] = "icon text save"
		self["title"] = translate("Save")

	def onClick(self, event):
		self.parent().parent().saveText()

	@staticmethod
	def isSuitableFor(modul, handler, actionName):
		return (actionName == "text.save")


actionDelegateSelector.insert(1, TextSaveAction.isSuitableFor, TextSaveAction)


class TextAbortAction(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(TextAbortAction, self).__init__(translate("Abort"), *args, **kwargs)
		self["class"] = "icon text abort"
		self["title"] = translate("Abort")

	def onClick(self, event):
		if self.parent().parent().editor._getChanged():
			html5.ext.popup.YesNoDialog(
				translate("Any changes will be lost. Do you really want to abort?"),
				yesCallback=self.doAbort
			)
		else:
			self.doAbort()

	def doAbort(self, *args, **kwargs):
		self.parent().parent().abortText()

	@staticmethod
	def isSuitableFor(modul, handler, actionName):
		return (actionName == "text.abort")


actionDelegateSelector.insert(1, TextAbortAction.isSuitableFor, TextAbortAction)


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


class Editor(html5.Div):
	def __init__(self, html, *args, **kwargs):
		super(Editor, self).__init__(*args, **kwargs)

		self.initial_value = self.value = html
		self.summernote = None
		self.enabled = True

		self.summernoteContainer = self

	def _attachSummernote(self, retry=0):
		elem = self.summernoteContainer.element

		try:
			self.summernote = JS("""window.top.createSummernote(@{{elem}})""")
			elem = self.element

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
		super(Editor, self).onAttach()

		if self.summernote:
			return

		self._attachSummernote()

		if not self.enabled:
			self.summernote.summernote("disable")

	def onDetach(self):
		super(Editor, self).onDetach()
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
		super(Editor, self).enable()

		self.enabled = True
		self.removeClass("is-disabled")

		if self.summernote:
			self.summernote.summernote("enable")

	def disable(self):
		super(Editor, self).disable()

		self.enabled = False
		self.addClass("is-disabled")

		if self.summernote:
			self.summernote.summernote("disable")

	def _getChanged(self):
		return self.initial_value != self._getValue()


#
# def changed(self):
# 	return self.initial_txt != self.element.innerHTML
#
# #def onKeyDown(self, e):
# #	if e.keyCode == 13:
# #		print("br")
# #		return False
#
# def toggleSelection(self, tagName):
# 	"""
# 	This was a test...
# 	"""
#
# 	sel = eval("window.top.document.getSelection()")
# 	range = sel.getRangeAt(0)
# 	current = range.extractContents()
#
# 	try:
# 		print(current)
# 		print(current.nodeType)
# 		print(current.tagName)
# 	except:
# 		pass
#
# 	if current.nodeType == 11 and current.firstElementChild: #DocumentFragment
# 		current = current.firstElementChild
#
# 	try:
# 		print(current)
# 		print(current.nodeType)
# 		print(current.tagName)
# 	except:
# 		pass
#
# 	if current and current.nodeType == 1 and str(current.tagName).upper() == tagName.upper():
# 		print("Toggle OFF")
#
# 		if current.hasChildNodes():
# 			while current.firstChild:
# 				range.insertNode(current.firstChild)
#
# 	else:
# 		print("Toggle ON")
#
# 		new = eval("window.top.document.createElement(\"%s\")" % tagName)
# 		new.appendChild(current)
#
# 		range.insertNode(new)
#
# 	print("%s done" % tagName)
#
# def execCommand(self, commandName, valueArgument=None):
# 	"""
# 	Wraps the document.execCommand() function for easier usage.
# 	"""
#
# 	if valueArgument is None:
# 		valueArgument = "null"
# 	else:
# 		valueArgument = "\"%s\"" % str(valueArgument)
#
# 	print("execCommand(\"%s\", false, %s)" % (commandName, valueArgument))
# 	return bool(eval("window.top.document.execCommand(\"%s\", false, %s)" % (commandName, valueArgument)))


class Wysiwyg(html5.Div):
	def __init__(self, editHtml, actionBarHint=translate("Text Editor"), *args, **kwargs):
		super(Wysiwyg, self).__init__(*args, **kwargs)
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self.saveTextEvent = EventDispatcher("saveText")
		self.abortTextEvent = EventDispatcher("abortText")

		self.actionbar = ActionBar(currentAction=actionBarHint)
		self.actionbar.setActions([
			"text.abort",
			"text.save"
		])
		self.appendChild(self.actionbar)

		# self["type"] = "text"
		self.isWysiwygMode = True
		self.discardNextClickEvent = False
		self.editor = Editor(editHtml)

		self.appendChild(self.editor)

		self.currentImage = None
		self.cursorImage = None
		self.lastMousePos = None

		self.sinkEvent("onMouseDown", "onMouseUp", "onMouseMove", "onClick")

	def saveText(self, *args, **kwargs):
		self.saveTextEvent.fire(self, self.editor._getValue())

	def abortText(self, *args, **kwargs):
		self.abortTextEvent.fire(self)

	def onMouseDown(self, event):
		self.lastMousePos = None
		if event.target.tagName == "IMG":
			offsetLeft = event.pageX - event.target.offsetLeft
			offsetTop = event.pageY - event.target.offsetTop
			if event.target.offsetParent is not None:
				offsetLeft -= event.target.offsetParent.offsetLeft
				offsetTop -= event.target.offsetParent.offsetTop
			if offsetLeft > 0.8 * event.target.clientWidth and offsetTop > 0.8 * event.target.clientHeight:
				self.currentImage = event.target
			self.imgEditor.doOpen(event.target)
			self.discardNextClickEvent = True
			event.preventDefault()
			event.stopPropagation()
		else:
			self.currentImage = None
			super(Wysiwyg, self).onMouseDown(event)

		node = eval("window.top.getSelection().anchorNode")

		while node and node != self.editor.element:
			# FIXME.. emit cursormoved event
			node = node.parentNode

	def onMouseUp(self, event):
		self.currentImage = None
		self.lastMousePos = None
		super(Wysiwyg, self).onMouseUp(event)

	def onMouseMove(self, event):
		if event.target.tagName == "IMG":
			offsetLeft = event.pageX - event.target.offsetLeft
			offsetTop = event.pageY - event.target.offsetTop
			if event.target.offsetParent is not None:
				offsetLeft -= event.target.offsetParent.offsetLeft
				offsetTop -= event.target.offsetParent.offsetTop
			if offsetLeft > 0.8 * event.target.clientWidth and offsetTop > 0.8 * event.target.clientHeight:
				self.cursorImage = event.target
				self.cursorImage.style.cursor = "se-resize"
			else:
				if self.cursorImage is not None:
					self.cursorImage.style.cursor = "default"
					self.cursorImage = None
		elif self.cursorImage is not None:
			self.cursorImage.style.cursor = "default"
			self.cursorImage = None
		if self.currentImage is not None and event.target.tagName == "IMG" and self.currentImage == event.target:
			if self.lastMousePos is None:
				self.lastMousePos = (event.x, event.y)
				return
			x, y = self.lastMousePos
			self.lastMousePos = (event.x, event.y)
			event.target.width = event.target.clientWidth - (x - event.x)
			event.target.height = event.target.clientHeight - (y - event.y)
			event.preventDefault()
			event.stopPropagation()
		else:
			self.lastMousePos = None
			self.currentImage = None
			super(Wysiwyg, self).onMouseMove(event)

	def onClick(self, event):
		if self.discardNextClickEvent:
			self.discardNextClickEvent = False
			return

		super(Wysiwyg, self).onClick(event)
		domWdg = event.target
		isEditorTarget = False

		while domWdg:
			if domWdg == self.editor.element:
				isEditorTarget = True
				break
			domWdg = domWdg.parentNode

		if not isEditorTarget:
			return

		node = eval("window.top.getSelection().anchorNode")
		nodeStack = []
		i = 10

		# Try to extract the relevant nodes from the dom
		while i > 0 and node and node != self.editor.element:
			i -= 1
			nodeStack.append(node)
			node = node.parentNode

		self.imgEditor.onCursorMoved(nodeStack)
		self.cursorMovedEvent.fire(nodeStack)
