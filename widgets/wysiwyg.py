import html5
from widgets.actionbar import ActionBar
from event import EventDispatcher

from priorityqueue import actionDelegateSelector

class BasicTextAction( html5.ext.Button ):
	cmd = None
	def __init__(self, *args, **kwargs):
		assert self.cmd is not None
		super( BasicTextAction, self ).__init__( self.cmd, *args, **kwargs )
		self["class"] = "icon text style"
		self["class"].append( self.cmd )

	def onClick(self, sender=None):
		eval("window.top.document.execCommand(\"%s\", false, null)" % self.cmd)

	def resetLoadingState(self):
		pass

class TextStyleBold( BasicTextAction ):
	cmd = "bold"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.bold", TextStyleBold )

class TextStyleItalic( BasicTextAction ):
	cmd = "italic"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.italic", TextStyleItalic )

class TextStyleJustifyCenter( BasicTextAction ):
	cmd = "justifyCenter"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.justifyCenter", TextStyleJustifyCenter )

class TextStyleJustifyLeft( BasicTextAction ):
	cmd = "justifyLeft"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.justifyLeft", TextStyleJustifyLeft )

class TextStyleJustifyRight( BasicTextAction ):
	cmd = "justifyRight"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.justifyRight", TextStyleJustifyRight )


class TextInsertImageAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TextInsertImageAction, self ).__init__( "Insert Image", *args, **kwargs )
		self["class"] = "icon text image"

	def onClick(self, sender=None):
		eval("window.top.document.execCommand(\"insertImage\", false, \"http://www.google.de/images/srpr/logo11w.png\")" )


	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.image" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TextInsertImageAction.isSuitableFor, TextInsertImageAction )

class TextInsertTableAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TextInsertTableAction, self ).__init__( "Insert Table", *args, **kwargs )
		self["class"] = "icon text table"

	def onClick(self, sender=None):
		rows = 3
		cols = 5
		insertHeader = True
		innerHtml = "<table>"
		if insertHeader:
			innerHtml += "<thead>"
			for c in range(0,cols):
				innerHtml += "<th>&nbsp;</th>"
			innerHtml += "</thead>"
		for x in range(0,rows):
			innerHtml += "<tr>"
			for y in range(0,cols):
				innerHtml += "<td>%s - %s</td>" % (x,y)
			innerHtml += "</tr>"
		innerHtml += "</table>"
		eval("window.top.document.execCommand(\"insertHTML\", false, \"%s\")" % innerHtml )


	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.table" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TextInsertTableAction.isSuitableFor, TextInsertTableAction )

class TableInsertRowBeforeAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TableInsertRowBeforeAction, self ).__init__( "Insert Table Row before", *args, **kwargs )
		self["class"] = "icon text table newrow before"

	def onClick(self, sender=None):
		node = eval("window.top.getSelection().baseNode")
		i = 10
		while i>0 and node and node != self.parent().parent().contentDiv.element:
			i -= 1
			if not "tagName" in dir( node ):
				node = node.parentElement
				continue
			if node.tagName=="TR":
				tr = html5.document.createElement("tr")
				for c in range(0,node.children.length):
					td = html5.document.createElement("td")
					tr.appendChild( td )
				node.parentNode.insertBefore( tr, node )
				return
			node = node.parentElement

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.table.newrow.before" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TableInsertRowBeforeAction.isSuitableFor, TableInsertRowBeforeAction )

class TableInsertRowAfterAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TableInsertRowAfterAction, self ).__init__( "Insert Table Row after", *args, **kwargs )
		self["class"] = "icon text table newrow after"

	def onClick(self, sender=None):
		node = eval("window.top.getSelection().baseNode")
		i = 10
		while i>0 and node and node != self.parent().parent().contentDiv.element:
			i -= 1
			if not "tagName" in dir( node ):
				node = node.parentElement
				continue
			if node.tagName=="TR":
				tr = html5.document.createElement("tr")
				for c in range(0,node.children.length):
					td = html5.document.createElement("td")
					tr.appendChild( td )
				if node.nextSibling:
					node.parentNode.insertBefore( tr, node.nextSibling )
				else:
					node.parentNode.appendChild( tr )
				return
			node = node.parentElement

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.table.newrow.after" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TableInsertRowAfterAction.isSuitableFor, TableInsertRowAfterAction )

class TableInsertColBeforeAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TableInsertColBeforeAction, self ).__init__( "Insert Table Col before", *args, **kwargs )
		self["class"] = "icon text table newrow before"

	def onClick(self, sender=None):
		print("COL BEFORE")
		node = eval("window.top.getSelection().baseNode")
		td = None
		tr = None
		table = None
		i = 10
		#Try to extract the relevat nodes from the dom
		while i>0 and node and node != self.parent().parent().contentDiv.element:
			i -= 1
			if not "tagName" in dir( node ):
				node = node.parentElement
				continue
			if node.tagName=="TD":
				td = node
			elif node.tagName=="TR":
				tr = node
			elif node.tagName=="TABLE":
				table = node
				break
			node = node.parentElement
		if td and tr and table:
			cellIdx = 0 # Before which column shall we insert a new col?
			for x in range(0, tr.children.length):
				if td==tr.children.item(x):
					break
				cellIdx += 1
			for trChildIdx in range(0,table.children.length):
				trChild = table.children.item(trChildIdx)
				if not "tagName" in dir( trChild ):
					continue
				if trChild.tagName=="THEAD":
					#Fix the table head
					for childIdx in range(0,trChild.children.length):
						child = trChild.children.item(childIdx)
						if not "tagName" in dir( child ):
							continue
						if child.tagName=="TR":
							newTd = html5.document.createElement("th")
							child.insertBefore( newTd, child.children.item(cellIdx) )
				elif trChild.tagName=="TBODY":
					#Fix all rows in the body
					for childIdx in range(0,trChild.children.length):
						child = trChild.children.item(childIdx)
						if not "tagName" in dir( child ):
							continue
						if child.tagName=="TR":
							newTd = html5.document.createElement("td")
							child.insertBefore( newTd, child.children.item(cellIdx) )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.table.newcol.before" )

	def resetLoadingState(self):
		pass


actionDelegateSelector.insert( 1, TableInsertColBeforeAction.isSuitableFor, TableInsertColBeforeAction )

class TableInsertColAftereAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TableInsertColAftereAction, self ).__init__( "Insert Table Col after", *args, **kwargs )
		self["class"] = "icon text table newrow before"

	def onClick(self, sender=None):
		print("COL BEFORE")
		node = eval("window.top.getSelection().baseNode")
		td = None
		tr = None
		table = None
		i = 10
		#Try to extract the relevat nodes from the dom
		while i>0 and node and node != self.parent().parent().contentDiv.element:
			i -= 1
			if not "tagName" in dir( node ):
				node = node.parentElement
				continue
			if node.tagName=="TD":
				td = node
			elif node.tagName=="TR":
				tr = node
			elif node.tagName=="TABLE":
				table = node
				break
			node = node.parentElement
		if td and tr and table:
			cellIdx = 0 # Before which column shall we insert a new col?
			for x in range(0, tr.children.length):
				if td==tr.children.item(x):
					break
				cellIdx += 1
			for trChildIdx in range(0,table.children.length):
				trChild = table.children.item(trChildIdx)
				if not "tagName" in dir( trChild ):
					continue
				if trChild.tagName=="THEAD":
					#Fix the table head
					for childIdx in range(0,trChild.children.length):
						child = trChild.children.item(childIdx)
						if not "tagName" in dir( child ):
							continue
						if child.tagName=="TR":
							newTd = html5.document.createElement("th")
							if cellIdx+1<child.children.length:
								child.insertBefore( newTd, child.children.item(cellIdx+1) )
							else:
								child.appendChild( newTd )
				elif trChild.tagName=="TBODY":
					#Fix all rows in the body
					for childIdx in range(0,trChild.children.length):
						child = trChild.children.item(childIdx)
						if not "tagName" in dir( child ):
							continue
						if child.tagName=="TR":
							newTd = html5.document.createElement("td")
							if cellIdx+1<child.children.length:
								child.insertBefore( newTd, child.children.item(cellIdx+1) )
							else:
								child.appendChild( newTd )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.table.newcol.after" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TableInsertColAftereAction.isSuitableFor, TableInsertColAftereAction )


class TableRemoveRowAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TableRemoveRowAction, self ).__init__( "Remove Table Row", *args, **kwargs )
		self["class"] = "icon text table remove row"

	def onClick(self, sender=None):
		node = eval("window.top.getSelection().baseNode")
		i = 10
		while i>0 and node and node != self.parent().parent().contentDiv.element:
			i -= 1
			if not "tagName" in dir( node ):
				node = node.parentElement
				continue
			if node.tagName=="TR":
				node.parentNode.removeChild(node)
				return
			node = node.parentElement

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.table.remove.row" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TableRemoveRowAction.isSuitableFor, TableRemoveRowAction )



class TableRemoveColAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TableRemoveColAction, self ).__init__( "Remove Table Col", *args, **kwargs )
		self["class"] = "icon text table remove col"

	def onClick(self, sender=None):
		print("COL BEFORE")
		node = eval("window.top.getSelection().baseNode")
		td = None
		tr = None
		table = None
		i = 10
		#Try to extract the relevat nodes from the dom
		while i>0 and node and node != self.parent().parent().contentDiv.element:
			i -= 1
			if not "tagName" in dir( node ):
				node = node.parentElement
				continue
			if node.tagName=="TD":
				td = node
			elif node.tagName=="TR":
				tr = node
			elif node.tagName=="TABLE":
				table = node
				break
			node = node.parentElement
		if td and tr and table:
			cellIdx = 0 # Which column shall we delete?
			for x in range(0, tr.children.length):
				if td==tr.children.item(x):
					break
				cellIdx += 1
			for trChildIdx in range(0,table.children.length):
				trChild = table.children.item(trChildIdx)
				if not "tagName" in dir( trChild ):
					continue
				if trChild.tagName=="THEAD":
					#Fix the table head
					for childIdx in range(0,trChild.children.length):
						child = trChild.children.item(childIdx)
						if not "tagName" in dir( child ):
							continue
						if child.tagName=="TR":
							child.removeChild(child.children.item(cellIdx))
				elif trChild.tagName=="TBODY":
					#Fix all rows in the body
					for childIdx in range(0,trChild.children.length):
						child = trChild.children.item(childIdx)
						if not "tagName" in dir( child ):
							continue
						if child.tagName=="TR":
							child.removeChild(child.children.item(cellIdx))

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.table.remove.col" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TableRemoveColAction.isSuitableFor, TableRemoveColAction )


class Wysiwyg( html5.Div ):
	def __init__(self, editHtml, *args, **kwargs ):
		super( Wysiwyg, self ).__init__(*args, **kwargs)
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self.saveTextEvent = EventDispatcher("saveText")
		#self["type"] = "text"
		self.actionBar = ActionBar(None, None, "Text edit")
		self.appendChild( self.actionBar )
		self.contentDiv = html5.Div()
		self.contentDiv["contenteditable"] = True
		self.contentDiv.element.innerHTML = editHtml
		self.appendChild( self.contentDiv )
		self.actionBar.setActions(["style.text.bold", "style.text.italic", "style.text.justifyCenter", "style.text.justifyLeft", "style.text.justifyRight", "text.image", "text.table", "text.table.newrow.before", "text.table.newrow.after", "text.table.newcol.before", "text.table.newcol.after", "text.table.remove.row", "text.table.remove.col"])
		btn = html5.ext.Button("Apply", self.saveText)
		btn["class"].append("apply")
		self.appendChild( btn )
		self.currentImage = None
		self.cursorImage = None
		self.lastMousePos = None
		self.sinkEvent("onMouseDown", "onMouseUp", "onMouseMove")

	def saveText(self, *args, **kwargs):
		self.saveTextEvent.fire( self, self.contentDiv.element.innerHTML )

	def onMouseDown(self, event):
		self.lastMousePos = None
		if event.target.tagName=="IMG":
			offsetLeft = event.pageX-event.target.offsetLeft
			offsetTop = event.pageY-event.target.offsetTop
			if event.target.offsetParent is not None:
				offsetLeft -= event.target.offsetParent.offsetLeft
				offsetTop -= event.target.offsetParent.offsetTop
			if offsetLeft>0.8*event.target.clientWidth and offsetTop>0.8*event.target.clientHeight:
				self.currentImage = event.target
			event.preventDefault()
			event.stopPropagation()
		else:
			self.currentImage = None
			super( Wysiwyg, self ).onMouseDown(event)
		#print( eval("window.getSelection().getRangeAt()") )
		node = eval("window.top.getSelection().baseNode")

		#print( node )
		#print( dir(node))
		print("----")
		while node and node != self.contentDiv.element:
			#FIXME.. emit cursormoved event
			print( node )
			node = node.parentElement

	def onMouseUp(self, event):
		self.currentImage = None
		self.lastMousePos = None
		super( Wysiwyg, self ).onMouseUp(event)

	def onMouseMove(self, event):
		if event.target.tagName=="IMG":
			offsetLeft = event.pageX-event.target.offsetLeft
			offsetTop = event.pageY-event.target.offsetTop
			if event.target.offsetParent is not None:
				offsetLeft -= event.target.offsetParent.offsetLeft
				offsetTop -= event.target.offsetParent.offsetTop
			if offsetLeft>0.8*event.target.clientWidth and offsetTop>0.8*event.target.clientHeight:
				self.cursorImage = event.target
				self.cursorImage.style.cursor = "se-resize"
			else:
				if self.cursorImage is not None:
					self.cursorImage.style.cursor = "default"
					self.cursorImage = None
		elif self.cursorImage is not None:
			self.cursorImage.style.cursor = "default"
			self.cursorImage = None
		if self.currentImage is not None and event.target.tagName=="IMG" and self.currentImage==event.target:
			if self.lastMousePos is None:
				self.lastMousePos = (event.x, event.y)
				return
			x,y = self.lastMousePos
			self.lastMousePos = (event.x, event.y)
			event.target.width = event.target.clientWidth-(x-event.x)
			event.preventDefault()
			event.stopPropagation()
		else:
			self.lastMousePos = None
			self.currentImage = None
			super( Wysiwyg, self ).onMouseMove(event)





