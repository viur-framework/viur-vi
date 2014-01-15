import html5
from widgets.actionbar import ActionBar
from event import EventDispatcher
from utils import doesEventHitWidgetOrChildren
from time import time
from priorityqueue import actionDelegateSelector
import re
from config import conf
from widgets.file import FileWidget

class BasicTextAction( html5.ext.Button ):
	cmd = None
	isActiveTag = None
	def __init__(self, *args, **kwargs):
		assert self.cmd is not None
		super( BasicTextAction, self ).__init__( self.cmd, *args, **kwargs )
		self["class"] = "icon text style"
		self["class"].append( self.cmd )

	def onAttach(self):
		super(BasicTextAction, self).onAttach( )
		if self.isActiveTag:
			self.parent().parent().cursorMovedEvent.register( self )

	def onDetach(self):
		super(BasicTextAction, self).onDetach( )
		if self.isActiveTag:
			self.parent().parent().cursorMovedEvent.unregister( self )

	def onCursorMoved(self, nodeStack):
		if self.isActiveTag in [(x.tagName if "tagName" in dir(x) else "") for x in nodeStack]:
			if not "isactive" in self["class"]:
				self["class"].append("isactive")
		else:
			if "isactive" in self["class"]:
				self["class"].remove("isactive")

	def onClick(self, sender=None):
		eval("window.top.document.execCommand(\"%s\", false, null)" % self.cmd)

	def resetLoadingState(self):
		pass


class TextStyleBold( BasicTextAction ):
	cmd = "bold"
	isActiveTag = "B"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.bold", TextStyleBold )

class TextStyleItalic( BasicTextAction ):
	cmd = "italic"
	isActiveTag = "I"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.italic", TextStyleItalic )

class TextStyleUnderline( BasicTextAction ):
	cmd = "underline"
	isActiveTag = "U"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.underline", TextStyleUnderline )

class TextStyleStrikeThrough( BasicTextAction ):
	cmd = "strikeThrough"
	isActiveTag = "STRIKE"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.strikeThrough", TextStyleStrikeThrough )



class BasicFormatBlockAction( BasicTextAction ):
	def onClick(self, sender=None):
		eval("window.top.document.execCommand(\"formatBlock\", false, \"%s\")" % self.cmd)


class TextStyleH1( BasicFormatBlockAction ):
	cmd = "H1"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.h1", TextStyleH1 )

class TextStyleH2( BasicFormatBlockAction ):
	cmd = "H2"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.h2", TextStyleH2 )

class TextStyleH3( BasicFormatBlockAction ):
	cmd = "H3"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.h3", TextStyleH3 )

class TextStyleH4( BasicFormatBlockAction ):
	cmd = "H4"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.h4", TextStyleH4 )

class TextStyleH5( BasicFormatBlockAction ):
	cmd = "H5"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.h5", TextStyleH5 )

class TextStyleH6( BasicFormatBlockAction ):
	cmd = "H6"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.h6", TextStyleH6 )


class TextStyleBlockQuote( BasicFormatBlockAction ):
	cmd = "BLOCKQUOTE"

#actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.blockquote", TextStyleBlockQuote )


class TextStyleJustifyCenter( BasicTextAction ):
	cmd = "justifyCenter"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.justifyCenter", TextStyleJustifyCenter )

class TextStyleJustifyLeft( BasicTextAction ):
	cmd = "justifyLeft"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.justifyLeft", TextStyleJustifyLeft )

class TextStyleJustifyRight( BasicTextAction ):
	cmd = "justifyRight"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="style.text.justifyRight", TextStyleJustifyRight )



class TextInsertOrderedList( BasicTextAction ):
	cmd = "insertOrderedList"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.orderedList", TextInsertOrderedList )

class TextInsertUnorderedList( BasicTextAction ):
	cmd = "insertUnorderedList"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.unorderedList", TextInsertUnorderedList )




class TextIndent( BasicTextAction ):
	cmd = "indent"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.indent", TextIndent )


class TextOutdent( BasicTextAction ):
	cmd = "outdent"
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.outdent", TextOutdent )



class TextRemoveFormat( BasicTextAction ):
	cmd = "removeformat"

	def onClick(self, sender=None):
		eval("window.top.document.execCommand(\"%s\", false, null)" % self.cmd)
		node = eval("window.top.getSelection().baseNode")
		i = 10
		while i>0 and node and node != self.parent().parent().contentDiv.element:
			i -= 1
			if not "tagName" in dir( node ):
				node = node.parentElement
				continue
			if node.tagName in ["H%s" % x for x in range(0,6)]:
				eval("window.top.document.execCommand(\"formatBlock\", false, 'div')")
				return
			node = node.parentElement

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.removeformat", TextRemoveFormat )





class TextInsertImageAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TextInsertImageAction, self ).__init__( "Insert Image", *args, **kwargs )
		self["class"] = "icon text image"

	def onClick(self, sender=None):
		currentSelector = FileWidget( "file", isSelector=True )
		currentSelector.selectionActivatedEvent.register( self )
		conf["mainWindow"].stackWidget( currentSelector )
		#


	def onSelectionActivated(self, selectWdg, selection):
		if not selection:
			return
		for item in selection:
			dataUrl = "/file/download/%s/%s" % (item.data["dlkey"], item.data["name"].replace("\"",""))
			if "mimetype" in item.data.keys() and item.data["mimetype"].startswith("image/"):
				eval("window.top.document.execCommand(\"insertImage\", false, \""+dataUrl+"\")" )
			else:
				eval("window.top.document.execCommand(\"createLink\", false, \""+dataUrl+"?download=1\")" )

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.image" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TextInsertImageAction.isSuitableFor, TextInsertImageAction )

class TextInsertLinkAction( html5.ext.Button ):
	newLinkIdx = 0
	def __init__(self, *args, **kwargs):
		super( TextInsertLinkAction, self ).__init__( "Insert Link", *args, **kwargs )
		self["class"] = "icon text link"

	def onClick(self, sender=None):
		newLinkTarget = "#linkidx-%s-%s" % (TextInsertLinkAction.newLinkIdx, time() )
		eval("window.top.document.execCommand(\"createLink\", false, \"#"+newLinkTarget+"\")" )
		self.parent().parent().linkEditor.openLink(newLinkTarget)

	def createLink(self, dialog, value):
		if value:
			self.parent().parent().contentDiv.focus()
			#eval("window.top.document.execCommand(\"createLink\", false, \""+value.replace("\"","")+"\")" )



	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.link" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, TextInsertLinkAction.isSuitableFor, TextInsertLinkAction )


class CreateTablePopup( html5.ext.Popup ):
	def __init__(self, targetNode, *args, **kwargs ):
		super( CreateTablePopup, self ).__init__( *args, **kwargs )
		while not "innerHTML" in dir(targetNode):
			targetNode = targetNode.parentElement
		self.targetNode = targetNode
		self["class"].append("createtable")
		self.rowInput = html5.Input()
		self.rowInput["type"] = "number"
		self.rowInput["value"] = 3
		self.appendChild( self.rowInput )
		l = html5.Label("Rows", forElem=self.rowInput)
		l["class"].append("rowlbl")
		self.appendChild( l )
		self.colInput = html5.Input()
		self.colInput["type"] = "number"
		self.colInput["value"] = 4
		self.appendChild( self.colInput )
		l = html5.Label("Cols", forElem=self.colInput)
		l["class"].append("collbl")
		self.appendChild( l )
		self.insertHeader = html5.Input()
		self.insertHeader["type"] = "checkbox"
		self.appendChild( self.insertHeader )
		l = html5.Label("Insert Table Header", forElem=self.insertHeader)
		l["class"].append("headerlbl")
		self.appendChild( l )
		self.appendChild( html5.ext.Button( "Cancel", callback=self.doClose ) )
		self.appendChild( html5.ext.Button( "Create", callback=self.createTable ) )

	def doClose(self, *args, **kwargs):
		self.targetNode = None
		self.close()

	def createTable(self, *args, **kwargs):
		rows = int(self.rowInput["value"])
		cols = int(self.colInput["value"])
		insertHeader = self.insertHeader["checked"]
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
		self.targetNode.innerHTML = self.targetNode.innerHTML+innerHtml
		#eval("window.top.document.execCommand(\"insertHTML\", false, \"%s\")" % innerHtml )
		self.doClose()

class TextInsertTableAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TextInsertTableAction, self ).__init__( "Insert Table", *args, **kwargs )
		self["class"] = "icon text table"

	def onClick(self, sender=None):
		self.parent().parent().contentDiv.focus()
		node = eval("window.top.getSelection().baseNode")
		CreateTablePopup( node )
		return

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
		self["class"] = "icon text table newcol before"

	def onClick(self, sender=None):
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

class TableInsertColAfterAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TableInsertColAfterAction, self ).__init__( "Insert Table Col after", *args, **kwargs )
		self["class"] = "icon text table newcol after"

	def onClick(self, sender=None):
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

actionDelegateSelector.insert( 1, TableInsertColAfterAction.isSuitableFor, TableInsertColAfterAction )


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

class TextSaveAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( TextSaveAction, self ).__init__( "Save", *args, **kwargs )
		self["class"] = "icon text save"

	def onClick(self, event):
		self.parent().parent().saveText()

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="text.save" )

actionDelegateSelector.insert( 1, TextSaveAction.isSuitableFor, TextSaveAction )

class LinkEditor( html5.Div ):
	newLinkIdx = 0
	def __init__(self, *args, **kwargs):
		super( LinkEditor, self ).__init__( *args, **kwargs )
		self["class"].append("linkeditor")
		self["style"]["display"] = "none"
		self.linkTxt = html5.Input()
		self.linkTxt["type"] = "text"
		self.appendChild(self.linkTxt)
		l = html5.Label("URL", forElem=self.linkTxt)
		l["class"].append("urllbl")
		self.appendChild( l )
		self.newTab = html5.Input()
		self.newTab["type"] = "checkbox"
		self.appendChild(self.newTab)
		l = html5.Label("New window", forElem=self.newTab)
		l["class"].append("newwindowlbl")
		self.appendChild( l )
		self.currentElem = None

	def getAFromTagStack(self, tagStack):
		for elem in tagStack:
			if not "tagName" in dir(elem):
				continue
			if elem.tagName=="A":
				return( elem )
		return( None )

	def onCursorMoved(self, tagStack):
		newElem = self.getAFromTagStack(tagStack)
		if newElem is not None and self.currentElem is not None:
			self.doClose()
			self.doOpen( newElem )
		elif self.currentElem is None and newElem is not None:
			self.doOpen( newElem )
		elif self.currentElem is not None and newElem is None:
			self.doClose()

	def doOpen(self, elem):
		self.currentElem = elem
		self.linkTxt["value"] = self.currentElem.href
		self.newTab["checked"] = self.currentElem.target=="_blank"

		self.isOpen = True
		self["style"]["display"] = "block"

	def doClose(self):
		if self.currentElem is None:
			return
		self.currentElem.href = self.linkTxt["value"]
		self.currentElem.target = "_blank" if self.newTab["checked"] else None
		self["style"]["display"] = "none"
		self.currentElem = None

	def findHref(self, linkTarget, elem):
		if "tagName" in dir(elem):
			if elem.tagName == "A":
				if elem.href == linkTarget or elem.href.endswith(linkTarget):
					return( elem )
		if "children" in dir(elem):
			for x in range(0,elem.children.length):
				child = elem.children.item(x)
				r = self.findHref( linkTarget, child)
				if r is not None:
					return( r )
		return( None )

	def openLink(self, linkTarget):
		self.doOpen( self.findHref( linkTarget, self.parent().contentDiv.element ) )
		self.linkTxt["value"] = ""
		self.linkTxt.focus()


class ImageEditor( html5.Div ):
	def __init__(self, *args, **kwargs):
		super( ImageEditor, self ).__init__( *args, **kwargs )
		self["class"].append("imageeditor")
		self["style"]["display"] = "none"
		self.widthInput = html5.Input()
		self.widthInput["type"] = "number"
		self.appendChild(self.widthInput)
		l = html5.Label("Width", self.widthInput)
		l["class"].append("widthlbl")
		self.appendChild( l )
		self.keepAspectRatio = html5.Input()
		self.keepAspectRatio["type"] = "checkbox"
		self.appendChild( self.keepAspectRatio )
		l = html5.Label("Keep aspect ratio", self.keepAspectRatio)
		l["class"].append("aspectlbl")
		self.appendChild( l )
		self.heightInput = html5.Input()
		self.heightInput["type"] = "number"
		self.appendChild(self.heightInput)
		l = html5.Label("Height", self.heightInput)
		l["class"].append("heightlbl")
		self.appendChild( l )
		self.titleInput = html5.Input()
		self.titleInput["type"] = "text"
		self.appendChild(self.titleInput)
		l = html5.Label("Title", self.titleInput)
		l["class"].append("titlelbl")
		self.appendChild( l )
		self.currentElem = None
		self.sinkEvent("onChange")

	def onChange(self, event):
		super(ImageEditor,self).onChange( event )
		aspect = self.currentElem.naturalWidth/self.currentElem.naturalHeight
		if event.target == self.widthInput.element:
			if self.keepAspectRatio["checked"]:
				self.heightInput["value"] = int(float(self.widthInput["value"])/aspect)
		elif event.target == self.heightInput.element:
			if self.keepAspectRatio["checked"]:
				self.widthInput["value"] = int(float(self.heightInput["value"])*aspect)
		self.currentElem.width = int(self.widthInput["value"])
		self.currentElem.height = int(self.heightInput["value"])

	def getImgFromTagStack(self, tagStack):
		for elem in tagStack:
			if not "tagName" in dir(elem):
				continue
			if elem.tagName=="IMG":
				return( elem )
		return( None )

	def onCursorMoved(self, tagStack):
		newElem = self.getImgFromTagStack(tagStack)
		if newElem is not None and self.currentElem is not None:
			self.doClose()
			self.doOpen( newElem )
		elif self.currentElem is None and newElem is not None:
			self.doOpen( newElem )
		elif self.currentElem is not None and newElem is None:
			self.doClose()

	def doOpen(self, elem):
		self.currentElem = elem
		self["style"]["display"] = ""
		self.heightInput["value"] = elem.height
		self.widthInput["value"] = elem.width
		self.titleInput["value"] = elem.title

	def doClose(self):
		if self.currentElem is None:
			return
		self.currentElem.width = int( self.widthInput["value"] )
		self.currentElem.height = int( self.heightInput["value"] )
		self.currentElem.title = self.titleInput["value"]
		self["style"]["display"] = "none"
		self.currentElem = None

	def findImg(self, linkTarget, elem):
		if "tagName" in dir(elem):
			if elem.tagName == "IMG":
				if elem.href == linkTarget or elem.href.endswith(linkTarget):
					return( elem )
		if "children" in dir(elem):
			for x in range(0,elem.children.length):
				child = elem.children.item(x)
				r = self.findImg( linkTarget, child)
				if r is not None:
					return( r )
		return( None )

	def openLink(self, linkTarget):
		self.doOpen( self.findHref( linkTarget, self.parent().contentDiv.element ) )
		self.linkTxt["value"] = ""
		self.linkTxt.focus()


class TextUndoAction( BasicTextAction ):
	cmd = "undo"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.undo", TextUndoAction )

class TextRedoAction( BasicTextAction ):
	cmd = "redo"

actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.redo", TextRedoAction )




class FlipViewAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( FlipViewAction, self ).__init__( "Flip View", *args, **kwargs )
		self["class"] = "icon flipview"

	def onAttach(self):
		super( FlipViewAction, self ).onAttach()
		if self.parent().parent().isWysiwygMode:
			self["class"].append("is_wysiwyg")
		else:
			self["class"].append("is_htmlview")

	def onClick(self, sender=None):
		self.parent().parent().flipView()
		if "is_wysiwyg" in self["class"]:
			self["class"].remove("is_wysiwyg")
		if "is_htmlview" in self["class"]:
			self["class"].remove("is_htmlview")
		if self.parent().parent().isWysiwygMode:
			self["class"].append("is_wysiwyg")
		else:
			self["class"].append("is_htmlview")

	def resetLoadingState(self):
		pass
actionDelegateSelector.insert( 1, lambda modul, handler, actionName: actionName=="text.flipView", FlipViewAction )

class Wysiwyg( html5.Div ):
	def __init__(self, editHtml, actionBarHint="Text Editor", *args, **kwargs ):
		super( Wysiwyg, self ).__init__(*args, **kwargs)
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self.saveTextEvent = EventDispatcher("saveText")
		self.textActions = ["style.text.bold", "style.text.italic", "style.text.underline", "style.text.strikeThrough"]+["style.text.h%s" % x for x in range(0,4)]+[ "text.removeformat", "style.text.justifyCenter", "style.text.justifyLeft", "style.text.justifyRight", "style.text.blockquote", "text.orderedList", "text.unorderedList", "text.indent", "text.outdent", "text.image", "text.link", "text.table", "text.flipView", "text.undo", "text.redo","text.save"]
		#self["type"] = "text"
		self.actionbar = ActionBar(None, None, actionBarHint)
		self.isWysiwygMode = True
		self.discardNextClickEvent = False
		self.appendChild( self.actionbar )
		self.tableDiv = html5.Div()
		self.tableDiv["class"].append("tableeditor")
		self.appendChild(self.tableDiv)
		for c in [TableInsertRowBeforeAction,TableInsertRowAfterAction,TableInsertColBeforeAction,TableInsertColAfterAction,TableRemoveRowAction,TableRemoveColAction]:
			self.tableDiv.appendChild( c() )
		self.tableDiv["style"]["display"]="none"
		self.linkEditor = LinkEditor()
		self.appendChild(self.linkEditor)
		self.imgEditor = ImageEditor()
		self.appendChild(self.imgEditor)
		self.contentDiv = html5.Div()
		self.contentDiv["contenteditable"] = True
		self.contentDiv.element.innerHTML = editHtml
		self.contentDiv["class"].append("contentdiv")
		self.appendChild( self.contentDiv )
		self.actionbar.setActions( self.textActions )
		#btn = html5.ext.Button("Apply", self.saveText)
		#btn["class"].append("icon apply")
		#self.appendChild( btn )
		self.currentImage = None
		self.cursorImage = None
		self.lastMousePos = None
		self.sinkEvent("onMouseDown", "onMouseUp", "onMouseMove", "onClick")

	def flipView(self, *args, **kwargs ):
		htmlStr = self.contentDiv.element.innerHTML
		if self.isWysiwygMode:
			self.imgEditor.doClose()
			self.linkEditor.doClose()
			self.tableDiv["style"]["display"] = None
			outStr = ""
			indent = 0
			indestStr = "&nbsp;&nbsp;&nbsp;"
			inStr = htmlStr.replace("&", "&amp;" ).replace("<", "&lt;" ).replace(">","&gt;")
			while inStr:
				if inStr.startswith("&lt;div&gt;"):
					outStr += "<br>"
					outStr += indestStr*indent
					indent +=1
				elif inStr.startswith("&lt;/div&gt;"):
					indent -=1
					outStr += "<br>"
					outStr += indestStr*indent
				elif inStr.startswith("&lt;br"):
					outStr += "<br>"
					outStr += indestStr*indent
				elif inStr.startswith("&lt;table"):
					outStr += "<br>"
					outStr += indestStr*indent
					indent +=1
				elif inStr.startswith("&lt;/table"):
					indent -=1
					outStr += "<br>"
					outStr += indestStr*indent
				elif inStr.startswith("&lt;tr"):
					outStr += "<br>"
					outStr += indestStr*indent
					indent +=1
				elif inStr.startswith("&lt;/tr"):
					indent -=1
					outStr += "<br>"
					outStr += indestStr*indent
				elif inStr.startswith("&lt;td"):
					outStr += "<br>"
					outStr += indestStr*indent
				elif inStr.startswith("&lt;th&gt;"):
					outStr += "<br>"
					outStr += indestStr*indent
				elif inStr.startswith("&lt;thead&gt;"):
					outStr += "<br>"
					outStr += indestStr*indent
					indent +=1
				elif inStr.startswith("&lt;/thead&gt;"):
					indent -=1
					outStr += "<br>"
					outStr += indestStr*indent
				elif inStr.startswith("&lt;tbody&gt;"):
					outStr += "<br>"
					outStr += indestStr*indent
					indent +=1
				elif inStr.startswith("&lt;/tbody&gt;"):
					indent -=1
					outStr += "<br>"
					outStr += indestStr*indent
				outStr += inStr[0]
				inStr = inStr[ 1: ]
			self.contentDiv.element.innerHTML = outStr
			self.isWysiwygMode = not self.isWysiwygMode
			self.actionbar.setActions( ["text.flipView"] )
		else:
			htmlStr = re.sub(r'<[^>]*?>', '', htmlStr)
			htmlStr = htmlStr.replace("&nbsp;","").replace("&nbsp;","")
			self.contentDiv.element.innerHTML = htmlStr.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
			self.isWysiwygMode = not self.isWysiwygMode
			self.actionbar.setActions( self.textActions )


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
			self.imgEditor.doOpen( event.target )
			self.discardNextClickEvent = True
			event.preventDefault()
			event.stopPropagation()
		else:
			self.currentImage = None
			super( Wysiwyg, self ).onMouseDown(event)
		node = eval("window.top.getSelection().baseNode")
		while node and node != self.contentDiv.element:
			#FIXME.. emit cursormoved event
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


	def onClick(self, event):
		if self.discardNextClickEvent:
			self.discardNextClickEvent = False
			return
		super(Wysiwyg, self).onClick( event )
		domWdg = event.target
		isContentDivTarget = False
		while domWdg:
			if domWdg==self.contentDiv.element:
				isContentDivTarget = True
				break
			domWdg = domWdg.parentElement
		if not isContentDivTarget:
			return
		node = eval("window.top.getSelection().baseNode")
		nodeStack = []
		i = 10
		#Try to extract the relevat nodes from the dom
		while i>0 and node and node != self.contentDiv.element:
			i -= 1
			nodeStack.append(node)
			node = node.parentElement
		if "TABLE" in [(x.tagName if "tagName" in dir(x) else "") for x in nodeStack]:
			self.tableDiv["style"]["display"] = ""
		else:
			self.tableDiv["style"]["display"] = "none"
		self.linkEditor.onCursorMoved(nodeStack)
		self.imgEditor.onCursorMoved(nodeStack)
		self.cursorMovedEvent.fire( nodeStack )


