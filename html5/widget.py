import re
from html5 import document

class ClassWrapper( list ):
	def __init__( self, targetWidget ):
		super( ClassWrapper, self ).__init__( )
		self.targetWidget = targetWidget
		clsStr = targetWidget.element.getAttribute("class")
		if clsStr:
			for c in clsStr.split(" "):
				list.append( self, c )

	def _updateElem(self):
		self.targetWidget.element.setAttribute("class", " ".join( self ) )

	def append(self, p_object):
		list.append( self, p_object )
		self._updateElem()

	def clear(self):
		list.clear( self )
		self._updateElem()

	def remove(self, value):
		list.remove( self, value )
		self._updateElem()

	def extend(self, iterable):
		list.extend( self, iterable )
		self._updateElem()

	def insert(self, index, p_object):
		list.insert( self, index, p_object )
		self._updateElem()

	def pop(self, index=None):
		list.pop( self, index )
		self._updateElem()


class DataWrapper(dict):
	def __init__(self,targetWidget):
		super(DataWrapper,self).__init__()
		self.targetWidget = targetWidget
		alldata =targetWidget.element
		for data in dir(alldata):
			if re.search("^data-",data):
				val=targetWidget.element.getAttribute( "data-"+re.search("^data-",data).string())
				dict.__setitem__(self,data,val)

	def __setitem__(self,key,value):
		dict.__setitem__(self,key,value)
		self.targetWidget.element.setAttribute(str("data-"+key),value)

	def update(self, E=None, **F):
		dict.update( self, E, **F)
		if E is not None and "keys" in dir(E):
			for key in E:
				self.targetWidget.element.setAttribute(str("data-"+key),E["data-"+key])
		elif E:
			for (key, val) in E:
				self.targetWidget.element.setAttribute(str("data-"+key),"data-"+val)
		for key in F:
			self.targetWidget.element.setAttribute(str("data-"+key),F["data-"+key])

class StyleWrapper( dict ):
	def __init__( self, targetWidget ):
		super( StyleWrapper, self ).__init__( )
		self.targetWidget = targetWidget
		style = targetWidget.element.style
		for key in dir(style):
			# Convert JS-Style-Syntax to CSS Syntax (ie borderTop -> border-top)
			realKey = ""
			for currChar in key:
				if currChar.isupper():
					realKey += "-"
				realKey += currChar.lower()
			val = style.getPropertyValue(realKey)
			if val:
				dict.__setitem__(self,realKey,val)

	def __setitem__(self, key, value):
		dict.__setitem__( self, key, value )
		self.targetWidget.element.style.setProperty( key, value )

	def update(self, E=None, **F):
		dict.update( self, E, **F)
		if E is not None and "keys" in dir(E):
			for key in E:
				self.targetWidget.element.style.setProperty( key, E[key] )
		elif E:
			for (key, val) in E:
				self.targetWidget.element.style.setProperty( key, val )
		for key in F:
			self.targetWidget.element.style.setProperty( key, F[key] )



class Widget( object ):
	_baseClass = None

	def __init__(self, *args, **kwargs ):
		if "_wrapElem" in kwargs.keys():
			self.element = kwargs["_wrapElem"]
			del kwargs["_wrapElem"]
		else:
			assert self._baseClass is not None
			self.element = document.createElement( self._baseClass )
		super( Widget, self ).__init__( *args, **kwargs )
		self._children = []
		self._catchedEvents = []
		self._disabledState = None
		self._parent = None


	def sinkEvent(self, *args):
		for eventName in args:
			if eventName in self._catchedEvents or eventName.lower in ["onattach","ondetach"]:
				continue
			assert eventName in dir( self ), "%s must provide a %s method" % (str(self),eventName)
			self._catchedEvents.append( eventName )
			setattr( self.element, eventName.lower(), getattr(self, eventName))

	def unsinkEvent(self, *args ):
		for eventName in args:
			if not eventName in self._catchedEvents:
				continue
			self._catchedEvents.remove( eventName )
			setattr( self.element, eventName.lower(), None )

	def getDisabled(self):
		return( self._disabledState is not None )

	def setDisabled(self, disable):
		if disable:
			if self._disabledState is not None:
				return
			else:
				self._disabledState = { "events": self._catchedEvents[:] }
				self.unsinkEvent( *self._catchedEvents[:] )
		else:
			if self._disabledState is None:
				return
			else:
				self.sinkEvent( *self._disabledState["events"] )
				self._disabledState = None

	def _getTargetFuncName(self, key, type):
		assert type in ["get","set"]
		return( "_%s%s" % (type,(key[0].upper()+key[1:])))

	def __getitem__(self, key):
		funcName = self._getTargetFuncName( key, "get" )
		if funcName in dir( self ):
			return( getattr( self, funcName)() )
		return( None )

	def __setitem__(self, key, value):
		funcName = self._getTargetFuncName( key, "set" )
		if funcName in dir( self ):
			return( getattr( self, funcName )( value ) )
		raise ValueError( "%s is no valid attribute for %s" % (key, (self._baseClass or str(self))) )

	def _getData(self):
		"""
		Custom data attributes are intended to store custom data private to the page or application, for which there are no more appropriate attributes or elements.
		@param name:
		@return:
		"""
		return( DataWrapper( self ) )


	def _getTranslate(self):
		"""
		Specifies whether an element’s attribute values and contents of its children are to be translated when the page is localized, or whether to leave them unchanged.
		@return: True | False
		"""
		return True if self.element.translate=="yes" else False

	def _setTranslate(self,val):
		"""
		Specifies whether an element’s attribute values and contents of its children are to be translated when the page is localized, or whether to leave them unchanged.
		@param val: True | False
		"""
		self.element.translate="yes" if val==True else "no"

	def _getTitle(self):
		"""
		Advisory information associated with the element.
		@return: String
		"""
		return self.element.title
	def _setTitle(self,val):
		"""
		Advisory information associated with the element.
		@param val: String
		"""
		self.element.title=val

	def _getTabindex(self):
		"""
		Specifies whether the element represents an element that is is focusable (that is, an element which is part of the sequence of focusable elements in the document), and the relative order of the element in the sequence of focusable elements in the document.
		@return: number
		"""
		return self.element.getAttribute("tabindex")
	def _setTabindex(self,val):
		"""
		Specifies whether the element represents an element that is is focusable (that is, an element which is part of the sequence of focusable elements in the document), and the relative order of the element in the sequence of focusable elements in the document.
		@param val:  number
		"""
		print("SETTING TABINDEX")
		self.element.setAttribute("tabindex",val)

	def _getSpellcheck(self):
		"""
		Specifies whether the element represents an element whose contents are subject to spell checking and grammar checking.
		@return: True | False
		"""
		return(True if self.element.spellcheck=="true" else False)
	def _setSpellcheck(self,val):
		"""
		Specifies whether the element represents an element whose contents are subject to spell checking and grammar checking.
		@param val: True | False
		"""
		self.element.spellcheck=str(val).lower()

	def _getLang(self):
		"""
		Specifies the primary language for the contents of the element and for any of the element’s attributes that contain text.
		@return: language tag e.g. de|en|fr|es|it|ru|
		"""
		return self.element.lang
	def _setLang(self,val):
		"""
		Specifies the primary language for the contents of the element and for any of the element’s attributes that contain text.
		@param val: language tag
		"""
		self.element.lang=val

	def _getHidden(self):
		"""
		Specifies that the element represents an element that is not yet, or is no longer, relevant.
		@return: True | False
		"""
		return( True if self.element.hasAttribute("hidden") else False )
	def _setHidden(self,val):
		"""
		Specifies that the element represents an element that is not yet, or is no longer, relevant.
		@param val: True | False
		"""
		if val==True:
			self.element.setAttribute("hidden","")
		else:
			self.element.removeAttribute("hidden")

	def _getDropzone(self):
		"""
		Specifies what types of content can be dropped on the element, and instructs the UA about which actions to take with content when it is dropped on the element.
		@return: "copy" | "move" | "link"
		"""
		return self.element.dropzone
	def _setDropzone(self,val):
		"""
		Specifies what types of content can be dropped on the element, and instructs the UA about which actions to take with content when it is dropped on the element.
		@param val: "copy" | "move" | "link"
		"""
		self.element.dropzone=val

	def _getDraggable(self):
		"""
		Specifies whether the element is draggable.
		@return: True | False | "auto"
		"""
		return(self.element.draggable if str(self.element.draggable)=="auto" else (True if str(self.element.contenteditable).lower()=="true" else False) )
	def _setDraggable(self,val):
		"""
		Specifies whether the element is draggable.
		@param val: True | False | "auto"
		"""
		self.element.draggable=str(val).lower()

	def _getDir(self):
		"""
		Specifies the element’s text directionality.
		@return: ltr | rtl | auto
		"""
		return self.element.dir
	def _setDir(self,val):
		"""
		Specifies the element’s text directionality.
		@param val: ltr | rtl | auto
		"""
		self.element.dir=val

	def _getContextmenu(self):
		"""
		The value of the id attribute on the menu with which to associate the element as a context menu.
		@return:
		"""
		return self.element.contextmenu
	def _setContextmenu(self,val):
		"""
		The value of the id attribute on the menu with which to associate the element as a context menu.
		@param val:
		"""
		self.element.contextmenu=val

	def _getContenteditable(self):
		"""
		Specifies whether the contents of the element are editable.
		@return: True | False
		"""
		return( True if str(self.element.contenteditable).lower()=="true" else False )
	def _setContenteditable(self, val):
		"""
		Specifies whether the contents of the element are editable.
		@param val: True | False
		"""
		self.element.contenteditable=str(val).lower()

	def _getAccesskey(self):
		"""
		A key label or list of key labels with which to associate the element; each key label represents a keyboard shortcut which UAs can use to activate the element or give focus to the element.
		@param self:
		@return:
		"""
		return( self.element.accesskey)
	def _setAccesskey(self,val):
		"""
		A key label or list of key labels with which to associate the element; each key label represents a keyboard shortcut which UAs can use to activate the element or give focus to the element.
		@param self:
		@param val:
		"""
		self.element.accesskey=val

	def _getId(self):
		"""
		Specifies a unique id for an element
		@param self:
		@return:
		"""
		return( self.element.id )
	def _setId( self, val ):
		"""
		Specifies a unique id for an element
		@param self:
		@param val:
		"""
		self.element.id = val

	def _getClass( self ):
		"""
		The class attribute specifies one or more classnames for an element.
		@return:
		"""
		return( ClassWrapper( self ) )
	def _setClass(self, value):
		"""
		The class attribute specifies one or more classnames for an element.
		@param self:
		@param value:
		@raise ValueError:
		"""

		if value is None:
			self.element.setAttribute("class", " " )
		elif isinstance( value, str ):
			self.element.setAttribute("class", value )
		elif isinstance( value, list ):
			self.element.setAttribute("class", " ".join(value) )
		else:
			raise ValueError("Class must be a String, a List or None")

	def _getStyle(self):
		"""
		The style attribute specifies an inline style for an element.
		@param self:
		@return:
		"""
		return( StyleWrapper( self ) )

	def onAttach(self):
		pass

	def onDetach(self):
		pass

	def appendChild(self, child):
		self._children.append( child )
		self.element.appendChild( child.element )
		child._parent = self
		child.onAttach()

	def removeChild(self, child):
		assert child in self._children, "%s is not a child of %s" % (child, self)
		child.onDetach()
		self.element.removeChild( child.element )
		self._children.remove( child )
		child._parent = None

	def onBlur(self, event):
		pass
	def onChange(self, event):
		pass
	def onContextMenu(self, event):
		pass
	def onFocus(self,event):
		pass
	def onFormChange(self,event):
		pass
	def onFormInput(self, event):
		pass
	def onInput(self, event):
		pass
	def onInvalid(self, event):
		pass
	def onReset(self, event):
		pass
	def onSelect(self, event):
		pass
	def onSubmit(self, event):
		pass
	def onKeyDown(self, event):
		pass
	def onKeyPress(self, event):
		pass
	def onKeyUp(self, event):
		pass
	def onClick(self, event):
		pass
	def onDblClick(self, event):
		pass
	def onDrag(self, event):
		pass
	def onDragEnd(self, event):
		pass
	def onDragEnter(self, event):
		pass
	def onDragLeave(self, event):
		pass
	def onDragOver(self, event):
		pass
	def onDragStart(self, event):
		pass
	def onDrop(self, event):
		pass
	def onMouseDown(self, event):
		pass
	def onMouseMove(self, event):
		pass
	def onMouseOut(self, event):
		pass
	def onMouseOver(self, event):
		pass
	def onMouseUp(self, event):
		pass
	def onMouseWheel(self, event):
		pass
	def onScroll(self, event):
		pass

	def focus(self):
		self.element.focus()

	def blur(self):
		self.element.blur()

	def parent(self):
		return( self._parent )


	def _getEventMap(self):
		res = { "onblur": "onBlur",
				"onchange":"onChange",
				"oncontextmenu":"onContextMenu",
				"onfocus":"onFocus",
				"onformchange":"onFormChange",
				"onforminput":"onFormInput",
				"oninput":"onInput",
				"oninvalid":"onInvalid",
				"onreset":"onReset",
				"onselect":"onSelect",
				"onsubmit":"onSubmit",
				"onkeydown":"onKeyDown",
				"onkeypress":"onKeyPress",
				"onkeyup":"onKeyUp",
				"onclick":"onClick",
				"ondblclick":"onDblClick",
				"ondrag":"onDrag",
				"ondragend":"onDragEnd",
				"ondragenter":"onDragEnter",
				"ondragleave":"onDragLeave",
				"ondragover":"onDragOver",
				"ondragstart":"onDragStart",
				"ondrop":"onDrop",
				"onmousedown":"onMouseDown",
				"onmousemove":"onMouseMove",
				"onmouseout":"onMouseOut",
				"onmouseover":"onMouseOver",
				"onmouseup":"onMouseUp",
				"onmousewheel":"onMouseWheel",
				"onscroll":"onScroll"
		}
		return( res )










